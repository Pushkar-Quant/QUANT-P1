# User Guide

## Adaptive Liquidity Provision Engine

Welcome to the comprehensive guide for using the Adaptive Liquidity Provision Engine.

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Training Your First Agent](#training-your-first-agent)
4. [Evaluating Performance](#evaluating-performance)
5. [Using the Dashboard](#using-the-dashboard)
6. [Advanced Topics](#advanced-topics)
7. [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager
- (Optional) CUDA-capable GPU for faster training

### Step 1: Clone or Download

If you haven't already, obtain the project files.

### Step 2: Create Virtual Environment

```bash
cd QUANT-P1
python -m venv venv
```

### Step 3: Activate Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Verify Installation

```bash
python -c "import src; print('✓ Installation successful!')"
```

---

## Quick Start

### Run the Quick Start Example

The fastest way to see the system in action:

```bash
python examples/quick_start.py
```

This will:
1. ✓ Run a simple simulation
2. ✓ Compare 4 different strategies
3. ✓ Generate visualizations
4. ✓ Display performance metrics

Expected output:
```
ADAPTIVE LIQUIDITY PROVISION ENGINE - QUICK START
==================================================

EXAMPLE 1: Single Episode Simulation
Running episode...
  Step 0: P&L=$0.00, Inventory=0
  Step 10: P&L=$12.50, Inventory=-50
  ...
```

---

## Training Your First Agent

### Option 1: Use Default Configuration

```bash
python scripts/train.py --timesteps 500000 --eval
```

This trains a PPO agent for 500,000 timesteps and runs evaluation afterward.

### Option 2: Use Configuration File

```bash
python scripts/train.py --config experiments/configs/ppo_baseline.yaml
```

### Option 3: Custom Parameters

```bash
python scripts/train.py \
    --timesteps 1000000 \
    --learning-rate 0.0003 \
    --use-curriculum \
    --eval \
    --output-dir experiments/runs/my_agent
```

### Training Progress

Monitor training with Tensorboard:

```bash
tensorboard --logdir experiments/runs/ppo_baseline/tensorboard
```

Then open `http://localhost:6006` in your browser.

### Expected Training Time

- **CPU**: ~2-4 hours for 1M timesteps
- **GPU**: ~30-60 minutes for 1M timesteps

---

## Evaluating Performance

### Evaluate a Trained Model

```bash
python scripts/evaluate.py \
    --model experiments/runs/ppo_baseline/ppo_market_maker_final.zip \
    --episodes 20
```

### Compare All Agents

```bash
python scripts/evaluate.py --compare-all --episodes 20
```

This compares:
- ✓ Trained PPO agent (if available)
- ✓ Static Spread strategy
- ✓ Avellaneda-Stoikov strategy
- ✓ Adaptive Spread strategy
- ✓ Random baseline

### Output

Results are saved to `experiments/evaluation/`:
- `metrics.json` - Performance metrics
- `comparison.csv` - Comparison table
- `summary_report.txt` - Detailed report
- Individual CSV files for each agent

---

## Using the Dashboard

### Launch the Dashboard

```bash
streamlit run src/visualization/dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`.

### Dashboard Features

#### 1. Live Simulation Mode
- Select an agent
- Configure simulation parameters
- Watch real-time P&L and inventory
- View order book depth

#### 2. Backtest Comparison Mode
- Compare multiple strategies
- Run multiple episodes
- Generate performance reports

#### 3. Strategy Analysis Mode
- Deep dive into single strategy
- Analyze volatility impact
- Episode-by-episode breakdown

### Tips for Dashboard Use

- Use shorter episodes (50-100s) for faster iteration
- Compare agents with same random seed for fair comparison
- Export plots by right-clicking on charts

---

## Advanced Topics

### Custom Agents

Create your own agent by inheriting from `BaseAgent`:

```python
from src.agents.baseline_agents import BaseAgent
import numpy as np

class MyCustomAgent(BaseAgent):
    def get_action(self, observation: np.ndarray) -> np.ndarray:
        # observation[0] = midprice
        # observation[1] = spread
        # observation[2] = inventory
        
        # Your logic here
        bid_offset = 2.0
        ask_offset = 2.0
        bid_size = 100.0
        ask_size = 100.0
        
        return np.array([bid_offset, ask_offset, bid_size, ask_size])
    
    def reset(self):
        pass
```

Then test it:

```python
from src.environments.market_making_env import MarketMakingEnv
from src.evaluation.backtester import Backtester

env = MarketMakingEnv()
backtester = Backtester(env)
agent = MyCustomAgent()

result = backtester.backtest(agent, num_episodes=10)
print(result.summary())
```

### Modifying Reward Function

Edit `src/environments/market_making_env.py`:

```python
def _calculate_reward(self) -> float:
    # Custom reward components
    pnl_change = current_pnl - self.prev_pnl
    inventory_penalty = self.config.inventory_penalty_lambda * (inventory ** 2)
    
    # Add your custom penalties/rewards
    custom_component = your_logic_here()
    
    reward = pnl_change - inventory_penalty + custom_component
    return reward
```

### Adjusting Market Microstructure

Modify order flow in `src/simulation/order_flow.py`:

```python
config = OrderFlowConfig(
    limit_order_rate=20.0,      # More limit orders
    market_order_rate=5.0,       # More market orders
    mean_order_size=200,         # Larger orders
    base_volatility=0.05,        # Higher volatility
    # ... other parameters
)

order_flow = OrderFlowGenerator(config)
```

### Multi-Asset Market Making

Extend to multiple assets:

```python
# Create multiple environments
assets = ['AAPL', 'MSFT', 'GOOGL']
envs = [MarketMakingEnv(config) for _ in assets]

# Train multi-asset agent
from stable_baselines3.common.vec_env import DummyVecEnv

vec_env = DummyVecEnv([lambda: env for env in envs])
agent = PPO("MlpPolicy", vec_env)
agent.learn(total_timesteps=1000000)
```

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```bash
# Make sure you're in the project root
cd QUANT-P1

# Run Python with module mode
python -m scripts.train  # Instead of python scripts/train.py
```

Or add to path:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

#### 2. CUDA/GPU Issues

**Problem**: `RuntimeError: CUDA out of memory`

**Solution**: Use CPU or reduce batch size:
```bash
python scripts/train.py --device cpu
```

Or in code:
```python
agent = PPOMarketMaker(env, device='cpu')
```

#### 3. Slow Training

**Problem**: Training is very slow

**Solutions**:
- Reduce `n_steps` in config (e.g., from 2048 to 1024)
- Reduce `episode_duration` (e.g., from 100 to 50)
- Use GPU if available
- Reduce number of parallel environments

#### 4. Poor Performance

**Problem**: Agent doesn't learn or performs worse than baseline

**Solutions**:
- Train longer (at least 500k timesteps)
- Enable curriculum learning: `--use-curriculum`
- Adjust reward penalties (reduce inventory penalty if too conservative)
- Check observation normalization
- Ensure environment is stable (no NaN values)

#### 5. Dashboard Won't Start

**Problem**: Streamlit dashboard fails to launch

**Solution**:
```bash
# Reinstall streamlit
pip install --upgrade streamlit

# Try different port
streamlit run src/visualization/dashboard.py --server.port 8502
```

---

## Performance Benchmarks

### Expected Results (Baseline Strategies)

After 1M training steps, you should see:

| Strategy | Sharpe Ratio | Avg P&L | Max DD |
|----------|-------------|---------|--------|
| Random | -0.2 to 0.1 | -$500 to $100 | 20-30% |
| Static Spread | 0.3 to 0.8 | $500 to $2000 | 10-15% |
| Avellaneda-Stoikov | 0.5 to 1.2 | $1000 to $3000 | 8-12% |
| Trained PPO | **0.8 to 1.8** | **$2000 to $5000** | **5-10%** |

*Results vary based on market conditions and configuration*

---

## Best Practices

### 1. Start Simple
- Begin with short episodes (50-100s)
- Use baseline strategies to understand behavior
- Gradually increase complexity

### 2. Monitor Training
- Always use Tensorboard
- Check for NaN values
- Monitor reward trends

### 3. Iterate Quickly
- Start with fewer timesteps (100k-500k)
- Test hyperparameters
- Scale up once stable

### 4. Version Control
- Save training configs with models
- Track experiment results
- Document changes

### 5. Validate Thoroughly
- Test on multiple seeds
- Compare against baselines
- Check edge cases

---

## Further Reading

### Academic Papers

1. **Avellaneda & Stoikov (2008)**: "High-frequency trading in a limit order book"
2. **Almgren & Chriss (2001)**: "Optimal execution of portfolio transactions"
3. **Guéant et al. (2013)**: "Dealing with the inventory risk"

### Code References

- Stable-Baselines3: https://stable-baselines3.readthedocs.io/
- Gymnasium: https://gymnasium.farama.org/
- Ray RLlib: https://docs.ray.io/en/latest/rllib/

---

## Getting Help

### Resources

1. **Documentation**: See `docs/TECHNICAL_OVERVIEW.md`
2. **Examples**: Check `examples/` directory
3. **Notebooks**: Explore `notebooks/` for interactive tutorials
4. **Tests**: Review `tests/` for usage examples

### Community

- Open an issue on GitHub
- Check existing issues for solutions
- Contribute improvements via pull requests

---

## Next Steps

Now that you're familiar with the basics:

1. ✅ Run `examples/quick_start.py`
2. ✅ Train your first agent
3. ✅ Explore the dashboard
4. ✅ Read the Jupyter notebooks
5. ✅ Modify and experiment!

Happy market making! 🚀📈

---

*Last updated: 2025*
