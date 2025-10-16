"""
Backtesting framework for market making strategies.

Tests agent performance across:
- Different volatility regimes
- Multiple episodes
- Various market conditions
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from tqdm import tqdm

from .metrics import calculate_performance_metrics, PerformanceMetrics


@dataclass
class BacktestResult:
    """Results from backtesting a strategy."""
    
    agent_name: str
    metrics: PerformanceMetrics
    
    # Time series data
    timestamps: np.ndarray
    pnl_series: np.ndarray
    inventory_series: np.ndarray
    midprice_series: np.ndarray
    spread_series: np.ndarray
    volatility_series: np.ndarray
    
    # Trade data
    fills: List[Dict]
    quotes: List[Dict]
    
    # Episode statistics
    num_episodes: int
    episode_returns: List[float] = field(default_factory=list)
    episode_sharpes: List[float] = field(default_factory=list)
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert time series to DataFrame."""
        df = pd.DataFrame({
            'timestamp': self.timestamps,
            'pnl': self.pnl_series,
            'inventory': self.inventory_series,
            'midprice': self.midprice_series,
            'spread': self.spread_series,
            'volatility': self.volatility_series
        })
        return df
    
    def summary(self) -> str:
        """Get summary string."""
        return f"""
Backtest Results for {self.agent_name}
{'='*50}
Episodes: {self.num_episodes}
{str(self.metrics)}
"""


class Backtester:
    """
    Backtesting engine for market making strategies.
    
    Features:
    - Multi-episode evaluation
    - Regime-specific testing
    - Comparative analysis
    - Statistical significance testing
    """
    
    def __init__(self, env, verbose: bool = True):
        """
        Initialize backtester.
        
        Args:
            env: Gymnasium environment
            verbose: Print progress
        """
        self.env = env
        self.verbose = verbose
    
    def run_episode(self, agent, render: bool = False) -> Dict[str, Any]:
        """
        Run a single episode.
        
        Args:
            agent: Agent to test (must have get_action method)
            render: Render environment
        
        Returns:
            Episode data dictionary
        """
        obs, info = self.env.reset()
        done = False
        
        # Track episode data
        episode_data = {
            'observations': [obs],
            'actions': [],
            'rewards': [],
            'infos': [info],
            'timestamps': [info['time']]
        }
        
        while not done:
            # Get action from agent
            action = agent.get_action(obs)
            episode_data['actions'].append(action)
            
            # Step environment
            obs, reward, terminated, truncated, info = self.env.step(action)
            done = terminated or truncated
            
            # Record data
            episode_data['observations'].append(obs)
            episode_data['rewards'].append(reward)
            episode_data['infos'].append(info)
            episode_data['timestamps'].append(info['time'])
            
            if render:
                self.env.render()
        
        # Calculate episode metrics
        episode_data['total_reward'] = sum(episode_data['rewards'])
        episode_data['final_pnl'] = info['pnl']
        episode_data['final_inventory'] = info['inventory']
        episode_data['num_steps'] = len(episode_data['rewards'])
        
        return episode_data
    
    def backtest(
        self,
        agent,
        num_episodes: int = 10,
        agent_name: Optional[str] = None
    ) -> BacktestResult:
        """
        Run full backtest over multiple episodes.
        
        Args:
            agent: Agent to test
            num_episodes: Number of episodes
            agent_name: Name for reporting
        
        Returns:
            BacktestResult object
        """
        if agent_name is None:
            agent_name = agent.__class__.__name__
        
        # Collect data from all episodes
        all_timestamps = []
        all_pnls = []
        all_inventories = []
        all_midprices = []
        all_spreads = []
        all_volatilities = []
        all_fills = []
        all_quotes = []
        episode_returns = []
        episode_sharpes = []
        
        iterator = tqdm(range(num_episodes), desc=f"Backtesting {agent_name}") if self.verbose else range(num_episodes)
        
        for episode in iterator:
            # Reset agent if stateful
            if hasattr(agent, 'reset'):
                agent.reset()
            
            # Run episode
            episode_data = self.run_episode(agent)
            
            # Extract time series
            infos = episode_data['infos']
            timestamps = np.array([info['time'] for info in infos])
            pnls = np.array([info['pnl'] for info in infos])
            inventories = np.array([info['inventory'] for info in infos])
            midprices = np.array([info['midprice'] for info in infos])
            spreads = np.array([info['spread'] for info in infos])
            volatilities = np.array([info['volatility'] for info in infos])
            
            # Accumulate
            all_timestamps.extend(timestamps)
            all_pnls.extend(pnls)
            all_inventories.extend(inventories)
            all_midprices.extend(midprices)
            all_spreads.extend(spreads)
            all_volatilities.extend(volatilities)
            
            # Episode stats
            episode_returns.append(episode_data['total_reward'])
            
            # Calculate episode Sharpe
            episode_rewards = np.array(episode_data['rewards'])
            if len(episode_rewards) > 1 and np.std(episode_rewards) > 0:
                ep_sharpe = np.mean(episode_rewards) / np.std(episode_rewards) * np.sqrt(len(episode_rewards))
            else:
                ep_sharpe = 0.0
            episode_sharpes.append(ep_sharpe)
        
        # Convert to arrays
        timestamps = np.array(all_timestamps)
        pnl_series = np.array(all_pnls)
        inventory_series = np.array(all_inventories)
        midprice_series = np.array(all_midprices)
        spread_series = np.array(all_spreads)
        volatility_series = np.array(all_volatilities)
        
        # Calculate metrics
        # Extract spreads captured (simplified - actual implementation would track fills)
        spreads_captured = spread_series[np.abs(np.diff(inventory_series, prepend=0)) > 0]
        total_quotes = num_episodes * episode_data['num_steps'] * 2  # Bid and ask
        
        metrics = calculate_performance_metrics(
            pnl_series=pnl_series,
            inventory_series=inventory_series,
            fills=all_fills,  # Would need to extract from episode data
            spreads=spreads_captured.tolist(),
            total_quotes=total_quotes
        )
        
        result = BacktestResult(
            agent_name=agent_name,
            metrics=metrics,
            timestamps=timestamps,
            pnl_series=pnl_series,
            inventory_series=inventory_series,
            midprice_series=midprice_series,
            spread_series=spread_series,
            volatility_series=volatility_series,
            fills=all_fills,
            quotes=all_quotes,
            num_episodes=num_episodes,
            episode_returns=episode_returns,
            episode_sharpes=episode_sharpes
        )
        
        if self.verbose:
            print(result.summary())
        
        return result
    
    def compare_agents(
        self,
        agents: List[tuple],  # List of (agent, name) tuples
        num_episodes: int = 10
    ) -> Dict[str, BacktestResult]:
        """
        Compare multiple agents.
        
        Args:
            agents: List of (agent, name) tuples
            num_episodes: Number of episodes per agent
        
        Returns:
            Dictionary mapping agent names to BacktestResults
        """
        results = {}
        
        for agent, name in agents:
            result = self.backtest(agent, num_episodes=num_episodes, agent_name=name)
            results[name] = result
        
        # Print comparison
        if self.verbose:
            self._print_comparison(results)
        
        return results
    
    def _print_comparison(self, results: Dict[str, BacktestResult]):
        """Print comparison table."""
        print("\n" + "="*80)
        print("AGENT COMPARISON")
        print("="*80)
        
        # Create comparison table
        metrics_to_compare = [
            ('Total P&L', 'total_pnl'),
            ('Sharpe Ratio', 'sharpe_ratio'),
            ('Max Drawdown', 'max_drawdown'),
            ('Win Rate', 'win_rate'),
            ('Avg |Inventory|', 'mean_abs_inventory'),
            ('Fill Ratio', 'fill_ratio')
        ]
        
        # Header
        print(f"{'Metric':<20}", end='')
        for name in results.keys():
            print(f"{name:<20}", end='')
        print()
        print("-" * 80)
        
        # Rows
        for metric_name, metric_key in metrics_to_compare:
            print(f"{metric_name:<20}", end='')
            for name, result in results.items():
                value = getattr(result.metrics, metric_key)
                if isinstance(value, float):
                    if 'ratio' in metric_key.lower():
                        print(f"{value:<20.3f}", end='')
                    elif 'rate' in metric_key.lower():
                        print(f"{value:<20.2%}", end='')
                    else:
                        print(f"{value:<20.2f}", end='')
                else:
                    print(f"{value:<20}", end='')
            print()
        
        print("="*80 + "\n")


def compare_strategies_statistical(
    results: Dict[str, BacktestResult],
    confidence_level: float = 0.95
) -> pd.DataFrame:
    """
    Perform statistical comparison of strategies.
    
    Args:
        results: Dictionary of BacktestResults
        confidence_level: Confidence level for intervals
    
    Returns:
        DataFrame with statistical comparison
    """
    from scipy import stats
    
    comparison_data = []
    
    for name, result in results.items():
        returns = result.episode_returns
        
        # Calculate statistics
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        # Confidence interval
        n = len(returns)
        t_val = stats.t.ppf((1 + confidence_level) / 2, n - 1)
        margin = t_val * std_return / np.sqrt(n)
        ci_lower = mean_return - margin
        ci_upper = mean_return + margin
        
        comparison_data.append({
            'Agent': name,
            'Mean Return': mean_return,
            'Std Return': std_return,
            'CI Lower': ci_lower,
            'CI Upper': ci_upper,
            'Sharpe': result.metrics.sharpe_ratio,
            'Max DD': result.metrics.max_drawdown
        })
    
    df = pd.DataFrame(comparison_data)
    return df
