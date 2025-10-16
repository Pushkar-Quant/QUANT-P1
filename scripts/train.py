"""
Training script for PPO market making agent.

Usage:
    python scripts/train.py --config experiments/configs/ppo_baseline.yaml
    python scripts/train.py --timesteps 1000000 --lr 0.0003
"""

import argparse
import yaml
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.environments.market_making_env import MarketMakingEnv, MarketMakingConfig
from src.simulation.market_simulator import SimulationConfig
from src.agents.ppo_agent import PPOMarketMaker, CurriculumCallback, MetricsCallback
from src.evaluation.backtester import Backtester
import torch


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def create_env_from_config(config: dict) -> MarketMakingEnv:
    """Create environment from configuration."""
    sim_config = SimulationConfig(
        initial_midprice=config.get('initial_midprice', 100.0),
        initial_spread=config.get('initial_spread', 0.02),
        tick_size=config.get('tick_size', 0.01),
        seed=config.get('seed')
    )
    
    mm_config = MarketMakingConfig(
        episode_duration=config.get('episode_duration', 100.0),
        time_step=config.get('time_step', 1.0),
        initial_cash=config.get('initial_cash', 100000.0),
        max_inventory=config.get('max_inventory', 1000),
        inventory_penalty_lambda=config.get('inventory_penalty', 0.01),
        simulation_config=sim_config
    )
    
    return MarketMakingEnv(mm_config)


def train(args):
    """Main training function."""
    print("=" * 80)
    print("ADAPTIVE LIQUIDITY PROVISION ENGINE - TRAINING")
    print("=" * 80)
    
    # Load config if provided
    if args.config:
        config = load_config(args.config)
        print(f"\n✓ Loaded configuration from {args.config}")
    else:
        config = {}
    
    # Override with command line arguments
    if args.timesteps:
        config['total_timesteps'] = args.timesteps
    if args.learning_rate:
        config['learning_rate'] = args.learning_rate
    
    # Set defaults
    config.setdefault('total_timesteps', 1000000)
    config.setdefault('learning_rate', 3e-4)
    config.setdefault('n_steps', 2048)
    config.setdefault('batch_size', 64)
    config.setdefault('save_freq', 50000)
    
    print(f"\nTraining Configuration:")
    print(f"  Total Timesteps: {config['total_timesteps']:,}")
    print(f"  Learning Rate: {config['learning_rate']}")
    print(f"  N Steps: {config['n_steps']}")
    print(f"  Batch Size: {config['batch_size']}")
    
    # Create environment
    print("\n✓ Creating environment...")
    env = create_env_from_config(config)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    tensorboard_dir = output_dir / "tensorboard"
    tensorboard_dir.mkdir(exist_ok=True)
    
    print(f"✓ Output directory: {output_dir}")
    print(f"✓ Tensorboard logs: {tensorboard_dir}")
    
    # Create agent
    print("\n✓ Creating PPO agent...")
    agent = PPOMarketMaker(
        env=env,
        learning_rate=config['learning_rate'],
        n_steps=config['n_steps'],
        batch_size=config['batch_size'],
        tensorboard_log=str(tensorboard_dir),
        verbose=1,
        device='cuda' if torch.cuda.is_available() else 'cpu'
    )
    
    print(f"✓ Using device: {agent.model.device}")
    
    # Create callbacks
    callbacks = []
    
    if args.use_curriculum:
        print("✓ Enabling curriculum learning...")
        curriculum = CurriculumCallback(
            initial_vol=0.01,
            target_vol=0.05,
            vol_increase_steps=config['total_timesteps'] // 2
        )
        callbacks.append(curriculum)
    
    metrics_callback = MetricsCallback(log_freq=1000)
    callbacks.append(metrics_callback)
    
    # Train
    print("\n" + "=" * 80)
    print("STARTING TRAINING")
    print("=" * 80 + "\n")
    
    try:
        agent.train(
            total_timesteps=config['total_timesteps'],
            callback=callbacks,
            log_interval=10
        )
        
        print("\n" + "=" * 80)
        print("TRAINING COMPLETE")
        print("=" * 80)
        
        # Save final model
        model_path = output_dir / "ppo_market_maker_final.zip"
        agent.save(str(model_path))
        print(f"\n✓ Model saved to {model_path}")
        
        # Run evaluation
        if args.eval:
            print("\n" + "=" * 80)
            print("RUNNING EVALUATION")
            print("=" * 80 + "\n")
            
            backtester = Backtester(env, verbose=True)
            result = backtester.backtest(agent, num_episodes=10, agent_name="PPO Agent")
            
            # Save results
            results_path = output_dir / "evaluation_results.txt"
            with open(results_path, 'w') as f:
                f.write(result.summary())
            print(f"\n✓ Results saved to {results_path}")
        
        print("\n✅ All done! Run tensorboard to view training curves:")
        print(f"   tensorboard --logdir {tensorboard_dir}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user")
        model_path = output_dir / "ppo_market_maker_interrupted.zip"
        agent.save(str(model_path))
        print(f"✓ Model saved to {model_path}")
    
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Train PPO agent for adaptive market making"
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to YAML configuration file'
    )
    
    parser.add_argument(
        '--timesteps',
        type=int,
        help='Total timesteps to train (overrides config)'
    )
    
    parser.add_argument(
        '--learning-rate', '--lr',
        type=float,
        help='Learning rate (overrides config)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='experiments/runs/ppo_baseline',
        help='Output directory for models and logs'
    )
    
    parser.add_argument(
        '--use-curriculum',
        action='store_true',
        help='Enable curriculum learning'
    )
    
    parser.add_argument(
        '--eval',
        action='store_true',
        help='Run evaluation after training'
    )
    
    args = parser.parse_args()
    train(args)


if __name__ == "__main__":
    main()
