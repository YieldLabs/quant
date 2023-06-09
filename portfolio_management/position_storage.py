import asyncio
from typing import Dict, List, Optional

from core.position import Order, Position


class PositionStorage:
    def __init__(self):
        self.active_positions: Dict[str, Position] = {}
        self.active_positions_lock = asyncio.Lock()
        self.closed_positions: Dict[str, Position] = {}
        self.closed_positions_lock = asyncio.Lock()

    async def add_active_position(self, symbol: str, position: Position):
        async with self.active_positions_lock:
            self.active_positions[symbol] = position

    async def remove_active_position(self, symbol: str):
        async with self.active_positions_lock:
            self.active_positions.pop(symbol, None)

    async def get_active_position(self, symbol: str) -> Optional[Position]:
        async with self.active_positions_lock:
            return self.active_positions.get(symbol)

    async def add_order(self, symbol: str, order: Order):
        async with self.active_positions_lock:
            position = self.active_positions.get(symbol)

            position.add_order(order)
            position.update_prices(order.price)

            self.active_positions[symbol] = position

    async def add_closed_position(self, position: Position, exit_price: float):
        async with self.closed_positions_lock:
            position.close_position(exit_price)

            if position.closed_key not in self.closed_positions:
                self.closed_positions[position.closed_key] = position

    async def filter_closed_positions_by_strategy(self, strategy_id: str) -> List[Position]:
        async with self.closed_positions_lock:
            return list(filter(lambda x: x.strategy_id == strategy_id, self.closed_positions.values()))
