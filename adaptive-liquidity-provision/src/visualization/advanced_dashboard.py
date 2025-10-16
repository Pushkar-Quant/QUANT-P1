"""
Advanced Production Dashboard for Market Making Analysis

Features:
- Real-time performance monitoring
- Advanced analytics and insights
- Risk management dashboard
- Model comparison tools
- Export capabilities
"""

import streamlit as st
import numpy as np
import pandas as pd
from pathlib import Path
import sys
import json
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.simulation.market_simulator import MarketSimulator, SimulationConfig
from src.environments.market_making_env import MarketMakingEnv, MarketMakingConfig
from src.agents.baseline_agents import *
from src.evaluation.backtester import Backtester
from src.visualization.plotting import *


# Page configuration
st.set_page_config(
    page_title="Liquidity Provision Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-metric {
        border-left-color: #28a745;
    }
    .warning-metric {
        border-left-color: #ffc107;
    }
    .danger-metric {
        border-left-color: #dc3545;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)


def render_header():
    """Render professional header."""
    st.markdown('<h1 class="main-header">📊 Adaptive Liquidity Provision Analytics Platform</h1>', 
                unsafe_allow_html=True)
    st.markdown("---")


def render_kpi_dashboard(result):
    """Render KPI dashboard with metrics."""
    st.subheader("📈 Key Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        pnl = result.metrics.total_pnl
        pnl_color = "success" if pnl > 0 else "danger"
        st.markdown(f'<div class="metric-card {pnl_color}-metric">', unsafe_allow_html=True)
        st.metric("Total P&L", f"${pnl:,.2f}", 
                  delta=f"{pnl/1000:.1f}k" if abs(pnl) > 1000 else None)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        sharpe = result.metrics.sharpe_ratio
        sharpe_color = "success" if sharpe > 1 else "warning" if sharpe > 0.5 else "danger"
        st.markdown(f'<div class="metric-card {sharpe_color}-metric">', unsafe_allow_html=True)
        st.metric("Sharpe Ratio", f"{sharpe:.3f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        max_dd = result.metrics.max_drawdown
        dd_color = "success" if max_dd < 0.1 else "warning" if max_dd < 0.2 else "danger"
        st.markdown(f'<div class="metric-card {dd_color}-metric">', unsafe_allow_html=True)
        st.metric("Max Drawdown", f"{max_dd:.2%}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        win_rate = result.metrics.win_rate
        wr_color = "success" if win_rate > 0.6 else "warning" if win_rate > 0.4 else "danger"
        st.markdown(f'<div class="metric-card {wr_color}-metric">', unsafe_allow_html=True)
        st.metric("Win Rate", f"{win_rate:.1%}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col5:
        inv = result.metrics.mean_abs_inventory
        inv_color = "success" if inv < 200 else "warning" if inv < 400 else "danger"
        st.markdown(f'<div class="metric-card {inv_color}-metric">', unsafe_allow_html=True)
        st.metric("Avg |Inventory|", f"{inv:.0f}")
        st.markdown('</div>', unsafe_allow_html=True)


def render_advanced_analytics(result):
    """Render advanced analytics section."""
    st.subheader("🔬 Advanced Analytics")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Performance Analysis", 
        "⚠️ Risk Metrics",
        "📉 Drawdown Analysis",
        "💹 Trade Statistics"
    ])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Returns distribution
            returns = np.diff(result.pnl_series)
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=returns,
                nbinsx=50,
                name='Returns',
                marker_color='#1f77b4'
            ))
            fig.update_layout(
                title="Returns Distribution",
                xaxis_title="Return",
                yaxis_title="Frequency",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistics
            st.write("**Distribution Statistics**")
            stats_df = pd.DataFrame({
                'Metric': ['Mean', 'Std Dev', 'Skewness', 'Kurtosis'],
                'Value': [
                    f"{np.mean(returns):.4f}",
                    f"{np.std(returns):.4f}",
                    f"{pd.Series(returns).skew():.4f}",
                    f"{pd.Series(returns).kurtosis():.4f}"
                ]
            })
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
        
        with col2:
            # Cumulative returns
            cumulative = np.cumsum(returns)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=cumulative,
                mode='lines',
                name='Cumulative Returns',
                line=dict(color='#2ca02c', width=2)
            ))
            fig.update_layout(
                title="Cumulative Returns",
                xaxis_title="Time Step",
                yaxis_title="Cumulative Return",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Performance metrics
            st.write("**Risk-Adjusted Metrics**")
            metrics_df = pd.DataFrame({
                'Metric': ['Sortino Ratio', 'Calmar Ratio', 'Profit Factor'],
                'Value': [
                    f"{result.metrics.sortino_ratio:.3f}",
                    f"{result.metrics.calmar_ratio:.3f}",
                    f"{result.metrics.profit_factor:.3f}"
                ]
            })
            st.dataframe(metrics_df, use_container_width=True, hide_index=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # VaR and CVaR visualization
            returns = np.diff(result.pnl_series)
            var_95 = result.metrics.value_at_risk_95
            cvar_95 = result.metrics.conditional_var_95
            
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=returns,
                nbinsx=50,
                name='Returns',
                marker_color='#1f77b4',
                opacity=0.7
            ))
            fig.add_vline(x=var_95, line_dash="dash", line_color="red", 
                         annotation_text=f"VaR 95%: {var_95:.2f}")
            fig.add_vline(x=cvar_95, line_dash="dash", line_color="darkred",
                         annotation_text=f"CVaR 95%: {cvar_95:.2f}")
            fig.update_layout(
                title="Value at Risk Analysis",
                xaxis_title="Return",
                yaxis_title="Frequency",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Inventory risk over time
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=result.inventory_series,
                mode='lines',
                name='Inventory',
                line=dict(color='#ff7f0e', width=1.5),
                fill='tozeroy',
                fillcolor='rgba(255, 127, 14, 0.2)'
            ))
            
            # Add risk bands
            mean_inv = np.mean(result.inventory_series)
            std_inv = np.std(result.inventory_series)
            
            fig.add_hline(y=mean_inv + 2*std_inv, line_dash="dot", 
                         line_color="red", opacity=0.5)
            fig.add_hline(y=mean_inv - 2*std_inv, line_dash="dot",
                         line_color="red", opacity=0.5)
            
            fig.update_layout(
                title="Inventory Risk Bands (±2σ)",
                xaxis_title="Time Step",
                yaxis_title="Inventory",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Drawdown analysis
        equity = result.pnl_series
        running_max = np.maximum.accumulate(equity)
        drawdown = (equity - running_max) / running_max
        
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            subplot_titles=('Equity Curve', 'Drawdown'),
            vertical_spacing=0.1
        )
        
        fig.add_trace(
            go.Scatter(y=equity, name='Equity', line=dict(color='#2ca02c', width=2)),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(y=drawdown*100, name='Drawdown %', 
                      fill='tozeroy', fillcolor='rgba(220, 53, 69, 0.3)',
                      line=dict(color='#dc3545', width=1.5)),
            row=2, col=1
        )
        
        fig.update_xaxes(title_text="Time Step", row=2, col=1)
        fig.update_yaxes(title_text="P&L ($)", row=1, col=1)
        fig.update_yaxes(title_text="Drawdown (%)", row=2, col=1)
        
        fig.update_layout(
            template="plotly_white",
            height=600,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Drawdown statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Max Drawdown", f"{result.metrics.max_drawdown:.2%}")
        with col2:
            avg_dd = np.mean(np.abs(drawdown[drawdown < 0]))
            st.metric("Avg Drawdown", f"{avg_dd:.2%}")
        with col3:
            recovery_periods = []
            in_dd = False
            dd_start = 0
            for i, dd in enumerate(drawdown):
                if dd < -0.01 and not in_dd:
                    in_dd = True
                    dd_start = i
                elif dd >= -0.001 and in_dd:
                    in_dd = False
                    recovery_periods.append(i - dd_start)
            
            avg_recovery = np.mean(recovery_periods) if recovery_periods else 0
            st.metric("Avg Recovery Time", f"{avg_recovery:.0f} steps")
    
    with tab4:
        # Trade statistics
        st.write("**Trade Analysis**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            trade_metrics = pd.DataFrame({
                'Metric': [
                    'Total Trades',
                    'Win Rate',
                    'Profit Factor',
                    'Avg Trade P&L',
                    'Fill Ratio',
                    'Avg Spread Captured'
                ],
                'Value': [
                    f"{result.metrics.total_trades}",
                    f"{result.metrics.win_rate:.2%}",
                    f"{result.metrics.profit_factor:.3f}",
                    f"${result.metrics.avg_trade_pnl:.2f}",
                    f"{result.metrics.fill_ratio:.2%}",
                    f"{result.metrics.avg_spread_captured:.4f}"
                ]
            })
            st.dataframe(trade_metrics, use_container_width=True, hide_index=True)
        
        with col2:
            # Episode performance
            if hasattr(result, 'episode_returns') and len(result.episode_returns) > 0:
                fig = go.Figure()
                fig.add_trace(go.Box(
                    y=result.episode_returns,
                    name='Episode Returns',
                    marker_color='#1f77b4',
                    boxmean='sd'
                ))
                fig.update_layout(
                    title="Episode Returns Distribution",
                    yaxis_title="Return",
                    template="plotly_white"
                )
                st.plotly_chart(fig, use_container_width=True)


def main():
    """Main dashboard function."""
    render_header()
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/667eea/ffffff?text=ALPE", width=150)
        st.markdown("### ⚙️ Configuration")
        
        mode = st.selectbox(
            "Dashboard Mode",
            ["🔴 Live Simulation", "📊 Strategy Comparison", "🔬 Deep Analysis", "📈 Portfolio View"]
        )
        
        st.markdown("---")
        st.markdown("### 📋 Quick Stats")
        st.info("System Status: ✅ Online")
        st.success(f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")
    
    if mode == "🔴 Live Simulation":
        live_simulation_page()
    elif mode == "📊 Strategy Comparison":
        strategy_comparison_page()
    elif mode == "🔬 Deep Analysis":
        deep_analysis_page()
    else:
        portfolio_view_page()


def live_simulation_page():
    """Enhanced live simulation page."""
    st.header("🔴 Live Market Simulation")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_right:
        with st.expander("🎯 Agent Configuration", expanded=True):
            agent_type = st.selectbox(
                "Agent Type",
                ["Avellaneda-Stoikov", "Adaptive Spread", "Static Spread", "Random"]
            )
            
        with st.expander("⚙️ Market Parameters", expanded=True):
            duration = st.slider("Duration (s)", 10, 500, 100, 10)
            volatility = st.slider("Volatility", 0.01, 0.10, 0.02, 0.01)
            initial_price = st.number_input("Initial Price ($)", 50.0, 200.0, 100.0, 5.0)
        
        run_sim = st.button("▶️ Run Simulation", type="primary", use_container_width=True)
    
    with col_left:
        if run_sim:
            with st.spinner("🔄 Running simulation..."):
                # Setup
                sim_config = SimulationConfig(
                    initial_midprice=initial_price,
                    tick_size=0.01
                )
                env_config = MarketMakingConfig(
                    episode_duration=duration,
                    simulation_config=sim_config
                )
                env = MarketMakingEnv(env_config)
                
                # Create agent
                if agent_type == "Avellaneda-Stoikov":
                    agent = AvellanedaStoikovAgent()
                elif agent_type == "Adaptive Spread":
                    agent = AdaptiveSpreadAgent()
                elif agent_type == "Static Spread":
                    agent = StaticSpreadAgent()
                else:
                    agent = RandomAgent()
                
                # Run
                backtester = Backtester(env, verbose=False)
                result = backtester.backtest(agent, num_episodes=1, agent_name=agent_type)
                
                # Display KPIs
                render_kpi_dashboard(result)
                
                # Charts
                st.plotly_chart(
                    plot_pnl_curve(result.timestamps, result.pnl_series),
                    use_container_width=True
                )
                
                st.plotly_chart(
                    plot_inventory_heatmap(
                        result.timestamps,
                        result.inventory_series,
                        result.pnl_series
                    ),
                    use_container_width=True
                )


def strategy_comparison_page():
    """Enhanced strategy comparison."""
    st.header("📊 Multi-Strategy Performance Analysis")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Configuration")
        num_episodes = st.number_input("Episodes", 1, 50, 10, 1)
        episode_duration = st.slider("Duration (s)", 10, 200, 100, 10)
        
        st.subheader("Strategies")
        use_static = st.checkbox("Static Spread", value=True)
        use_avellaneda = st.checkbox("Avellaneda-Stoikov", value=True)
        use_adaptive = st.checkbox("Adaptive Spread", value=True)
        
        run_comparison = st.button("🚀 Run Comparison", type="primary", use_container_width=True)
    
    with col2:
        if run_comparison:
            with st.spinner("Running comprehensive backtest..."):
                env = MarketMakingEnv(MarketMakingConfig(episode_duration=episode_duration))
                backtester = Backtester(env, verbose=False)
                
                agents = []
                if use_static:
                    agents.append((StaticSpreadAgent(), "Static Spread"))
                if use_avellaneda:
                    agents.append((AvellanedaStoikovAgent(), "Avellaneda-Stoikov"))
                if use_adaptive:
                    agents.append((AdaptiveSpreadAgent(), "Adaptive Spread"))
                
                results = backtester.compare_agents(agents, num_episodes=num_episodes)
                
                # Comparison table
                st.subheader("📋 Performance Comparison")
                comparison_data = []
                for name, result in results.items():
                    comparison_data.append({
                        'Strategy': name,
                        'P&L': f"${result.metrics.total_pnl:,.2f}",
                        'Sharpe': f"{result.metrics.sharpe_ratio:.3f}",
                        'Max DD': f"{result.metrics.max_drawdown:.2%}",
                        'Win Rate': f"{result.metrics.win_rate:.1%}",
                        'Avg |Inv|': f"{result.metrics.mean_abs_inventory:.0f}"
                    })
                
                df_comparison = pd.DataFrame(comparison_data)
                st.dataframe(df_comparison, use_container_width=True, hide_index=True)
                
                # Charts
                st.plotly_chart(
                    plot_performance_comparison(results, metric='pnl'),
                    use_container_width=True
                )


def deep_analysis_page():
    """Deep analysis for single strategy."""
    st.header("🔬 Deep Strategy Analysis")
    
    agent_type = st.selectbox(
        "Select Strategy",
        ["Avellaneda-Stoikov", "Adaptive Spread", "Static Spread"]
    )
    
    if st.button("Analyze Strategy"):
        with st.spinner("Running deep analysis..."):
            env = MarketMakingEnv(MarketMakingConfig(episode_duration=100))
            
            if agent_type == "Avellaneda-Stoikov":
                agent = AvellanedaStoikovAgent()
            elif agent_type == "Adaptive Spread":
                agent = AdaptiveSpreadAgent()
            else:
                agent = StaticSpreadAgent()
            
            backtester = Backtester(env, verbose=False)
            result = backtester.backtest(agent, num_episodes=20, agent_name=agent_type)
            
            # KPIs
            render_kpi_dashboard(result)
            
            # Advanced analytics
            render_advanced_analytics(result)


def portfolio_view_page():
    """Portfolio view with multiple strategies."""
    st.header("📈 Portfolio Performance Dashboard")
    
    st.info("🚧 This feature allows you to run multiple strategies simultaneously and view aggregate performance.")
    
    # Placeholder for portfolio view
    st.write("Coming soon: Multi-strategy portfolio optimization and allocation")


if __name__ == "__main__":
    main()
