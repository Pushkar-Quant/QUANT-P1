# Technical Overview

## Adaptive Liquidity Provision Engine

This document provides a comprehensive technical overview of the market making framework.

---

## Table of Contents

1. [Architecture](#architecture)
2. [Core Components](#core-components)
3. [Mathematical Foundations](#mathematical-foundations)
4. [Implementation Details](#implementation-details)
5. [Performance Optimization](#performance-optimization)

---

## Architecture

### System Design

```
┌─────────────────────────────────────────────────────────┐
│                    RL Training Loop                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────┐  │
│  │   PPO    │───▶│   Env    │───▶│   Simulator      │  │
│  │  Agent   │◀───│          │◀───│   (LOB + Flow)   │  │
│  └──────────┘    └──────────┘    └──────────────────┘  │
│       │               │                    │             │
│       ▼               ▼                    ▼             │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────┐  │
│  │ Network  │    │  Reward  │    │  Impact Model    │  │
│  │ (Policy) │    │ Function │    │ (Almgren-Chriss) │  │
│  └──────────┘    └──────────┘    └──────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Market State → Observation**: LOB state transformed into feature vector
2. **Observation → Action**: RL policy outputs bid/ask offsets and sizes
3. **Action → Orders**: Orders submitted to limit order book
4. **Orders → Fills**: Matching engine processes order flow
5. **Fills → Reward**: Performance evaluated and fed back to agent

---

## Core Components

### 1. Limit Order Book (LOB)

**File**: `src/simulation/order_book.py`

**Features**:
- Price-time priority matching
- Queue position tracking
- O(log n) order insertion/deletion
- L2 market depth queries

**Key Classes**:
```python
class LimitOrderBook:
    - submit_order(order) -> List[Fill]
    - cancel_order(order_id) -> bool
    - get_midprice() -> float
    - get_order_book_imbalance() -> float
```

### 2. Order Flow Generator

**File**: `src/simulation/order_flow.py`

**Features**:
- Poisson arrival processes
- Stochastic order sizes
- Volatility regime switching
- Realistic latency modeling

**Models**:
- **Limit Orders**: Clustered around best quotes
- **Market Orders**: Take liquidity aggressively
- **Cancellations**: State-dependent rates

### 3. Market Impact Models

**File**: `src/impact/impact_models.py`

**Implemented Models**:

#### Almgren-Chriss Model
```
Temporary Impact: η * (|v| / √T) * σ
Permanent Impact: γ * v * σ
```

#### Square-Root Model
```
Impact: β * σ * √(|v| / V_daily) * sign(v)
```

### 4. Gymnasium Environment

**File**: `src/environments/market_making_env.py`

**Observation Space** (9D):
1. Midprice
2. Spread
3. Inventory
4. Volatility
5. Order book imbalance
6. Bid queue position (normalized)
7. Ask queue position (normalized)
8. Recent P&L change
9. Number of fills

**Action Space** (4D):
1. Bid offset (ticks from mid)
2. Ask offset (ticks from mid)
3. Bid size
4. Ask size

**Reward Function**:
```
R_t = ΔP&L - λ_I * I_t² - λ_V * σ_t² - λ_Q * ImpactCost
```

Where:
- `ΔP&L`: Change in profit/loss
- `I_t`: Current inventory
- `σ_t`: Current volatility
- `ImpactCost`: Market impact penalty

---

## Mathematical Foundations

### 1. Avellaneda-Stoikov Model

The optimal bid/ask spreads are derived from solving:

```
max E[X_T - q_T * S_T - α * Var(X_T)]
```

**Optimal Quotes**:
```
δ± = γ * σ² * (T - t) + (2/γ) * ln(1 + γ/k)
r = S - q * γ * σ² * (T - t)
bid = r - δ
ask = r + δ
```

Where:
- `γ`: Risk aversion parameter
- `σ`: Volatility
- `k`: Order arrival rate
- `q`: Inventory position
- `r`: Reservation price

### 2. Market Impact

**Temporary Impact** (mean-reverts):
```
ΔP_temp(t) = I_0 * exp(-λ * t)
```

**Permanent Impact** (persists):
```
ΔP_perm = γ * V * σ
```

**Total Execution Cost**:
```
Cost = V * (I_temp + I_perm/2)
```

### 3. Inventory Risk

**Value-at-Risk (VaR)**:
```
VaR_α = q * S * Φ^(-1)(α) * σ * √T
```

**Conditional VaR (CVaR)**:
```
CVaR_α = E[Loss | Loss > VaR_α]
```

---

## Implementation Details

### Event-Driven Simulation

The simulator uses discrete-event simulation for efficiency:

```python
def step(duration):
    # 1. Generate all events for time window
    events = order_flow.generate_events(duration)
    
    # 2. Sort by timestamp
    events.sort(key=lambda e: e.timestamp)
    
    # 3. Process sequentially
    for event in events:
        if event.type == "limit":
            lob.submit_limit_order(event)
        elif event.type == "market":
            fills = lob.execute_market_order(event)
            update_positions(fills)
        elif event.type == "cancel":
            lob.cancel_order(event.order_id)
    
    # 4. Update state
    return get_state()
```

### PPO Training

**Hyperparameters**:
- Learning rate: 3e-4 with linear decay
- Clip range: 0.2
- GAE λ: 0.95
- Entropy coefficient: 0.01
- Value function coefficient: 0.5

**Network Architecture**:
```
Input (9D) → Dense(256) → ReLU → Dense(256) → ReLU → Dense(128) → ReLU
                                                    ↓
                                           ┌────────┴────────┐
                                           ↓                 ↓
                                    Policy Head        Value Head
                                    Dense(4)           Dense(1)
```

### Curriculum Learning

Gradually increase difficulty:

```python
class CurriculumSchedule:
    phase_1: low_volatility (0-250k steps)
    phase_2: medium_volatility (250k-500k steps)
    phase_3: high_volatility (500k-1M steps)
    phase_4: regime_switching (1M+ steps)
```

---

## Performance Optimization

### 1. Computational Efficiency

**Order Book**:
- Use `sortedcontainers.SortedDict` for O(log n) operations
- Lazy deletion for cancelled orders
- Batch order processing

**Simulation**:
- Vectorized reward calculation
- Pre-generated order flow for reproducibility
- Numba JIT compilation for hot paths

### 2. Memory Management

```python
# Use circular buffers for time series
from collections import deque

class RollingBuffer:
    def __init__(self, maxlen=10000):
        self.buffer = deque(maxlen=maxlen)
```

### 3. Parallel Training

```python
# Ray RLlib for distributed training
from ray import tune

tune.run(
    "PPO",
    config={
        "num_workers": 8,
        "num_gpus": 1,
        ...
    }
)
```

---

## Key Performance Metrics

### 1. Profitability
- **Total P&L**: Cumulative profit/loss
- **Sharpe Ratio**: Risk-adjusted returns
- **Profit Factor**: Gross profit / gross loss

### 2. Risk Management
- **Max Drawdown**: Largest peak-to-trough decline
- **VaR / CVaR**: Tail risk measures
- **Inventory Std Dev**: Position volatility

### 3. Market Making Specific
- **Spread Captured**: Average spread earned per fill
- **Fill Ratio**: Orders filled / orders posted
- **Adverse Selection**: Cost of being "picked off"

---

## References

1. Avellaneda, M., & Stoikov, S. (2008). High-frequency trading in a limit order book. *Quantitative Finance*, 8(3), 217-224.

2. Almgren, R., & Chriss, N. (2001). Optimal execution of portfolio transactions. *Journal of Risk*, 3, 5-40.

3. Gueant, O., Lehalle, C. A., & Fernandez-Tapia, J. (2013). Dealing with the inventory risk: a solution to the market making problem. *Mathematics and Financial Economics*, 7(4), 477-507.

4. Schulman, J., Wolski, F., Dhariwal, P., Radford, A., & Klimov, O. (2017). Proximal policy optimization algorithms. *arXiv preprint arXiv:1707.06347*.

---

## Contact & Support

For questions or issues, please open an issue on GitHub or contact the development team.
