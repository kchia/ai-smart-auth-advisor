# Time Usage Metrics

**Parable's Mission:** Help CEOs gain organizational observability to answer "Where is the time waste?"

SSO data reveals **quantifiable productivity loss** in multiple dimensions. Here's how to calculate time waste from this data:

---

## ⚠️ **CRITICAL: Data Requirements for These Metrics**

**This document describes a production framework** for calculating time waste from SSO data at Parable scale (petabytes, days/weeks of data per user).

**Current Sample Dataset Limitations:**

- **18 events** across 10 users
- **13-second time window** (2025-04-01 15:38:07 to 15:38:20)
- **Cannot compute most metrics below** - they require full daily/weekly coverage

**What We CAN Analyze from Sample:**

- ✅ Authentication step distribution (range, average, per-user patterns)
- ✅ User segmentation by app diversity (power vs casual users in snapshot)
- ✅ App co-occurrence patterns (which apps accessed together)

**What We CANNOT Compute from Sample:**

- ❌ Daily authentication frequency (need full day, not 13 seconds)
- ❌ Context switching behavior (need hours/days, not seconds)
- ❌ Focus time / dwell time (need session-level data over time)
- ❌ Idle time gaps (need multi-hour coverage)
- ❌ Any productivity waste calculations assuming daily patterns

**In Production:** With full SSO data spanning days/weeks, ALL metrics below become computable and meaningful.

---

### **1. Authentication Time Waste**

**Problem:** Higher authentication steps = more time spent authenticating instead of working.

**⚠️ Sample Data Status:** We CAN measure auth step distribution (1-9 range, avg 5.6) but CANNOT compute daily/weekly time waste without full day of data showing authentication frequency.

**Formula (Production):**

```
Time per auth = base_time + (authenticationStep - 1) × step_overhead
Where:
  base_time = 30 seconds (simple password)
  step_overhead = 30 seconds per additional step (MFA, challenges, etc.)
```

**Example Calculation:**

- User with `authenticationStep = 1`: 30 seconds
- User with `authenticationStep = 8`: 30 + (7 × 30) = 240 seconds = 4 minutes
- **Time waste:** 3.5 minutes per authentication

**Daily Impact:**

- User accesses 20 apps/day
- Step 8 user: 20 × 4 min = 80 min/day authenticating
- Step 1 user: 20 × 0.5 min = 10 min/day authenticating
- **Daily waste:** 70 minutes = 1.2 hours/day

**Weekly Impact:**

- 70 min/day × 5 days = **5.8 hours/week** lost to excessive authentication
- **Cost:** At $50/hr average salary = $290/week = $15,080/year per employee
- **Organization:** 1,000 employees with step 8 = **$15M/year in wasted time**

**How to Calculate from Data (Production):**

```sql
-- Requires: Full day of SSO events to get accurate daily_auths count
SELECT
    actor.id,
    AVG(authenticationContext.authenticationStep) as avg_auth_step,
    COUNT(*) as daily_auths,  -- ⚠️ Only accurate with full day of data
    -- Time waste calculation
    (AVG(authenticationContext.authenticationStep) - 1) * 0.5 * COUNT(*) as daily_minutes_wasted,
    -- Weekly/yearly extrapolation
    daily_minutes_wasted * 5 / 60 as weekly_hours_wasted,
    weekly_hours_wasted * 50 * 50 as annual_cost_per_employee
FROM events
WHERE DATE(published) = '2025-04-01'  -- Filter to single full day
GROUP BY actor.id
ORDER BY daily_minutes_wasted DESC
```

**What We CAN Compute from Sample (18 events, 13 seconds):**

- Auth step distribution: range 1-9, average 5.6, most common step 8 (33%)
- Per-user patterns: User "mco laboris nisi ut" consistently faces step 9
- Step variability: Wide range indicates friction opportunities

**What We CANNOT Compute from Sample:**

- Daily authentication frequency (need full day, not 13 seconds)
- Time waste calculations (depend on daily_auths which we don't have)
- Weekly/annual cost projections (require daily baseline)

---

### **2. Context Switching Time Tax**

**Problem:** Every app switch requires cognitive reload time - mental context must shift.

**⚠️ Sample Data Status:** CANNOT compute from 13-second sample. Context switching measurement requires observing user behavior over hours/days, not seconds. We can see app diversity (2 apps vs 0-1) but cannot infer switching patterns or frequency.

**Research (Production Context):** Studies show context switching costs 5-23 minutes of focused time per switch (average: 15 minutes for deep work tasks, 5 minutes for shallow tasks).

**Formula:**

```
Context switch tax = app_switches × cognitive_reload_time
Where:
  cognitive_reload_time = 5 minutes (conservative estimate for shallow work)
  cognitive_reload_time = 15 minutes (for deep work requiring focus)
```

**Example Calculation (Production Context - NOT from 13-second sample):**

⚠️ The calculations below require full-day production data to be meaningful. Our 13-second sample cannot measure context switching behavior.

**Hypothetical Production Scenario:**

- User switches apps 47 times/day (requires observing full workday)
- Conservative: 47 × 5 min = 235 min = **3.9 hours/day wasted**
- Deep work: 47 × 15 min = 705 min = **11.8 hours/day wasted** (impossible - indicates zero productive work!)

**Weekly Impact (Production):**

- 3.9 hrs/day × 5 days = **19.5 hours/week** lost to context switching
- Nearly **50% of work time** spent on cognitive reload

**How to Calculate from Data (Production - Requires Full Day):**

⚠️ This query requires full-day production data. With our 13-second sample, app_switches would be meaningless (max 1-2 switches observed).

```sql
-- Requires: Full day of SSO events to measure actual switching patterns
SELECT
    actor.id,
    COUNT(DISTINCT target[].id) as unique_apps_accessed,
    COUNT(*) as total_events,
    -- ⚠️ Assumes events spread over 8-hour workday (NOT 13 seconds!)
    CASE
        WHEN total_events > 1 THEN total_events - 1  -- N events = N-1 switches
        ELSE 0
    END as app_switches,
    -- Time waste (conservative)
    app_switches * 5 as minutes_wasted_conservative,
    app_switches * 15 as minutes_wasted_deep_work,
    -- Daily hours
    minutes_wasted_conservative / 60.0 as hours_wasted_per_day
FROM events
WHERE target IS NOT EMPTY  -- Only count app access events
  AND DATE(published) = '2025-04-01'  -- Filter to single full day
GROUP BY actor.id
ORDER BY hours_wasted_per_day DESC
```

**⚠️ CRITICAL CORRECTION - Velocity Flag:**
The `debugContext.debugData.logOnlySecurityData.behaviors.Velocity` flag is a **SECURITY feature**, NOT a productivity metric. It detects **impossible geographic travel** (e.g., NY login → London login 30 min later, traveling > 805 km/h). High prevalence (67% in sample) likely indicates VPN usage, mobile access, or legitimate travel - NOT context switching behavior.

**For actual context switching measurement:** Use time gaps between app accesses (published timestamps) and distinct target.id transitions over hours/days.

---

### **3. App Dwell Time (Focus Metric)**

**Problem:** Short dwell times indicate lack of focus or tool frustration.

**Definition:** Time between first and last access to the same app within a session.

**Formula:**

```
Dwell time = MAX(published) - MIN(published) for same target.id in same session
```

**Interpretation:**

- **< 5 minutes:** Quick check, minimal focus (email glance, Slack ping)
- **5-30 minutes:** Shallow work (responding to messages, light tasks)
- **30-120 minutes:** Focused work session (writing, coding, analysis)
- **> 120 minutes:** Deep work session (major projects, complex tasks)

**Productivity Insight:**

- Users with mostly < 5 min dwell times are **fragmented** - lots of interruptions
- Users with > 60 min dwell times are **focused** - able to maintain concentration

**How to Calculate from Data:**

```sql
WITH app_sessions AS (
    SELECT
        actor.id,
        target[].id as app_id,
        authenticationContext.rootSessionId as session_id,
        MIN(published) as first_access,
        MAX(published) as last_access,
        TIMESTAMP_DIFF(MAX(published), MIN(published), MINUTE) as dwell_minutes
    FROM events
    WHERE target IS NOT EMPTY
    GROUP BY actor.id, app_id, session_id
)
SELECT
    actor.id,
    AVG(dwell_minutes) as avg_dwell_minutes,
    SUM(CASE WHEN dwell_minutes < 5 THEN 1 ELSE 0 END) as fragmented_sessions,
    SUM(CASE WHEN dwell_minutes > 60 THEN 1 ELSE 0 END) as focused_sessions,
    -- Focus score
    focused_sessions / (focused_sessions + fragmented_sessions) as focus_ratio
FROM app_sessions
GROUP BY actor.id
ORDER BY focus_ratio DESC
```

**Note:** With only 18 events in sample data, dwell time calculations are not meaningful. Need full day/week of data.

---

### **4. Idle Time Detection**

**Problem:** Large gaps between SSO events may indicate blockers or unproductive time.

**Definition:** Time gaps > 4 hours between consecutive SSO events (excluding nights/weekends).

**Formula:**

```
Idle time = gap between consecutive published timestamps where gap > 240 minutes during work hours
```

**Interpretation:**

- **< 30 min gaps:** Normal work rhythm
- **30-60 min gaps:** Meetings, lunch, breaks (expected)
- **60-240 min gaps:** Long meetings, blocked work, context loss
- **> 240 min gaps:** Potential idle time, blocked on dependencies, or tools not captured in SSO

**Productivity Insight:**

- Frequent long gaps suggest blockers, inefficient meetings, or missing tool coverage
- Could indicate "waiting time" - employee blocked by dependencies

**Limitation:** SSO data only captures tool access, not meetings, phone calls, or offline work. Gaps might be legitimate non-tool work.

---

### **5. CEO-Ready Time Waste Metrics**

**Parable's customers are CEOs.** They need simple, actionable metrics:

#### **Metric 1: Total Wasted Hours per Employee**

```
Weekly waste = auth_waste_hours + context_switch_waste_hours
Annual cost = weekly_waste × 50 weeks × hourly_salary
```

#### **Metric 2: Organization-Wide Productivity Loss**

```
Total annual waste = Σ(employee_annual_cost) across all employees
Percentage of time wasted = total_waste_hours / total_work_hours
```

#### **Metric 3: Top Waste Categories**

- "Authentication friction: 15% of employees waste 6+ hrs/week (35% of wasted time)"
- "Context switching: 25% of employees switch 40+ times/day (45% of wasted time)"
- "Underutilized tools: 12 apps with < 5% adoption ($200k in licenses)"

#### **Metric 4: ROI of Interventions**

- "Implementing risk-based auth could reduce auth friction by 60% = $9M/year savings"
- "Focus mode alerts could reduce context switching by 30% = $6M/year savings"
- "Reclaiming unused licenses = $200k immediate cost savings"

**Example CEO Dashboard (Production Data - Full Daily/Weekly Coverage):**

⚠️ This example assumes full production SSO data with days/weeks of coverage per user. Cannot be computed from our 13-second sample.

```
Organization: 1,000 employees
Total Wasted Time: 12,000 hours/week (24% of work time)
Annual Cost: $31M in wasted productivity
Top Opportunities:
  1. Context Switching (45%) - $14M opportunity
  2. Auth Friction (35%) - $11M opportunity
  3. Unused Tools (15%) - $5M opportunity
  4. Idle/Blocked Time (5%) - $1M opportunity
```

---

### **Time Metrics Summary Table**

| Metric             | Formula                                | Sample Calculation                 | Impact          |
| ------------------ | -------------------------------------- | ---------------------------------- | --------------- |
| **Auth Waste**     | (authStep - 1) × 0.5 min × daily_auths | Step 8 user, 20 auths = 70 min/day | 5.8 hrs/week    |
| **Context Switch** | app_switches × 5 min                   | 47 switches = 235 min/day          | 19.5 hrs/week   |
| **App Dwell**      | MAX(time) - MIN(time) per app          | Avg 12 min = fragmented            | Low focus       |
| **Idle Gaps**      | Gaps > 4 hrs between events            | 6 hr gap = blocked time            | Dependency wait |
| **Total Waste**    | Sum of above                           | 25+ hrs/week                       | 60% of time     |

**Key Insight for Parable:** Every pattern in SSO data can be converted to hours wasted and dollars lost. That's what CEOs care about.

---

### **Sample Data Capabilities Summary**

**What We CAN Compute from 13-Second Sample (18 events, 10 users):**

| Metric                         | Status | What We Can See                                         |
| ------------------------------ | ------ | ------------------------------------------------------- |
| **Auth Step Distribution**     | ✅ YES | Range: 1-9, Average: 5.6, Mode: Step 8 (33%)            |
| **Auth Step Variability**      | ✅ YES | Wide range indicates friction opportunities             |
| **Per-User Auth Patterns**     | ✅ YES | User "mco laboris nisi ut" consistently faces step 9    |
| **User Segmentation Snapshot** | ✅ YES | 30% power users (2 apps), 40% regular, 30% casual (0-1) |
| **App Co-occurrence**          | ✅ YES | 5 app pairs appear together in same session             |
| **App Diversity Per User**     | ✅ YES | Average 1.1 unique apps, max 2                          |

**What We CANNOT Compute from 13-Second Sample (Requires Full Day/Week):**

| Metric                       | Status | Why Not?                                                        |
| ---------------------------- | ------ | --------------------------------------------------------------- |
| **Daily Auth Frequency**     | ❌ NO  | Need full day, not 13 seconds (can't extrapolate)               |
| **Auth Time Waste ($/year)** | ❌ NO  | Requires daily_auths count (depends on full day coverage)       |
| **Context Switching**        | ❌ NO  | Need hours/days to observe switching patterns                   |
| **App Dwell Time**           | ❌ NO  | Need session-level data over time (min to hours)                |
| **Focus vs Fragmented Time** | ❌ NO  | Requires observing work sessions (30-120 min each)              |
| **Idle Time Gaps**           | ❌ NO  | Need multi-hour coverage to detect > 4 hr gaps                  |
| **Weekly Productivity Loss** | ❌ NO  | All weekly/annual calculations require daily baseline           |
| **Org-Wide ROI Estimates**   | ❌ NO  | Extrapolation from 13 seconds → days is not statistically valid |

**Production Data Requirements:**

- **Minimum:** 1 full business day (8 hours) per user for basic patterns
- **Recommended:** 2-4 weeks for reliable productivity metrics and trend analysis
- **Scale:** Parable operates at petabyte scale with weeks/months of data per user
