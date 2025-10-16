"""
Performance Metrics for Market Making Strategies

Implements industry-standard metrics:
- Sharpe Ratio, Sortino Ratio
- Maximum Drawdown
- Profit Factor
- Inventory Risk Metrics
- Fill Ratio Analysis
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional
from dataclasses import dataclass


def calculate_sharpe_ratio(
    returns: np.ndarray,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252
) -> float:
    """
    Calculate annualized Sharpe ratio.
    
    Args:
        returns: Array of period returns
        risk_free_rate: Risk-free rate (annualized)
        periods_per_year: Number of periods per year
    
    Returns:
        Sharpe ratio
    """
    if len(returns) == 0:
        return 0.0
    
    excess_returns = returns - (risk_free_rate / periods_per_year)
    
    if np.std(returns) == 0:
        return 0.0
    
    sharpe = np.mean(excess_returns) / np.std(returns) * np.sqrt(periods_per_year)
    return sharpe


def calculate_sortino_ratio(
    returns: np.ndarray,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252
) -> float:
    """
    Calculate annualized Sortino ratio (focuses on downside risk).
    
    Args:
        returns: Array of period returns
        risk_free_rate: Risk-free rate (annualized)
        periods_per_year: Number of periods per year
    
    Returns:
        Sortino ratio
    """
    if len(returns) == 0:
        return 0.0
    
    excess_returns = returns - (risk_free_rate / periods_per_year)
    downside_returns = returns[returns < 0]
    
    if len(downside_returns) == 0 or np.std(downside_returns) == 0:
        return 0.0
    
    sortino = np.mean(excess_returns) / np.std(downside_returns) * np.sqrt(periods_per_year)
    return sortino


def calculate_max_drawdown(equity_curve: np.ndarray) -> float:
    """
    Calculate maximum drawdown.
    
    Args:
        equity_curve: Array of cumulative equity values
    
    Returns:
        Maximum drawdown (as fraction, e.g., 0.2 = 20% drawdown)
    """
    if len(equity_curve) == 0:
        return 0.0
    
    running_max = np.maximum.accumulate(equity_curve)
    drawdowns = (equity_curve - running_max) / running_max
    max_dd = np.min(drawdowns)
    
    return abs(max_dd)


def calculate_profit_factor(returns: np.ndarray) -> float:
    """
    Calculate profit factor (gross profits / gross losses).
    
    Args:
        returns: Array of period returns
    
    Returns:
        Profit factor
    """
    if len(returns) == 0:
        return 0.0
    
    gross_profit = np.sum(returns[returns > 0])
    gross_loss = abs(np.sum(returns[returns < 0]))
    
    if gross_loss == 0:
        return np.inf if gross_profit > 0 else 0.0
    
    return gross_profit / gross_loss


def calculate_calmar_ratio(
    returns: np.ndarray,
    equity_curve: np.ndarray,
    periods_per_year: int = 252
) -> float:
    """
    Calculate Calmar ratio (annualized return / max drawdown).
    
    Args:
        returns: Array of period returns
        equity_curve: Array of cumulative equity values
        periods_per_year: Number of periods per year
    
    Returns:
        Calmar ratio
    """
    if len(returns) == 0 or len(equity_curve) == 0:
        return 0.0
    
    annualized_return = np.mean(returns) * periods_per_year
    max_dd = calculate_max_drawdown(equity_curve)
    
    if max_dd == 0:
        return np.inf if annualized_return > 0 else 0.0
    
    return annualized_return / max_dd


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    
    # P&L Metrics
    total_pnl: float
    mean_pnl: float
    std_pnl: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    
    # Risk Metrics
    max_drawdown: float
    value_at_risk_95: float  # 95% VaR
    conditional_var_95: float  # CVaR (Expected Shortfall)
    
    # Trading Metrics
    total_trades: int
    win_rate: float
    profit_factor: float
    avg_trade_pnl: float
    
    # Inventory Metrics
    mean_abs_inventory: float
    max_abs_inventory: float
    std_inventory: float
    
    # Market Making Specific
    avg_spread_captured: float
    fill_ratio: float
    adverse_selection_cost: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'total_pnl': self.total_pnl,
            'mean_pnl': self.mean_pnl,
            'std_pnl': self.std_pnl,
            'sharpe_ratio': self.sharpe_ratio,
            'sortino_ratio': self.sortino_ratio,
            'calmar_ratio': self.calmar_ratio,
            'max_drawdown': self.max_drawdown,
            'value_at_risk_95': self.value_at_risk_95,
            'conditional_var_95': self.conditional_var_95,
            'total_trades': self.total_trades,
            'win_rate': self.win_rate,
            'profit_factor': self.profit_factor,
            'avg_trade_pnl': self.avg_trade_pnl,
            'mean_abs_inventory': self.mean_abs_inventory,
            'max_abs_inventory': self.max_abs_inventory,
            'std_inventory': self.std_inventory,
            'avg_spread_captured': self.avg_spread_captured,
            'fill_ratio': self.fill_ratio,
            'adverse_selection_cost': self.adverse_selection_cost
        }
    
    def __str__(self) -> str:
        """String representation."""
        return f"""
Performance Metrics:
==================
P&L:
  Total P&L: ${self.total_pnl:.2f}
  Mean P&L: ${self.mean_pnl:.2f}
  Sharpe Ratio: {self.sharpe_ratio:.3f}
  Sortino Ratio: {self.sortino_ratio:.3f}
  Calmar Ratio: {self.calmar_ratio:.3f}

Risk:
  Max Drawdown: {self.max_drawdown:.2%}
  VaR (95%): ${self.value_at_risk_95:.2f}
  CVaR (95%): ${self.conditional_var_95:.2f}

Trading:
  Total Trades: {self.total_trades}
  Win Rate: {self.win_rate:.2%}
  Profit Factor: {self.profit_factor:.3f}
  Avg Trade P&L: ${self.avg_trade_pnl:.2f}

Inventory:
  Mean |Inventory|: {self.mean_abs_inventory:.1f}
  Max |Inventory|: {self.max_abs_inventory:.1f}
  Std Inventory: {self.std_inventory:.1f}

Market Making:
  Avg Spread Captured: {self.avg_spread_captured:.4f}
  Fill Ratio: {self.fill_ratio:.2%}
  Adverse Selection Cost: ${self.adverse_selection_cost:.2f}
"""


def calculate_performance_metrics(
    pnl_series: np.ndarray,
    inventory_series: np.ndarray,
    fills: List[Dict],
    spreads: List[float],
    total_quotes: int
) -> PerformanceMetrics:
    """
    Calculate comprehensive performance metrics.
    
    Args:
        pnl_series: Time series of P&L
        inventory_series: Time series of inventory
        fills: List of fill events with details
        spreads: List of spreads captured
        total_quotes: Total number of quotes posted
    
    Returns:
        PerformanceMetrics object
    """
    # P&L Metrics
    returns = np.diff(pnl_series)
    total_pnl = pnl_series[-1] - pnl_series[0] if len(pnl_series) > 0 else 0
    mean_pnl = np.mean(returns) if len(returns) > 0 else 0
    std_pnl = np.std(returns) if len(returns) > 0 else 0
    
    sharpe = calculate_sharpe_ratio(returns)
    sortino = calculate_sortino_ratio(returns)
    calmar = calculate_calmar_ratio(returns, pnl_series)
    
    # Risk Metrics
    max_dd = calculate_max_drawdown(pnl_series)
    var_95 = np.percentile(returns, 5) if len(returns) > 0 else 0
    cvar_95 = np.mean(returns[returns <= var_95]) if len(returns) > 0 and np.any(returns <= var_95) else 0
    
    # Trading Metrics
    total_trades = len(fills)
    winning_trades = sum(1 for f in fills if f.get('pnl', 0) > 0)
    win_rate = winning_trades / total_trades if total_trades > 0 else 0
    profit_factor = calculate_profit_factor(np.array([f.get('pnl', 0) for f in fills]))
    avg_trade_pnl = np.mean([f.get('pnl', 0) for f in fills]) if fills else 0
    
    # Inventory Metrics
    mean_abs_inv = np.mean(np.abs(inventory_series)) if len(inventory_series) > 0 else 0
    max_abs_inv = np.max(np.abs(inventory_series)) if len(inventory_series) > 0 else 0
    std_inv = np.std(inventory_series) if len(inventory_series) > 0 else 0
    
    # Market Making Metrics
    avg_spread = np.mean(spreads) if spreads else 0
    fill_ratio = total_trades / total_quotes if total_quotes > 0 else 0
    adverse_selection = sum(f.get('adverse_selection', 0) for f in fills)
    
    return PerformanceMetrics(
        total_pnl=total_pnl,
        mean_pnl=mean_pnl,
        std_pnl=std_pnl,
        sharpe_ratio=sharpe,
        sortino_ratio=sortino,
        calmar_ratio=calmar,
        max_drawdown=max_dd,
        value_at_risk_95=var_95,
        conditional_var_95=cvar_95,
        total_trades=total_trades,
        win_rate=win_rate,
        profit_factor=profit_factor,
        avg_trade_pnl=avg_trade_pnl,
        mean_abs_inventory=mean_abs_inv,
        max_abs_inventory=max_abs_inv,
        std_inventory=std_inv,
        avg_spread_captured=avg_spread,
        fill_ratio=fill_ratio,
        adverse_selection_cost=adverse_selection
    )
