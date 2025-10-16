# 🚀 Quick Start Guide - 5 Minutes to Your First Results

## 📍 Your Dashboard

**Live URL**: https://quant-p1.onrender.com

---

## ⚡ Get Results in 3 Steps

### Step 1: Access Dashboard (30 seconds)

1. Go to: https://quant-p1.onrender.com
2. **⏳ Wait 30-60 seconds** if it's sleeping (free tier)
3. You'll see the main dashboard load

---

### Step 2: Configure (30 seconds)

**On the left sidebar**:

1. **Dashboard Mode**: Select "🔴 Live Simulation"

2. **Agent Type**: Select "Avellaneda-Stoikov"  
   *(This is the best strategy to start with)*

3. **Market Parameters**:
   - Duration: **100** seconds *(leave default)*
   - Volatility: **0.02** *(leave default)*
   - Initial Price: **$100** *(leave default)*

---

### Step 3: Run & Wait (2-3 minutes)

1. Click the big **"Run Simulation"** button

2. **⏳ WAIT** - You'll see:
   ```
   Running simulation...
   ⏳ Please wait (this may take 20-30 seconds)...
   ```

3. **DO NOT REFRESH** the page while it's running!

4. After 20-30 seconds, results will appear:
   - ✅ 5 KPI boxes at the top
   - ✅ Charts showing performance
   - ✅ Detailed metrics table

---

## 📊 Understanding Your Results

### The 5 KPI Boxes

After simulation completes, you'll see **5 colored boxes**:

```
┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│  Total P&L  │   Sharpe    │   Max DD    │  Win Rate   │ Avg Inv     │
│   $2,450    │    1.35     │    8.2%     │    57%      │    145      │
│   (GREEN)   │   (GREEN)   │   (GREEN)   │  (YELLOW)   │   (GREEN)   │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
```

**What they mean**:

1. **Total P&L** ($2,450)
   - Your total profit
   - ✅ GREEN = making money
   - ❌ RED = losing money

2. **Sharpe Ratio** (1.35)
   - Risk-adjusted return
   - ✅ > 1.0 = Good
   - ⭐ > 1.2 = Excellent
   - ❌ < 0.5 = Poor

3. **Max Drawdown** (8.2%)
   - Biggest loss from peak
   - ✅ < 10% = Low risk
   - ⚠️ > 15% = High risk

4. **Win Rate** (57%)
   - % of profitable trades
   - ✅ > 55% = Good
   - ⚠️ < 50% = Needs work

5. **Avg Inventory** (145)
   - Average position size
   - ✅ < 200 = Well controlled
   - ⚠️ > 400 = Too risky

---

## 🎨 The Charts

### 1. P&L Curve (Top Left)
Shows your profit over time:
- 📈 Going up = Making money
- 📉 Going down = Losing money
- Smooth = Consistent
- Zigzag = Volatile

### 2. Inventory Path (Top Right)
Shows your position over time:
- Should zigzag around zero
- Too high/low for too long = risky
- Good strategies keep it balanced

### 3. Order Book (Bottom Left)
Final state of the market:
- Green bars = Buy orders
- Red bars = Sell orders
- Your quotes vs market orders

### 4. Key Metrics Table (Bottom Right)
All the numbers:
- Returns %
- Risk metrics
- Trading stats

---

## ✅ Success Checklist

After your first simulation, you should see:

- [ ] 5 KPI boxes with numbers (not blank!)
- [ ] P&L curve chart
- [ ] Inventory chart
- [ ] Metrics table with data
- [ ] No error messages

**If KPIs are blank**: You didn't wait long enough! The simulation is still running.

---

## 🎯 Try This Next

### Experiment #1: Compare Strategies

1. **Change Mode** → "📊 Strategy Comparison"
2. **Check all 4 agents**
3. **Episodes**: 5
4. **Click "Run Comparison"**
5. **Wait 3-4 minutes**
6. See which strategy wins!

**Expected Results**:
- Avellaneda-Stoikov: Usually best
- Adaptive Spread: Close second
- Static Spread: Decent
- Random: Worst (baseline)

### Experiment #2: Test Volatility

Run same agent (Avellaneda-Stoikov) with different volatilities:

1. **Vol = 0.01** (calm market)
2. **Vol = 0.03** (normal)
3. **Vol = 0.07** (volatile)

**Watch how**:
- P&L changes
- Sharpe ratio changes
- Drawdown increases with volatility

### Experiment #3: Long Simulation

1. **Duration = 200 seconds**
2. **Run simulation**
3. **Wait ~45 seconds**
4. More trades = better statistics!

---

## ⚠️ Common Issues & Fixes

### Issue 1: "KPIs Not Showing"

**Cause**: Simulation still running!

**Fix**: 
- Look for "Running simulation..." message
- WAIT for it to complete
- Usually 20-30 seconds
- Don't refresh the page!

### Issue 2: "Page Won't Load"

**Cause**: Free tier is waking up

**Fix**:
- Wait 30-60 seconds
- Refresh once if needed
- Should load

### Issue 3: "Icons Not Showing"

**Cause**: Browser compatibility

**Fix**:
- Update your browser
- Try Chrome (best support)
- Doesn't affect functionality!

### Issue 4: "Simulation Stuck"

**Cause**: Network issue or timeout

**Fix**:
- Refresh the page
- Try shorter duration (50s)
- Check internet connection

---

## 💡 Pro Tips

### Tip 1: Start Simple
- Use default parameters first
- Understand one agent before comparing
- Read results carefully

### Tip 2: Be Patient
- Simulations take time (20-60 seconds)
- Don't refresh while running
- Longer duration = longer wait

### Tip 3: Compare Fairly
- Use same parameters for all agents
- Run multiple episodes (10+)
- Check statistical significance

### Tip 4: Learn Gradually
- Day 1: Run one simulation
- Day 2: Compare strategies
- Week 1: Deep analysis
- Month 1: Custom experiments

---

## 📚 Next Steps

### Learn More
- **Full Manual**: `docs/USER_MANUAL.md`
- **Technical Docs**: `docs/TECHNICAL_OVERVIEW.md`
- **Research Paper**: `docs/RESEARCH_PAPER_TEMPLATE.md`

### Get Help
- Check USER_MANUAL.md FAQ section
- Review troubleshooting guide
- Open GitHub issue if stuck

---

## 🎉 You're Ready!

**Go to**: https://quant-p1.onrender.com

**Follow**: Steps 1-2-3 above

**First run**: Use default settings

**Have fun** exploring market making strategies!

---

**Need help? Read `docs/USER_MANUAL.md` for complete guide!**

**Questions? The manual has a troubleshooting section!**

---

**Total Time**: 5 minutes for first results ⏱️  
**Difficulty**: Beginner-friendly ⭐  
**Cost**: FREE 💰

**Happy Trading!** 📈🚀
