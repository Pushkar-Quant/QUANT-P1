"""
Quick Start Example: Running a Simple Market Making Simulation

This script demonstrates:
1. Creating a market simulator
2. Running baseline agents
3. Evaluating performance
4. Basic visualization
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
import matplotlib.pyplot as plt
from src.environments.market_making_env import MarketMakingEnv, MarketMakingConfig
from src.agents.baseline_agents import (
    StaticSpreadAgent,
    AvellanedaStoikovAgent,
    AdaptiveSpreadAgent,
    RandomAgent
)
from src.evaluation.backtester import Backtester


def run_simple_episode():
    """Run a single episode with a static spread agent."""
    print("=" * 80)
    print("EXAMPLE 1: Single Episode Simulation")
    print("=" * 80 + "\n")
    
    # Create environment
    env_config = MarketMakingConfig(
        episode_duration=50.0,
        time_step=1.0
    )
    env = MarketMakingEnv(env_config)
    
    # Create agent
    agent = StaticSpreadAgent(spread_ticks=2, quote_size=100)
    
    # Run episode
    obs, _ = env.reset(seed=42)
    done = False
    step = 0
    
    pnls = []
    inventories = []
    
    print("Running episode...")
    while not done and step < 50:
        action = agent.get_action(obs)
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        
        pnls.append(info['pnl'])
        inventories.append(info['inventory'])
        
        if step % 10 == 0:
            print(f"  Step {step}: P&L=${info['pnl']:.2f}, Inventory={info['inventory']}")
        
        step += 1
    
    print(f"\n✓ Episode Complete!")
    print(f"  Final P&L: ${pnls[-1]:.2f}")
    print(f"  Final Inventory: {inventories[-1]}")
    print(f"  Steps: {step}")
    
    return pnls, inventories


def compare_multiple_agents():
    """Compare performance of different agents."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Comparing Multiple Strategies")
    print("=" * 80 + "\n")
    
    # Create environment
    env_config = MarketMakingConfig(episode_duration=100.0)
    env = MarketMakingEnv(env_config)
    
    # Create agents
    agents = [
        (StaticSpreadAgent(spread_ticks=2), "Static Spread (2 ticks)"),
        (AvellanedaStoikovAgent(), "Avellaneda-Stoikov"),
        (AdaptiveSpreadAgent(), "Adaptive Spread"),
        (RandomAgent(seed=42), "Random Baseline")
    ]
    
    # Run backtest
    print(f"Testing {len(agents)} agents with 5 episodes each...\n")
    backtester = Backtester(env, verbose=False)
    
    results = {}
    for agent, name in agents:
        print(f"Testing {name}...")
        result = backtester.backtest(agent, num_episodes=5, agent_name=name)
        results[name] = result
        print(f"  ✓ Final P&L: ${result.metrics.total_pnl:.2f}")
        print(f"  ✓ Sharpe Ratio: {result.metrics.sharpe_ratio:.3f}")
        print(f"  ✓ Avg |Inventory|: {result.metrics.mean_abs_inventory:.1f}\n")
    
    return results


def visualize_results(results):
    """Create visualization of results."""
    print("=" * 80)
    print("EXAMPLE 3: Visualization")
    print("=" * 80 + "\n")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Plot 1: P&L curves
    for name, result in results.items():
        axes[0, 0].plot(result.timestamps, result.pnl_series, label=name, linewidth=2)
    axes[0, 0].set_title('P&L Over Time', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel('Time (s)')
    axes[0, 0].set_ylabel('P&L ($)')
    axes[0, 0].legend()
    axes[0, 0].grid(alpha=0.3)
    axes[0, 0].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    
    # Plot 2: Inventory
    for name, result in results.items():
        axes[0, 1].plot(result.timestamps, result.inventory_series, label=name, linewidth=2)
    axes[0, 1].set_title('Inventory Over Time', fontsize=14, fontweight='bold')
    axes[0, 1].set_xlabel('Time (s)')
    axes[0, 1].set_ylabel('Inventory')
    axes[0, 1].legend()
    axes[0, 1].grid(alpha=0.3)
    axes[0, 1].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    
    # Plot 3: Sharpe Ratio comparison
    names = list(results.keys())
    sharpes = [results[name].metrics.sharpe_ratio for name in names]
    axes[1, 0].bar(names, sharpes, color=['#2E86AB', '#A23B72', '#06D6A0', '#F18F01'])
    axes[1, 0].set_title('Sharpe Ratio Comparison', fontsize=14, fontweight='bold')
    axes[1, 0].set_ylabel('Sharpe Ratio')
    axes[1, 0].tick_params(axis='x', rotation=45)
    axes[1, 0].grid(alpha=0.3, axis='y')
    
    # Plot 4: Final P&L comparison
    final_pnls = [results[name].metrics.total_pnl for name in names]
    colors = ['green' if p > 0 else 'red' for p in final_pnls]
    axes[1, 1].bar(names, final_pnls, color=colors, alpha=0.7)
    axes[1, 1].set_title('Total P&L Comparison', fontsize=14, fontweight='bold')
    axes[1, 1].set_ylabel('Total P&L ($)')
    axes[1, 1].tick_params(axis='x', rotation=45)
    axes[1, 1].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    axes[1, 1].grid(alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    # Save figure
    output_path = project_root / "examples" / "quick_start_results.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Visualization saved to {output_path}")
    
    plt.show()


def print_summary_table(results):
    """Print summary comparison table."""
    print("\n" + "=" * 80)
    print("SUMMARY: Performance Metrics")
    print("=" * 80 + "\n")
    
    # Header
    print(f"{'Agent':<25} {'P&L':<12} {'Sharpe':<10} {'Max DD':<10} {'Win Rate':<10}")
    print("-" * 80)
    
    # Rows
    for name, result in results.items():
        m = result.metrics
        print(f"{name:<25} "
              f"${m.total_pnl:<11.2f} "
              f"{m.sharpe_ratio:<9.3f} "
              f"{m.max_drawdown:<9.2%} "
              f"{m.win_rate:<9.2%}")
    
    print("=" * 80)


def main():
    """Main function."""
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  ADAPTIVE LIQUIDITY PROVISION ENGINE - QUICK START".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝\n")
    
    # Example 1: Single episode
    pnls, inventories = run_simple_episode()
    
    # Example 2: Compare agents
    results = compare_multiple_agents()
    
    # Example 3: Visualize
    visualize_results(results)
    
    # Summary
    print_summary_table(results)
    
    print("\n" + "=" * 80)
    print("✅ QUICK START COMPLETE!")
    print("=" * 80)
    print("\nNext Steps:")
    print("  1. Train an RL agent: python scripts/train.py")
    print("  2. Run evaluation: python scripts/evaluate.py --compare-all")
    print("  3. Launch dashboard: streamlit run src/visualization/dashboard.py")
    print("  4. Explore notebooks: jupyter notebook notebooks/01_getting_started.ipynb")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
