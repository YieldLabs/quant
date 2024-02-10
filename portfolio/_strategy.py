import asyncio
from typing import Dict, Tuple

import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

from core.models.strategy import Strategy
from core.models.symbol import Symbol
from core.models.timeframe import Timeframe


class StrategyStorage:
    def __init__(self, n_clusters=3):
        self.kmeans = KMeans(n_clusters=n_clusters, n_init="auto")
        self.scaler = MinMaxScaler()
        self.data: Dict[Tuple[Symbol, Timeframe, Strategy], Tuple[np.array, int]] = {}
        self.lock = asyncio.Lock()

    async def next(
        self,
        symbol: Symbol,
        timeframe: Timeframe,
        strategy: Strategy,
        metrics: np.array,
    ):
        async with self.lock:
            key = (symbol, timeframe, strategy)
            self.data[key] = (metrics, -1)

            if len(self.data.keys()) >= self.kmeans.n_clusters:
                self._update_clusters()

    async def reset(self, symbol: Symbol, timeframe: Timeframe, strategy: Strategy):
        async with self.lock:
            self.data.pop((symbol, timeframe, strategy), None)

    async def reset_all(self):
        async with self.lock:
            self.data = {}

    async def get_top(self, num: int = 10, positive_pnl: bool = True):
        async with self.lock:
            sorted_strategies = sorted(
                self.data.keys(), key=self._sorting_key, reverse=True
            )

            selected_symbols = set()
            top_strategies = [
                key
                for key in sorted_strategies
                if (symbol := key[0]) not in selected_symbols
                and (
                    not selected_symbols.add(symbol) and (self.data[key][0][-1] > 0)
                    if positive_pnl
                    else True
                )
            ]

            return top_strategies[:num]

    def _update_clusters(self):
        data_matrix = np.array([item[0] for item in self.data.values()])
        normalized_data = self.scaler.fit_transform(data_matrix)
        cluster_indices = self.kmeans.fit_predict(normalized_data)

        for (symbol, timeframe, strategy), idx in zip(
            self.data.keys(), cluster_indices
        ):
            self.data[(symbol, timeframe, strategy)] = (
                self.data[(symbol, timeframe, strategy)][0],
                idx,
            )

    def _sorting_key(self, key):
        return self.data[key][1], self.data[key][0][0]
