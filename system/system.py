import asyncio
import logging
from enum import Enum, auto

from core.commands.account import UpdateAccountSize
from core.commands.backtest import BacktestRun
from core.commands.broker import Subscribe, UpdateSettings
from core.commands.portfolio import PortfolioReset
from core.interfaces.abstract_actor import AbstractActor
from core.interfaces.abstract_datasource import AbstractDataSource
from core.interfaces.abstract_system import AbstractSystem
from core.models.broker import BrokerType, MarginMode, PositionMode
from core.models.datasource import DataSourceType
from core.models.exchange import ExchangeType
from core.models.lookback import Lookback
from core.models.optimizer import Optimizer
from core.models.order import OrderType
from core.models.symbol import Symbol
from core.models.timeframe import Timeframe
from core.models.strategy import Strategy, StrategyType
from core.queries.broker import GetAccountBalance, GetSymbols
from core.queries.portfolio import GetTopStrategy
from infrastructure.estimator import Estimator

from .context import SystemContext
from .squad import Squad


logger = logging.getLogger(__name__)


class SystemState(Enum):
    INIT = auto()
    GENERATE = auto()
    BACKTEST = auto()
    OPTIMIZATION = auto()
    TRADING = auto()
    STOPPED = auto()


class Event(Enum):
    GENERATE_COMPLETE = auto()
    RUN_BACKTEST = auto()
    REGENERATE = auto()
    BACKTEST_COMPLETE = auto()
    OPTIMIZATION_COMPLETE = auto()
    TRADING_STOPPED = auto()
    SYSTEM_STOP = auto()


class System(AbstractSystem):
    def __init__(self, context: SystemContext):
        super().__init__()
        self.context = context
        self.state = SystemState.INIT

        self.event_queue = asyncio.Queue()
        self.active_strategy: list[tuple[Symbol, Timeframe, Strategy]] = []
        self.strategy: tuple[Symbol, Timeframe, Strategy] = []
        self.optimizer = None

    async def start(self):
        async with self.context.broker_factory.create(
            BrokerType.FUTURES, self.context.exchange_factory.create(ExchangeType.BYBIT)
        ):
            await self.event_queue.put(Event.REGENERATE)

            while True:
                event = await self.event_queue.get()

                match self.state:
                    case SystemState.INIT:
                        if event == Event.REGENERATE:
                            self.state = SystemState.GENERATE
                            await self._generate()
                        if event == Event.SYSTEM_STOP:
                            return
                    case SystemState.GENERATE:
                        if event == Event.GENERATE_COMPLETE:
                            self.state = SystemState.BACKTEST
                            await self._run_backtest()
                        if event == Event.SYSTEM_STOP:
                            return
                    case SystemState.BACKTEST:
                        if event == Event.BACKTEST_COMPLETE:
                            self.state = SystemState.OPTIMIZATION
                            await self._run_optimization()
                        if event == Event.SYSTEM_STOP:
                            return
                    case SystemState.OPTIMIZATION:
                        if event == Event.OPTIMIZATION_COMPLETE:
                            self.state = SystemState.TRADING
                            await self._run_trading()
                        if event == Event.REGENERATE:
                            self.state = SystemState.GENERATE
                            await self._generate()
                        if event == Event.RUN_BACKTEST:
                            self.state = SystemState.BACKTEST
                            await self._run_backtest()
                        if event == Event.SYSTEM_STOP:
                            return

    def stop(self):
        self.event_queue.put_nowait(Event.SYSTEM_STOP)

    async def _generate(self):
        logger.info("Generate a new population")

        futures_symbols = await self.query(GetSymbols())

        self.optimizer = self.context.strategy_optimizer_factory.create(
            Optimizer.GENETIC,
            self.context.strategy_generator_factory.create(
                StrategyType.TREND, futures_symbols
            ),
        )

        self.optimizer.init()

        await self.event_queue.put(Event.GENERATE_COMPLETE)

    async def _run_backtest(self):
        population = self.optimizer.population
        total_steps = len(population)

        logger.info(f"Run backtest for: {total_steps}")

        estimator = Estimator(total_steps)
        datasource = self.context.datasource_factory.create(
            DataSourceType.EXCHANGE,
            self.context.exchange_factory.create(ExchangeType.BYBIT),
        )

        async for batch_actors in self._generate_batch_actors(population, False):
            tasks = [
                self._process_backtest(datasource, actors) for actors in batch_actors
            ]
            await asyncio.gather(*tasks)
            logger.info(f"Remaining time: {estimator.remaining_time():.2f}sec")

        await self.event_queue.put(Event.BACKTEST_COMPLETE)

    async def _generate_batch_actors(self, data, is_trading):
        actors_batch = []

        for symbol, timeframe, strategy in data:
            squad = self.context.squad_factory.create_squad(
                symbol, timeframe, strategy, is_trading
            )
            order_executor = self.context.executor_factory.create_actor(
                OrderType.PAPER, symbol, timeframe, strategy
            )

            actors_batch.append((squad, order_executor))

            if len(actors_batch) == self.context.parallel_num:
                yield actors_batch
                actors_batch = []

        if actors_batch:
            yield actors_batch

    async def _refresh_account(self):
        account_size = await self.query(GetAccountBalance())
        await self.execute(UpdateAccountSize(account_size))

    async def _process_backtest(
        self, datasource: AbstractDataSource, actors: tuple[Squad, AbstractActor]
    ):
        squad, order_executor = actors

        await asyncio.gather(
            *[squad.start(), self._refresh_account(), order_executor.start()]
        )

        await self.execute(
            BacktestRun(
                datasource,
                squad.symbol,
                squad.timeframe,
                squad.strategy,
                self.context.lookback,
            )
        )
        await asyncio.gather(*[squad.stop(), order_executor.stop()])

    async def _process_pretrading(
        self, datasource: AbstractDataSource, actors: tuple[Squad, AbstractActor]
    ):
        squad, order_executor = actors

        await asyncio.gather(
            *[squad.start(), self._refresh_account(), order_executor.start()]
        )

        await self.execute(
            BacktestRun(
                datasource,
                squad.symbol,
                squad.timeframe,
                squad.strategy,
                Lookback.ONE_MONTH,
            )
        )

        await asyncio.gather(*[self.execute(PortfolioReset()), order_executor.stop()])

    async def _run_optimization(self):
        logger.info("Run optimization")

        strategies = await self.query(
            GetTopStrategy(num=self.context.active_strategy_num)
        )

        if not len(strategies):
            logger.info("Regenerate population")
            await self.event_queue.put(Event.REGENERATE)
            return

        if self.optimizer.done:
            logger.info("Optimization complete")
            await self.event_queue.put(Event.OPTIMIZATION_COMPLETE)
            return

        await self.optimizer.optimize()

        await self.event_queue.put(Event.RUN_BACKTEST)

    async def _run_trading(self):
        logger.info("Run trading")

        strategies = await self.query(
            GetTopStrategy(num=self.context.active_strategy_num)
        )

        logger.info(
            [
                f"{str(strategy[0])}_{str(strategy[1])}{str(strategy[2])}"
                for strategy in strategies
            ]
        )

        datasource = self.context.datasource_factory.create(
            DataSourceType.EXCHANGE,
            self.context.exchange_factory.create(ExchangeType.BYBIT),
        )

        trading_actors = []

        async for batch_actors in self._generate_batch_actors(strategies, True):
            for actors in batch_actors:
                await self._process_pretrading(datasource, actors)
                trading_actors.append(actors)

        for squad, _ in trading_actors:
            order_executor = self.context.executor_factory.create_actor(
                OrderType.MARKET if self.context.is_live else OrderType.PAPER,
                squad.symbol,
                squad.timeframe,
                squad.strategy,
            )
            await asyncio.gather(
                *[
                    self.execute(
                        UpdateSettings(
                            squad.symbol,
                            self.context.leverage,
                            PositionMode.ONE_WAY,
                            MarginMode.ISOLATED,
                        )
                    ),
                    order_executor.start(),
                ]
            )

        await self._refresh_account()
        await self.execute(
            Subscribe([(strategy[0], strategy[1]) for strategy in strategies])
        )