# 🔧 Troubleshooting Guide

## 🐛 Common Issues & Solutions

---

## Issue 1: KPIs Show All Zeros

### Symptoms:
```
Total P&L: $0.00
Sharpe Ratio: 0.000
Max Drawdown: 0.00%
Win Rate: 0.0%
Avg Inventory: (blank)
```

### Diagnosis:

**Step 1**: Look for error messages
- Red error box? → Go to "Error Messages" section below
- Yellow warning? → See what it says

**Step 2**: Click "📊 Simulation Details" (expandable section at bottom)

Check these values:

| Value | What It Means | Action |
|-------|---------------|--------|
| **Steps = 0 or 1** | Environment not running | See "Environment Issues" below |
| **Steps > 100, Trades = 0** | Strategy not executing | See "Strategy Issues" below |
| **Steps > 100, Trades > 0, P&L = 0** | Unusual but possible | Try different parameters |

### Solutions:

#### If Steps = 0 or 1:
```
Environment configuration issue
```

**Fix**:
1. Refresh the page
2. Use default parameters
3. Try shorter duration (50s)
4. If persists, check Render logs

#### If Trades = 0:
```
Strategy not placing orders
```

**Fix**:
1. Try different agent (Avellaneda-Stoikov recommended)
2. Increase volatility (try 0.03-0.05)
3. Increase duration (try 200s)
4. Check if agent is properly initialized

#### If P&L = 0 despite trades:
```
Trades executing at zero profit
```

**Possible causes**:
- All trades matched at mid-price (rare)
- Transaction costs offsetting gains
- Very short simulation

**Fix**:
- Run longer simulation (200s+)
- Try different volatility
- Compare with other agents

---

## Issue 2: "Simulation Produced No Data"

### Error Message:
```
⚠️ Simulation produced no data. This might be a configuration issue.
```

### Causes:
1. Environment failed to initialize
2. Configuration parameters invalid
3. Memory issue (Render free tier limit)

### Solutions:

**Try These (in order)**:

1. **Refresh page** and try again
   ```
   Sometimes Streamlit state gets confused
   ```

2. **Use default parameters**
   - Duration: 100s
   - Volatility: 0.02
   - Initial Price: $100

3. **Try shorter duration**
   - Start with 50s
   - Gradually increase

4. **Check Render logs**
   - Go to https://dashboard.render.com/
   - Click your service → "Logs"
   - Look for Python errors

5. **Redeploy**
   ```bash
   git push
   # Wait for rebuild
   ```

---

## Issue 3: Page Won't Load

### Symptoms:
- Blank page
- "Application Error"
- Infinite loading

### Causes:
1. **Free tier sleeping** (most common)
2. Build failed
3. Out of memory
4. Port binding issue

### Solutions:

#### A. Free Tier Wake-Up:
```
Wait 30-60 seconds
Refresh browser once
App should load
```

This is **NORMAL** for free tier!

#### B. Check Render Status:
1. Go to https://dashboard.render.com/
2. Check service status
3. Look at "Events" tab

#### C. Check Logs:
1. Click "Logs" tab
2. Look for:
   - "Your service is live 🎉" → Good!
   - Python errors → Need to fix
   - "Out of memory" → Need optimization

#### D. Rebuild:
```bash
# Force rebuild
git commit --allow-empty -m "Trigger rebuild"
git push
```

---

## Issue 4: Simulation Taking Too Long

### Symptoms:
- Spinning for > 2 minutes
- Browser tab frozen
- No progress

### Causes:
1. Long duration parameter
2. Complex simulation
3. Server overloaded

### Solutions:

**Immediate**:
- **Don't refresh!** Wait a bit longer
- Long simulations (200s+) can take 1-2 minutes
- Check if progress spinner is moving

**Prevention**:
- Start with shorter durations (50-100s)
- Free tier is slower than paid
- Run during off-peak hours

**If Stuck**:
1. Wait 3 minutes total
2. If still stuck, refresh page
3. Try shorter duration (50s)
4. Try simpler agent (Static Spread)

---

## Issue 5: Icons/Emojis Not Showing

### Symptoms:
- Boxes instead of emojis
- Missing icons in buttons
- Strange characters

### Cause:
Browser emoji support varies

### Solution:
**This is cosmetic only!**

- ✅ All functionality works fine
- Use Chrome for best experience
- Or ignore it - doesn't affect results

---

## Issue 6: "Error During Simulation"

### Red error box appears with message

### Steps:

1. **Read the error message carefully**

2. **Click "🐛 Technical Details"** to see full stack trace

3. **Common errors**:

   | Error | Meaning | Fix |
   |-------|---------|-----|
   | `ModuleNotFoundError` | Missing package | Add to requirements.txt |
   | `MemoryError` | Out of RAM | Reduce duration or episodes |
   | `ValueError: ...` | Invalid parameter | Check parameter ranges |
   | `KeyError: ...` | Missing data | Environment config issue |

4. **Try**:
   - Refresh and use defaults
   - Check if issue persists
   - Copy error for support

---

## Issue 7: Charts Not Displaying

### Symptoms:
- KPIs show but no charts
- Empty chart areas
- "Error loading chart"

### Solutions:

1. **Scroll down** - charts are below KPIs
2. **Wait** - they load after KPIs
3. **Check browser console** (F12)
4. **Try different browser**
5. **Refresh page**

---

## Issue 8: Strategy Comparison Stuck

### Symptoms:
- Progress bar not moving
- Taking > 10 minutes
- No results

### Causes:
- Multiple agents × multiple episodes = long time
- 4 agents × 20 episodes × 100s = ~10 minutes!

### Solutions:

**Reduce complexity**:
- Fewer episodes (start with 5)
- Shorter duration (50s)
- Fewer agents (compare 2 at a time)

**Be patient**:
- Check progress bar
- Don't refresh if moving
- Free tier is slower

---

## 🔍 Debugging Tips

### Enable Debug Mode:

1. **Check "Simulation Details"** expandable section
   - Shows steps, trades, P&L
   - First place to look!

2. **Check "Technical Details"** if error
   - Shows full stack trace
   - Helps identify exact issue

3. **Check Render Logs**
   - Most detailed information
   - Shows all print statements
   - See errors before crash

### Useful Debug Commands:

**Local Testing**:
```bash
# Run locally with debug output
streamlit run app.py --logger.level=debug
```

**Check Render Logs**:
```bash
# Or via dashboard
https://dashboard.render.com/ → Your Service → Logs
```

---

## 🆘 Still Stuck?

### Gather This Information:

1. **What you see**:
   - Screenshot of dashboard
   - Error messages (full text)
   - Debug info from expandable section

2. **What you did**:
   - Steps to reproduce
   - Parameter values used
   - Browser and version

3. **Logs**:
   - Render logs (last 50 lines)
   - Browser console (F12 → Console)
   - Any error stack traces

### Where to Get Help:

1. **Check this guide first**
2. **Read USER_MANUAL.md**
3. **Check QUICK_START_GUIDE.md**
4. **Open GitHub issue with details above**

---

## ✅ Prevention Checklist

Before reporting issues, verify:

- [ ] Used default parameters
- [ ] Waited 30-60 seconds for wake-up
- [ ] Waited 20-30 seconds for simulation
- [ ] Checked "Simulation Details" section
- [ ] Refreshed page once
- [ ] Tried different browser
- [ ] Checked Render logs
- [ ] Read relevant documentation

---

## 🎯 Quick Reference

| Problem | Quick Fix |
|---------|-----------|
| All zeros | Check "Simulation Details" → See Issue 1 |
| Won't load | Wait 60 seconds → See Issue 3 |
| Too slow | Reduce duration → See Issue 4 |
| No icons | Ignore (cosmetic) → See Issue 5 |
| Error message | Read it + check Technical Details → See Issue 6 |
| No charts | Scroll down + wait → See Issue 7 |

---

**Most issues are solved by: Refresh + Default Parameters + Wait!** 🎯
