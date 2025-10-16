"""
Streamlit Dashboard for Market Making Visualization

Interactive dashboard showing:
- Real-time order book
- P&L tracking
- Inventory management
- Performance metrics
"""

import streamlit as st
import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.simulation.market_simulator import MarketSimulator, SimulationConfig
from src.environments.market_making_env import MarketMakingEnv, MarketMakingConfig
from src.agents.baseline_agents import (
    RandomAgent, StaticSpreadAgent, 
    AvellanedaStoikovAgent, AdaptiveSpreadAgent
)
from src.evaluation.backtester import Backtester
from src.visualization.plotting import (
    plot_pnl_curve, plot_inventory_heatmap,
    plot_order_book, plot_performance_comparison,
    plot_volatility_regimes
)


st.set_page_config(
    page_title="Adaptive Liquidity Provision Engine",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    st.title("🎯 Adaptive Liquidity Provision Engine")
    st.markdown("### Market-Impact-Aware Reinforcement Learning for Market Making")
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Mode selection
    mode = st.sidebar.selectbox(
        "Mode",
        ["Live Simulation", "Backtest Comparison", "Strategy Analysis"]
    )
    
    if mode == "Live Simulation":
        live_simulation_page()
    elif mode == "Backtest Comparison":
        backtest_comparison_page()
    else:
        strategy_analysis_page()


def live_simulation_page():
    """Live simulation with real-time visualization."""
    st.header("🔴 Live Market Simulation")
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.subheader("Agent Selection")
        agent_type = st.selectbox(
            "Select Agent",
            ["Static Spread", "Avellaneda-Stoikov", "Adaptive Spread", "Random"]
        )
        
        st.subheader("Simulation Parameters")
        duration = st.slider("Duration (seconds)", 10, 500, 100)
        volatility = st.slider("Volatility", 0.01, 0.1, 0.02, 0.01)
        
        run_button = st.button("▶️ Run Simulation", type="primary")
    
    with col1:
        if run_button:
            with st.spinner("Running simulation..."):
                # Create environment
                sim_config = SimulationConfig(
                    initial_midprice=100.0,
                    initial_spread=0.02,
                    tick_size=0.01
                )
                sim_config.order_flow_config.base_volatility = volatility
                
                env_config = MarketMakingConfig(
                    episode_duration=duration,
                    time_step=1.0,
                    simulation_config=sim_config
                )
                
                env = MarketMakingEnv(env_config)
                
                # Create agent
                if agent_type == "Static Spread":
                    agent = StaticSpreadAgent(spread_ticks=2, quote_size=100)
                elif agent_type == "Avellaneda-Stoikov":
                    agent = AvellanedaStoikovAgent()
                elif agent_type == "Adaptive Spread":
                    agent = AdaptiveSpreadAgent()
                else:
                    agent = RandomAgent()
                
                # Run episode
                obs, _ = env.reset()
                done = False
                
                timestamps = []
                pnls = []
                inventories = []
                midprices = []
                spreads = []
                vols = []
                
                progress_bar = st.progress(0)
                
                step = 0
                max_steps = int(duration)
                
                while not done and step < max_steps:
                    action = agent.get_action(obs)
                    obs, reward, terminated, truncated, info = env.step(action)
                    done = terminated or truncated
                    
                    timestamps.append(info['time'])
                    pnls.append(info['pnl'])
                    inventories.append(info['inventory'])
                    midprices.append(info['midprice'])
                    spreads.append(info['spread'])
                    vols.append(info['volatility'])
                    
                    step += 1
                    progress_bar.progress(min(step / max_steps, 1.0))
                
                # Display results
                st.success(f"✅ Simulation Complete! Final P&L: ${pnls[-1]:.2f}")
                
                # Metrics
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                with col_m1:
                    st.metric("Final P&L", f"${pnls[-1]:.2f}")
                with col_m2:
                    st.metric("Final Inventory", f"{inventories[-1]}")
                with col_m3:
                    st.metric("Avg Spread", f"{np.mean(spreads):.4f}")
                with col_m4:
                    st.metric("Total Trades", info['num_trades'])
                
                # Plots
                st.plotly_chart(
                    plot_pnl_curve(np.array(timestamps), np.array(pnls)),
                    use_container_width=True
                )
                
                st.plotly_chart(
                    plot_inventory_heatmap(
                        np.array(timestamps),
                        np.array(inventories),
                        np.array(pnls)
                    ),
                    use_container_width=True
                )
                
                # Order book visualization
                st.subheader("📊 Final Order Book State")
                book_state = env.simulator.lob.get_book_depth(levels=10)
                fig_book = plot_order_book(
                    book_state['bids'],
                    book_state['asks'],
                    title="Order Book Depth (L2)"
                )
                st.plotly_chart(fig_book, use_container_width=True)


def backtest_comparison_page():
    """Compare multiple strategies via backtesting."""
    st.header("📊 Strategy Comparison")
    
    st.markdown("""
    Compare different market making strategies across multiple episodes.
    """)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Backtest Settings")
        num_episodes = st.number_input("Number of Episodes", 1, 50, 10)
        episode_duration = st.slider("Episode Duration (s)", 10, 200, 100)
        
        st.subheader("Select Agents")
        use_static = st.checkbox("Static Spread", value=True)
        use_avellaneda = st.checkbox("Avellaneda-Stoikov", value=True)
        use_adaptive = st.checkbox("Adaptive Spread", value=True)
        use_random = st.checkbox("Random (Baseline)", value=False)
        
        run_backtest = st.button("🚀 Run Backtest", type="primary")
    
    with col2:
        if run_backtest:
            with st.spinner("Running backtest..."):
                # Setup environment
                env_config = MarketMakingConfig(episode_duration=episode_duration)
                env = MarketMakingEnv(env_config)
                backtester = Backtester(env, verbose=False)
                
                # Create agent list
                agents = []
                if use_static:
                    agents.append((StaticSpreadAgent(), "Static Spread"))
                if use_avellaneda:
                    agents.append((AvellanedaStoikovAgent(), "Avellaneda-Stoikov"))
                if use_adaptive:
                    agents.append((AdaptiveSpreadAgent(), "Adaptive Spread"))
                if use_random:
                    agents.append((RandomAgent(), "Random"))
                
                # Run comparison
                results = backtester.compare_agents(agents, num_episodes=num_episodes)
                
                # Display results
                st.success("✅ Backtest Complete!")
                
                # Metrics table
                st.subheader("📈 Performance Metrics")
                
                metrics_data = []
                for name, result in results.items():
                    metrics_data.append({
                        'Agent': name,
                        'Total P&L': f"${result.metrics.total_pnl:.2f}",
                        'Sharpe Ratio': f"{result.metrics.sharpe_ratio:.3f}",
                        'Max Drawdown': f"{result.metrics.max_drawdown:.2%}",
                        'Win Rate': f"{result.metrics.win_rate:.2%}",
                        'Avg |Inventory|': f"{result.metrics.mean_abs_inventory:.1f}",
                        'Fill Ratio': f"{result.metrics.fill_ratio:.2%}"
                    })
                
                df_metrics = pd.DataFrame(metrics_data)
                st.dataframe(df_metrics, use_container_width=True)
                
                # Comparison plots
                st.subheader("📉 P&L Comparison")
                fig_pnl = plot_performance_comparison(results, metric='pnl')
                st.plotly_chart(fig_pnl, use_container_width=True)
                
                st.subheader("📦 Inventory Comparison")
                fig_inv = plot_performance_comparison(results, metric='inventory')
                st.plotly_chart(fig_inv, use_container_width=True)


def strategy_analysis_page():
    """Deep dive into a single strategy."""
    st.header("🔬 Strategy Deep Dive")
    
    st.markdown("""
    Analyze a single strategy's behavior in detail.
    """)
    
    agent_type = st.selectbox(
        "Select Strategy",
        ["Avellaneda-Stoikov", "Adaptive Spread", "Static Spread"]
    )
    
    if st.button("Analyze Strategy"):
        with st.spinner("Running analysis..."):
            # Setup
            env_config = MarketMakingConfig(episode_duration=100)
            env = MarketMakingEnv(env_config)
            
            if agent_type == "Avellaneda-Stoikov":
                agent = AvellanedaStoikovAgent()
            elif agent_type == "Adaptive Spread":
                agent = AdaptiveSpreadAgent()
            else:
                agent = StaticSpreadAgent()
            
            backtester = Backtester(env, verbose=False)
            result = backtester.backtest(agent, num_episodes=20, agent_name=agent_type)
            
            # Display metrics
            st.subheader("📊 Performance Summary")
            st.text(str(result.metrics))
            
            # Detailed plots
            st.subheader("💰 P&L Analysis")
            fig_pnl = plot_pnl_curve(result.timestamps, result.pnl_series)
            st.plotly_chart(fig_pnl, use_container_width=True)
            
            st.subheader("📦 Inventory Management")
            fig_inv = plot_inventory_heatmap(
                result.timestamps,
                result.inventory_series,
                result.pnl_series
            )
            st.plotly_chart(fig_inv, use_container_width=True)
            
            st.subheader("🌊 Volatility Impact")
            fig_vol = plot_volatility_regimes(
                result.timestamps,
                result.volatility_series,
                result.pnl_series
            )
            st.plotly_chart(fig_vol, use_container_width=True)
            
            # Episode statistics
            st.subheader("📈 Episode Statistics")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Episode Returns**")
                df_returns = pd.DataFrame({
                    'Episode': range(1, len(result.episode_returns) + 1),
                    'Return': result.episode_returns
                })
                st.line_chart(df_returns.set_index('Episode'))
            
            with col2:
                st.write("**Episode Sharpe Ratios**")
                df_sharpe = pd.DataFrame({
                    'Episode': range(1, len(result.episode_sharpes) + 1),
                    'Sharpe': result.episode_sharpes
                })
                st.line_chart(df_sharpe.set_index('Episode'))


if __name__ == "__main__":
    main()
