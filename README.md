# Backtesting Engine

## Overview

This project is a Python-based backtesting engine for testing trading strategies using historical financial data. The `Engine` class handles data ingestion, execution of strategies, portfolio management, and performance metrics calculation. Users can define their trading strategies by extending the `Strategy` class.

## Features

- **Data Ingestion**: Supports OHLC data for backtesting.
- **Custom Strategies**: Users can implement their own trading strategies by inheriting from the `Strategy` base class.
- **Order Management**: Supports market and limit orders for buying and selling.
- **Performance Metrics**: Calculates key metrics such as:
  - Total Return
  - Annualized Returns
  - Annualized Volatility
  - Sharpe Ratio
  - Maximum Drawdown
  - Asset Exposure
- **Buy & Hold Benchmark**: Compares strategy performance against a simple buy-and-hold benchmark.
- **Visualization**: Plots the portfolio value over time against the buy-and-hold benchmark.

---

