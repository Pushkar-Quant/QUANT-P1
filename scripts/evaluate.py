"""
Evaluation script for trained agents.

Usage:
    python scripts/evaluate.py --model experiments/runs/ppo_baseline/model.zip
    python scripts/evaluate.py --compare-all --episodes 20
"""

import argparse
from pathlib import Path
import sys
import json

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.environments.market_making_env import MarketMakingEnv, MarketMakingConfig
from src.agents.baseline_agents import (
    StaticSpreadAgent, AvellanedaStoikovAgent, 
    AdaptiveSpreadAgent, RandomAgent
)
from src.agents.ppo_agent import PPOMarketMaker
from src.evaluation.backtester import Backtester
import pandas as pd


def evaluate_model(model_path: str, env: MarketMakingEnv, num_episodes: int = 10):
    """Evaluate a trained model."""
    print(f"\n📦 Loading model from {model_path}")
    agent = PPOMarketMaker(env)
    agent.load(model_path)
    
    print(f"🧪 Running evaluation with {num_episodes} episodes...")
    backtester = Backtester(env, verbose=True)
    result = backtester.backtest(agent, num_episodes=num_episodes, agent_name="Trained PPO")
    
    return result


def compare_all_agents(env: MarketMakingEnv, num_episodes: int = 10, model_path: str = None):
    """Compare all available agents."""
    print("\n" + "=" * 80)
    print("COMPARATIVE EVALUATION OF ALL STRATEGIES")
    print("=" * 80)
    
    agents = [
        (StaticSpreadAgent(spread_ticks=2), "Static Spread"),
        (AvellanedaStoikovAgent(), "Avellaneda-Stoikov"),
        (AdaptiveSpreadAgent(), "Adaptive Spread"),
        (RandomAgent(), "Random Baseline")
    ]
    
    # Add trained model if provided
    if model_path and Path(model_path).exists():
        ppo_agent = PPOMarketMaker(env)
        ppo_agent.load(model_path)
        agents.append((ppo_agent, "Trained PPO"))
        print(f"✓ Loaded trained PPO model from {model_path}")
    
    print(f"\n🧪 Testing {len(agents)} agents with {num_episodes} episodes each...")
    
    backtester = Backtester(env, verbose=True)
    results = backtester.compare_agents(agents, num_episodes=num_episodes)
    
    return results


def save_results(results: dict, output_path: Path):
    """Save evaluation results."""
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save metrics to JSON
    metrics_dict = {}
    for name, result in results.items():
        metrics_dict[name] = result.metrics.to_dict()
    
    json_path = output_path / "metrics.json"
    with open(json_path, 'w') as f:
        json.dump(metrics_dict, f, indent=2)
    print(f"\n✓ Metrics saved to {json_path}")
    
    # Save time series to CSV
    for name, result in results.items():
        df = result.to_dataframe()
        csv_path = output_path / f"{name.replace(' ', '_').lower()}_timeseries.csv"
        df.to_csv(csv_path, index=False)
    print(f"✓ Time series saved to {output_path}")
    
    # Save comparison table
    comparison_data = []
    for name, result in results.items():
        comparison_data.append({
            'Agent': name,
            'Total P&L': result.metrics.total_pnl,
            'Sharpe Ratio': result.metrics.sharpe_ratio,
            'Max Drawdown': result.metrics.max_drawdown,
            'Win Rate': result.metrics.win_rate,
            'Mean |Inventory|': result.metrics.mean_abs_inventory,
            'Profit Factor': result.metrics.profit_factor
        })
    
    df_comparison = pd.DataFrame(comparison_data)
    comparison_path = output_path / "comparison.csv"
    df_comparison.to_csv(comparison_path, index=False)
    print(f"✓ Comparison table saved to {comparison_path}")
    
    # Save summary report
    report_path = output_path / "summary_report.txt"
    with open(report_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("EVALUATION SUMMARY REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        for name, result in results.items():
            f.write(result.summary())
            f.write("\n" + "=" * 80 + "\n\n")
    
    print(f"✓ Summary report saved to {report_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate market making agents"
    )
    
    parser.add_argument(
        '--model',
        type=str,
        help='Path to trained model (.zip file)'
    )
    
    parser.add_argument(
        '--compare-all',
        action='store_true',
        help='Compare all available agents'
    )
    
    parser.add_argument(
        '--episodes',
        type=int,
        default=10,
        help='Number of episodes for evaluation'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='experiments/evaluation',
        help='Output directory for results'
    )
    
    parser.add_argument(
        '--episode-duration',
        type=float,
        default=100.0,
        help='Duration of each episode in seconds'
    )
    
    args = parser.parse_args()
    
    # Create environment
    print("\n✓ Creating evaluation environment...")
    env_config = MarketMakingConfig(
        episode_duration=args.episode_duration,
        time_step=1.0
    )
    env = MarketMakingEnv(env_config)
    
    # Run evaluation
    if args.compare_all:
        results = compare_all_agents(env, args.episodes, args.model)
    elif args.model:
        result = evaluate_model(args.model, env, args.episodes)
        results = {"Trained Model": result}
    else:
        print("❌ Error: Must specify either --model or --compare-all")
        return
    
    # Save results
    output_path = Path(args.output_dir)
    save_results(results, output_path)
    
    print("\n" + "=" * 80)
    print("✅ EVALUATION COMPLETE")
    print("=" * 80)
    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
