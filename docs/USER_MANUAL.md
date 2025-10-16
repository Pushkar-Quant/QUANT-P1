# 📘 User Manual - Adaptive Liquidity Provision Engine

## 🎯 Welcome!

This is your complete guide to using the **Adaptive Liquidity Provision Engine** - a professional market making analytics platform powered by reinforcement learning.

**Your Live Dashboard**: https://quant-p1.onrender.com

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Dashboard Overview](#dashboard-overview)
3. [Live Simulation Guide](#live-simulation-guide)
4. [Strategy Comparison](#strategy-comparison)
5. [Deep Analysis](#deep-analysis)
6. [Understanding Metrics](#understanding-metrics)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Step 1: Access the Dashboard

Go to: **https://quant-p1.onrender.com**

⏳ **First visit?** The app may take 30-60 seconds to wake up (free tier spins down after inactivity).

### Step 2: Choose a Mode

The sidebar shows 4 modes:
- 🔴 **Live Simulation** - Run single strategy simulations
- 📊 **Strategy Comparison** - Compare multiple strategies
- 🔬 **Deep Analysis** - Detailed performance analytics
- 📈 **Portfolio View** - Multi-strategy portfolios (coming soon)

### Step 3: Configure & Run

1. Select your desired agent/strategy
2. Adjust market parameters (duration, volatility, etc.)
3. Click the **Run** button
4. Wait for simulation to complete
5. Explore the results!

---

## 🖥️ Dashboard Overview

### Main Components

```
┌─────────────────────────────────────────────────────┐
│  📊 Adaptive Liquidity Provision Analytics Platform │
│                                                     │
│  ┌──────────┐  ┌────────────────────────────────┐  │
│  │ SIDEBAR  │  │     MAIN CONTENT AREA         │  │
│  │          │  │                                │  │
│  │ • Mode   │  │  • KPI Dashboard               │  │
│  │ • Config │  │  • Performance Charts          │  │
│  │ • Params │  │  • Risk Metrics                │  │
│  │          │  │  • Trade Analysis              │  │
│  └──────────┘  └────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### System Status

Top-right corner shows:
- ✅ **Online** - System ready
- **Last Updated** - Current timestamp

---

## 🔴 Live Simulation Guide

### Purpose
Run a single market making strategy and analyze its performance in real-time.

### Step-by-Step

#### 1. Select Dashboard Mode
- Click sidebar dropdown
- Select: **"🔴 Live Simulation"**

#### 2. Choose Agent Type

Available agents:
- **Avellaneda-Stoikov** ⭐ RECOMMENDED FOR BEGINNERS
  - Academic optimal control strategy
  - Balances inventory risk and profit
  - Good baseline performance
  
- **Static Spread**
  - Fixed bid-ask spread
  - Simple, predictable
  - Good for stable markets
  
- **Adaptive Spread**
  - Adjusts to market volatility
  - More sophisticated
  - Better in dynamic markets
  
- **Random**
  - Baseline comparison
  - Random quote placement
  - Shows value of smarter strategies

**💡 TIP**: Start with **Avellaneda-Stoikov** to see optimal performance!

#### 3. Configure Market Parameters

**Duration (seconds)**:
- Range: 10 - 500 seconds
- Default: 100 seconds
- **Recommendation**: Start with 50-100 seconds
- Longer = more trades, more statistical significance
- Shorter = faster results

**Volatility**:
- Range: 0.01 - 0.10
- Default: 0.02
- Low (0.01-0.03): Calm market
- Medium (0.03-0.05): Normal conditions
- High (0.05-0.10): Volatile market
- **💡 TIP**: Try 0.02 first (realistic conditions)

**Initial Price ($)**:
- Range: $50 - $200
- Default: $100
- Doesn't significantly affect strategy performance
- Higher prices → larger absolute P&L (but same % returns)

#### 4. Run Simulation

Click **"Run Simulation"** button

**What happens**:
1. ⏳ Simulation starts (may take 10-30 seconds)
2. 📊 Progress indicator appears
3. ✅ Results display when complete

**⏱️ Expected time**:
- 50s duration → ~15 seconds to run
- 100s duration → ~20-25 seconds to run
- 200s duration → ~40-50 seconds to run

#### 5. Understanding Results

After simulation completes, you'll see:

**A. Key Performance Indicators (KPIs)**

Five boxes showing:

1. **Total P&L**
   - Total profit/loss in dollars
   - ✅ Green if positive
   - ❌ Red if negative
   - **Good**: > $1,000
   - **Excellent**: > $2,000

2. **Sharpe Ratio**
   - Risk-adjusted returns
   - Higher is better
   - **Good**: > 0.8
   - **Excellent**: > 1.2
   - **Random agent**: ~0.05

3. **Max Drawdown**
   - Largest peak-to-trough decline
   - Lower is better
   - **Good**: < 10%
   - **Excellent**: < 6%
   - **Warning**: > 15%

4. **Win Rate**
   - % of profitable trades
   - **Good**: > 55%
   - **Excellent**: > 60%
   - Random: ~50%

5. **Fill Ratio**
   - % of quotes that got filled
   - Shows market making activity
   - **Good**: 30-50%
   - **Too high**: May be too aggressive
   - **Too low**: Quotes too far from market

**B. Performance Charts**

**P&L Curve**:
- Shows cumulative profit over time
- Smooth upward = consistent profit
- Volatile = high risk
- Downward trending = losing money

**Inventory Path**:
- Shows position size over time
- Should oscillate around zero
- Excessive inventory = high risk
- Good strategies keep |inventory| < 300

**Order Book Snapshot**:
- Shows final state of limit order book
- Bids (green) vs Asks (red)
- Your quotes vs market orders

**C. Detailed Metrics Table**

Shows all performance metrics:
- Returns (total, annualized)
- Risk metrics (volatility, VaR, CVaR)
- Trading statistics
- Execution quality

---

## 📊 Strategy Comparison

### Purpose
Compare multiple market making strategies side-by-side to see which performs best.

### Step-by-Step

#### 1. Select Mode
- Sidebar → **"📊 Strategy Comparison"**

#### 2. Configure Settings

**Number of Episodes**:
- Range: 1-50
- Default: 10
- More episodes = more robust comparison
- **Recommendation**: 10-20 episodes

**Episode Duration**:
- Same as Live Simulation
- **Recommendation**: 50-100 seconds per episode

**Strategies to Compare**:
- Check boxes for agents you want to compare
- **Recommendation**: Compare all 4 to see differences

#### 3. Run Comparison

Click **"Run Comparison"** button

**⏱️ Expected time**:
- 4 agents × 10 episodes × 50s = ~8-10 minutes
- Progress bar shows status

#### 4. Understanding Results

**A. Performance Metrics Table**

Compares agents across:
- Total P&L (average across episodes)
- Sharpe Ratio
- Max Drawdown
- Win Rate
- Fill Ratio
- Volatility

**How to read**:
- Green highlight = best performer
- Red highlight = worst performer
- Sort by clicking column headers

**B. Comparison Charts**

**P&L Distribution**:
- Box plots showing P&L spread
- Wider box = more variable
- Higher median = better average performance

**Sharpe Ratio Comparison**:
- Bar chart of risk-adjusted returns
- Taller = better

**Risk vs Return**:
- Scatter plot
- Upper-right = best (high return, low risk)
- Lower-left = worst

**C. Statistical Significance**

Table shows if differences are statistically significant:
- ✅ = significant difference
- ❌ = not significant (could be luck)

---

## 🔬 Deep Analysis

### Purpose
Perform comprehensive analysis of a single strategy with advanced metrics.

### Step-by-Step

#### 1. Select Mode
- Sidebar → **"🔬 Deep Analysis"**

#### 2. Select Strategy
- Choose one agent for deep dive
- **Recommendation**: Start with Avellaneda-Stoikov

#### 3. Run Analysis

Runs 20 episodes automatically to gather statistical data.

**⏱️ Time**: 3-5 minutes

#### 4. Understanding Results

**A. Summary Statistics**

- Mean performance across episodes
- Standard deviation (consistency)
- Best and worst episode
- Confidence intervals

**B. Risk Analytics**

**Value at Risk (VaR)**:
- 95% VaR: Expected worst loss in 95% of cases
- Example: VaR = -$500 means 95% of time you won't lose more than $500

**Conditional VaR (CVaR)**:
- Average loss in worst 5% of cases
- More conservative risk measure

**Sortino Ratio**:
- Like Sharpe but only penalizes downside volatility
- Higher is better

**C. Trade Analysis**

**Trade Size Distribution**:
- Shows histogram of trade sizes
- Should be centered around mean order size
- Long tails = occasional large trades

**Hold Time Analysis**:
- How long positions are held
- Shorter = more active trading
- Longer = more passive

**P&L per Trade**:
- Distribution of individual trade profitability
- Should be centered slightly positive

**D. Advanced Metrics**

- Profit Factor (gross profit / gross loss)
- Recovery Factor (total return / max drawdown)
- Calmar Ratio (return / max drawdown)
- Omega Ratio (probability-weighted ratio)

---

## 📊 Understanding Metrics

### Performance Metrics

**Total P&L**
- Sum of all profits and losses
- Measured in dollars
- Higher is better
- Typical range: -$500 to +$5,000

**Returns (%)**
- P&L as percentage of capital
- Annualized for comparison
- Good: > 20% annually

**Sharpe Ratio**
- Risk-adjusted returns
- (Return - Risk-free rate) / Volatility
- **Interpretation**:
  - < 0: Losing money
  - 0-0.5: Poor
  - 0.5-1.0: Acceptable
  - 1.0-2.0: Good
  - > 2.0: Excellent

**Sortino Ratio**
- Like Sharpe but better
- Only penalizes downside volatility
- Generally higher than Sharpe
- Same interpretation scale

### Risk Metrics

**Max Drawdown**
- Largest peak-to-trough decline
- Percentage of portfolio
- **Interpretation**:
  - < 5%: Very low risk
  - 5-10%: Low risk
  - 10-20%: Moderate risk
  - > 20%: High risk

**Volatility**
- Standard deviation of returns
- Annualized percentage
- Lower is more stable
- Typical: 10-30%

**VaR (Value at Risk)**
- Expected worst loss at confidence level
- Usually 95% or 99%
- Example: 95% VaR = -$500 means 95% of time loss won't exceed $500

**CVaR (Conditional VaR)**
- Average loss beyond VaR threshold
- "Expected Shortfall"
- More conservative than VaR

### Trading Metrics

**Win Rate**
- % of profitable trades
- 50% = break-even
- > 55% = good
- Market making typically 50-60%

**Fill Ratio**
- % of quotes that execute
- Too high (>70%): Quotes too aggressive, adverse selection
- Too low (<20%): Quotes too passive, missing opportunities
- Optimal: 30-50%

**Average Inventory**
- Mean absolute position size
- Should be low for market makers
- High inventory = high risk
- Target: < 200 shares

**Profit Factor**
- Gross profit / Gross loss
- > 1.0 = profitable overall
- > 1.5 = good
- > 2.0 = excellent

---

## 💡 Best Practices

### 1. Starting Out

**First Time Users**:
1. Go to **Live Simulation**
2. Select **Avellaneda-Stoikov**
3. Use default parameters (100s, 0.02 volatility)
4. Click **Run Simulation**
5. Study the results

### 2. Comparing Strategies

**To find best strategy**:
1. Go to **Strategy Comparison**
2. Select all 4 agents
3. Run 10 episodes
4. Compare Sharpe Ratios
5. Check consistency (lower std dev is better)

### 3. Understanding Market Conditions

**Test different volatilities**:
- Run same agent at vol = 0.01, 0.03, 0.05
- See how performance changes
- Some strategies better in calm/volatile markets

### 4. Statistical Significance

**Run enough episodes**:
- Single episode can be lucky/unlucky
- 10+ episodes for reliable comparison
- 20+ episodes for deep analysis

### 5. Interpreting Results

**Look for**:
- ✅ Consistent positive P&L
- ✅ Sharpe ratio > 1.0
- ✅ Max drawdown < 10%
- ✅ Inventory mean near zero

**Red flags**:
- ❌ Highly volatile P&L
- ❌ Large max drawdown (>15%)
- ❌ Consistent inventory buildup
- ❌ Win rate < 45%

---

## 🎓 Advanced Usage

### Custom Scenarios

**High Volatility Stress Test**:
- Set volatility = 0.08-0.10
- See which strategies handle it best
- Avellaneda-Stoikov usually adapts well

**Long Duration Test**:
- Set duration = 200-500 seconds
- More realistic trading day
- Better statistical significance

**Price Level Comparison**:
- Run same setup at $50, $100, $200
- Verify strategy works across price ranges

### Performance Optimization

**Finding Optimal Parameters**:
1. Run strategy comparison
2. Note best performer
3. Run deep analysis on winner
4. Study when it performs best/worst

### Risk Management

**Monitor These**:
- Max drawdown < 10%
- VaR within acceptable range
- Inventory doesn't spiral
- Consistent win rate

---

## 🔧 Troubleshooting

### Dashboard Issues

**Problem**: Page won't load  
**Solution**: Wait 30-60 seconds (free tier wake-up time)

**Problem**: KPIs not showing  
**Solution**: 
- Wait for simulation to complete
- Check progress indicator
- If stuck, refresh page

**Problem**: Buttons not responding  
**Solution**:
- Refresh browser
- Check internet connection
- Try different browser (Chrome recommended)

**Problem**: Icons/emojis not visible  
**Solution**:
- Browser compatibility issue
- Update browser
- Functionality not affected

### Simulation Issues

**Problem**: Simulation taking too long  
**Solution**:
- Reduce duration (try 50s instead of 200s)
- Reduce number of episodes
- Free tier has limited resources

**Problem**: Error messages  
**Solution**:
- Check parameter ranges
- Try default values
- Refresh and retry

**Problem**: Results look wrong  
**Solution**:
- Verify parameters are realistic
- Try with default settings
- Compare with other strategies

### Performance Issues

**Problem**: Slow response  
**Solution**:
- Free tier spins down after 15min
- First request takes time to wake up
- Subsequent requests are faster

**Problem**: App crashed  
**Solution**:
- Refresh page
- Wait for restart (30-60 seconds)
- Try simpler parameters

---

## 📚 Learning Path

### Beginner (Day 1)
1. Read this manual (Quick Start section)
2. Run Live Simulation with defaults
3. Try each agent type once
4. Understand KPI dashboard

### Intermediate (Week 1)
1. Run Strategy Comparison
2. Try different market conditions
3. Understand all metrics
4. Read technical documentation

### Advanced (Month 1)
1. Run Deep Analysis
2. Test custom scenarios
3. Analyze statistical significance
4. Optimize strategies

---

## 🎯 What You Can Achieve

### Learning Outcomes

After using this platform, you'll understand:
- ✅ How market making works
- ✅ Risk vs return tradeoffs
- ✅ Different market making strategies
- ✅ Performance evaluation metrics
- ✅ Statistical analysis of trading strategies

### Practical Applications

**For Students**:
- Learn quantitative finance
- Understand algorithmic trading
- Practice data analysis
- Portfolio projects

**For Researchers**:
- Test new strategies
- Benchmark performance
- Analyze market microstructure
- Publish findings

**For Traders**:
- Understand market making
- Evaluate strategy ideas
- Risk management insights
- Strategy optimization

**For Developers**:
- Study RL applications
- Learn production ML systems
- Understand financial systems
- Build similar platforms

---

## 📖 Related Documentation

- **Technical Overview**: `docs/TECHNICAL_OVERVIEW.md`
- **Research Paper**: `docs/RESEARCH_PAPER_TEMPLATE.md`
- **API Documentation**: `docs/API.md`
- **Deployment Guide**: `RENDER_DEPLOY_GUIDE.md`

---

## 💬 Support

**Questions?**
- Check this manual first
- Read technical documentation
- Open GitHub issue

**Found a Bug?**
- Note the error message
- List steps to reproduce
- Report on GitHub

**Feature Request?**
- Describe the feature
- Explain use case
- Submit GitHub issue

---

## 📄 License

MIT License - Free to use, modify, and distribute

---

## 🎉 Enjoy!

You now have access to a professional market making analytics platform!

**Start exploring**: https://quant-p1.onrender.com

Happy trading! 📈🚀

---

**Last Updated**: October 2025  
**Version**: 1.0.0  
**Platform**: Streamlit + Render
