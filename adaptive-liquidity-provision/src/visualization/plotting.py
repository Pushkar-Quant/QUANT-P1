"""
Plotting utilities for visualization.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Dict, Optional


def plot_pnl_curve(
    timestamps: np.ndarray,
    pnl: np.ndarray,
    title: str = "P&L Curve"
) -> go.Figure:
    """
    Plot P&L curve over time.
    
    Args:
        timestamps: Time points
        pnl: P&L values
        title: Plot title
    
    Returns:
        Plotly figure
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=pnl,
        mode='lines',
        name='P&L',
        line=dict(color='#2E86AB', width=2)
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        title=title,
        xaxis_title="Time (s)",
        yaxis_title="P&L ($)",
        template="plotly_white",
        hovermode='x unified'
    )
    
    return fig


def plot_inventory_heatmap(
    timestamps: np.ndarray,
    inventory: np.ndarray,
    pnl: np.ndarray,
    title: str = "Inventory vs P&L"
) -> go.Figure:
    """
    Plot inventory and P&L heatmap.
    
    Args:
        timestamps: Time points
        inventory: Inventory values
        pnl: P&L values
        title: Plot title
    
    Returns:
        Plotly figure
    """
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=('Inventory Position', 'P&L')
    )
    
    # Inventory plot
    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=inventory,
            mode='lines',
            name='Inventory',
            line=dict(color='#A23B72', width=2),
            fill='tozeroy',
            fillcolor='rgba(162, 59, 114, 0.2)'
        ),
        row=1, col=1
    )
    
    # P&L plot
    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=pnl,
            mode='lines',
            name='P&L',
            line=dict(color='#2E86AB', width=2),
            fill='tozeroy',
            fillcolor='rgba(46, 134, 171, 0.2)'
        ),
        row=2, col=1
    )
    
    # Add zero lines
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=1, col=1)
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=2, col=1)
    
    fig.update_xaxes(title_text="Time (s)", row=2, col=1)
    fig.update_yaxes(title_text="Inventory", row=1, col=1)
    fig.update_yaxes(title_text="P&L ($)", row=2, col=1)
    
    fig.update_layout(
        title=title,
        template="plotly_white",
        height=600,
        showlegend=True
    )
    
    return fig


def plot_order_book(
    bids: List[tuple],
    asks: List[tuple],
    title: str = "Order Book Depth"
) -> go.Figure:
    """
    Plot L2 order book visualization.
    
    Args:
        bids: List of (price, size) tuples for bids
        asks: List of (price, size) tuples for asks
        title: Plot title
    
    Returns:
        Plotly figure
    """
    fig = go.Figure()
    
    if bids:
        bid_prices, bid_sizes = zip(*bids)
        fig.add_trace(go.Bar(
            x=bid_sizes,
            y=bid_prices,
            orientation='h',
            name='Bids',
            marker=dict(color='#06D6A0'),
            text=bid_sizes,
            textposition='auto'
        ))
    
    if asks:
        ask_prices, ask_sizes = zip(*asks)
        fig.add_trace(go.Bar(
            x=[-s for s in ask_sizes],  # Negative for left side
            y=ask_prices,
            orientation='h',
            name='Asks',
            marker=dict(color='#EF476F'),
            text=ask_sizes,
            textposition='auto'
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Size",
        yaxis_title="Price",
        template="plotly_white",
        barmode='overlay',
        showlegend=True
    )
    
    return fig


def plot_performance_comparison(
    results: Dict[str, 'BacktestResult'],
    metric: str = 'pnl'
) -> go.Figure:
    """
    Compare multiple agents' performance.
    
    Args:
        results: Dictionary mapping agent names to BacktestResults
        metric: Metric to compare ('pnl', 'inventory', 'sharpe')
    
    Returns:
        Plotly figure
    """
    fig = go.Figure()
    
    for name, result in results.items():
        if metric == 'pnl':
            y_data = result.pnl_series
            y_label = 'P&L ($)'
        elif metric == 'inventory':
            y_data = result.inventory_series
            y_label = 'Inventory'
        elif metric == 'sharpe':
            # Plot episode Sharpe ratios
            y_data = result.episode_sharpes
            y_label = 'Sharpe Ratio'
            fig.add_trace(go.Box(
                y=y_data,
                name=name,
                boxmean='sd'
            ))
            continue
        else:
            raise ValueError(f"Unknown metric: {metric}")
        
        fig.add_trace(go.Scatter(
            x=result.timestamps,
            y=y_data,
            mode='lines',
            name=name,
            line=dict(width=2)
        ))
    
    fig.update_layout(
        title=f"Agent Comparison: {metric.upper()}",
        xaxis_title="Time (s)" if metric != 'sharpe' else "",
        yaxis_title=y_label,
        template="plotly_white",
        hovermode='x unified'
    )
    
    return fig


def plot_metrics_radar(metrics_dict: Dict[str, float]) -> go.Figure:
    """
    Create radar chart for performance metrics.
    
    Args:
        metrics_dict: Dictionary of metric names to normalized values
    
    Returns:
        Plotly figure
    """
    categories = list(metrics_dict.keys())
    values = list(metrics_dict.values())
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Metrics'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=False,
        title="Performance Metrics (Normalized)"
    )
    
    return fig


def plot_volatility_regimes(
    timestamps: np.ndarray,
    volatility: np.ndarray,
    pnl: np.ndarray
) -> go.Figure:
    """
    Plot P&L colored by volatility regime.
    
    Args:
        timestamps: Time points
        volatility: Volatility values
        pnl: P&L values
    
    Returns:
        Plotly figure
    """
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=('P&L', 'Volatility Regime')
    )
    
    # P&L with color gradient based on volatility
    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=pnl,
            mode='lines',
            name='P&L',
            line=dict(width=2, color='#2E86AB')
        ),
        row=1, col=1
    )
    
    # Volatility
    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=volatility,
            mode='lines',
            name='Volatility',
            line=dict(width=2, color='#F18F01'),
            fill='tozeroy',
            fillcolor='rgba(241, 143, 1, 0.2)'
        ),
        row=2, col=1
    )
    
    fig.update_xaxes(title_text="Time (s)", row=2, col=1)
    fig.update_yaxes(title_text="P&L ($)", row=1, col=1)
    fig.update_yaxes(title_text="Volatility", row=2, col=1)
    
    fig.update_layout(
        title="P&L and Volatility Regimes",
        template="plotly_white",
        height=600
    )
    
    return fig
