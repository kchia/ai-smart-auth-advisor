# Verification Queries for Top 3 Hypotheses

**Purpose:** SQL queries to verify the top 3 hypotheses using production-scale SSO audit log data

**Assumptions:**

- Production BigQuery dataset with full daily/weekly coverage
- Table structure based on Okta SSO audit log schema
- Queries assume a table named `sso_events` (adjust as needed)

**Note:** These queries assume access to a larger dataset than the 13-second sample.

---

## Hypothesis 2.1: Authentication Friction ⭐⭐⭐⭐⭐

**Goal:** Verify that users with higher authentication steps waste significant time

**Target ROI:** $2.4M/year for 1,000 employees (15% at step 8-9)

### Query 1: Auth Step Distribution

```sql
-- Identify users with high authentication friction
-- Shows: range of auth steps, avg per user, time waste potential
SELECT
    authenticationContext.authenticationStep as auth_step,
    COUNT(*) as event_count,
    COUNT(DISTINCT actor.id) as unique_users,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as pct_of_events
FROM sso_events
WHERE DATE(published) >= CURRENT_DATE() - 30  -- Last 30 days
    AND authenticationContext.authenticationStep IS NOT NULL
GROUP BY auth_step
ORDER BY auth_step DESC;
```

**Expected Pattern:** Wide distribution with concentration at steps 7-9 indicating friction opportunities

### Query 2: Time Waste by User

```sql
-- Calculate daily authentication time waste per user
-- Time formula: (authStep - 1) × 30 seconds × daily_auths
SELECT
    actor.id as user_id,
    actor.displayName as user_name,
    COUNT(*) as daily_auths,
    ROUND(AVG(authenticationContext.authenticationStep), 1) as avg_auth_step,
    -- Time waste calculation
    ROUND((AVG(authenticationContext.authenticationStep) - 1) * 0.5 * COUNT(*), 1) as daily_minutes_wasted,
    ROUND((AVG(authenticationContext.authenticationStep) - 1) * 0.5 * COUNT(*) * 5 / 60, 1) as weekly_hours_wasted,
    -- Annual cost at $50/hr
    ROUND((AVG(authenticationContext.authenticationStep) - 1) * 0.5 * COUNT(*) * 5 / 60 * 50 * 50, 0) as annual_cost_per_user
FROM sso_events
WHERE DATE(published) = CURRENT_DATE() - 1  -- Full single day for accurate count
    AND authenticationContext.authenticationStep IS NOT NULL
GROUP BY user_id, user_name
HAVING avg_auth_step >= 8  -- Focus on high-friction users
ORDER BY daily_minutes_wasted DESC
LIMIT 100;
```

**Expected Output:**

- 10-15% of users with avg_auth_step >= 8
- Weekly hours wasted: 5-7 hours per affected user
- Annual cost: $15,000-$17,000 per affected user

### Query 3: Organization-Wide Impact

```sql
-- Calculate org-wide authentication friction cost
WITH user_metrics AS (
    SELECT
        actor.id as user_id,
        AVG(authenticationContext.authenticationStep) as avg_step,
        COUNT(*) as daily_auths,
        (AVG(authenticationContext.authenticationStep) - 1) * 0.5 * COUNT(*) * 5 / 60 * 50 * 50 as annual_cost
    FROM sso_events
    WHERE DATE(published) = CURRENT_DATE() - 1
        AND authenticationContext.authenticationStep IS NOT NULL
    GROUP BY user_id
)
SELECT
    COUNT(*) as total_users,
    COUNT(CASE WHEN avg_step >= 8 THEN 1 END) as high_friction_users,
    ROUND(COUNT(CASE WHEN avg_step >= 8 THEN 1 END) * 100.0 / COUNT(*), 1) as pct_high_friction,
    ROUND(SUM(annual_cost), 0) as total_annual_cost,
    ROUND(AVG(CASE WHEN avg_step >= 8 THEN annual_cost END), 0) as avg_cost_per_affected_user
FROM user_metrics;
```

**Verification Criteria:**

- ✅ 10-20% of users at step 8-9
- ✅ Total annual cost ~$2M-$3M for 1,000 employees
- ✅ Clear correlation between auth steps and time waste

---

## Hypothesis 2.7: Work Categorizer ⭐⭐⭐⭐⭐

**Goal:** Verify that app usage patterns can categorize work types

**Target ROI:** $100M/year (10% productivity gain from role-based optimizations)

### Query 1: App Usage Patterns by User

```sql
-- Get 90-day app usage patterns for work categorization
-- Shows which apps each user accesses and frequency
SELECT
    actor.id as user_id,
    actor.displayName as user_name,
    ARRAY_AGG(
        STRUCT(
            target.displayName as app_name,
            COUNT(*) as access_count
        )
        ORDER BY COUNT(*) DESC
    ) as app_usage_pattern,
    COUNT(DISTINCT target.id) as unique_apps,
    COUNT(*) as total_accesses
FROM sso_events
WHERE DATE(published) >= CURRENT_DATE() - 90  -- 90-day window
    AND target.id IS NOT NULL  -- Only app access events
GROUP BY user_id, user_name
ORDER BY unique_apps DESC
LIMIT 100;
```

**Expected Patterns:**

- Engineers: GitHub, Jira, Figma, Slack (heavy)
- Sales: Salesforce, Gmail, Calendar, LinkedIn
- Support: Zendesk, Slack, internal tools
- HR: Workday, BambooHR, email

### Query 2: App Co-occurrence Analysis

```sql
-- Find app pairs frequently accessed together
-- Helps identify work pattern signatures
WITH user_apps AS (
    SELECT
        actor.id as user_id,
        DATE(published) as access_date,
        ARRAY_AGG(DISTINCT target.displayName) as apps_accessed
    FROM sso_events
    WHERE DATE(published) >= CURRENT_DATE() - 90
        AND target.id IS NOT NULL
    GROUP BY user_id, access_date
)
SELECT
    app1,
    app2,
    COUNT(*) as co_occurrence_count,
    COUNT(DISTINCT user_id) as unique_users
FROM user_apps,
    UNNEST(apps_accessed) as app1,
    UNNEST(apps_accessed) as app2
WHERE app1 < app2  -- Avoid duplicates (A,B) vs (B,A)
GROUP BY app1, app2
HAVING co_occurrence_count >= 10  -- Significant co-occurrence
ORDER BY co_occurrence_count DESC
LIMIT 50;
```

**Expected Output:**

- Strong app pairs indicating work types
- Example: (GitHub, Jira) = Engineering
- Example: (Salesforce, HubSpot) = Sales

### Query 3: User Segmentation by App Diversity

```sql
-- Segment users by app access diversity (proxy for work categorization)
-- Higher diversity might indicate cross-functional roles
WITH user_app_stats AS (
    SELECT
        actor.id as user_id,
        actor.displayName as user_name,
        COUNT(DISTINCT target.id) as unique_apps,
        COUNT(*) as total_accesses,
        ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT target.id), 1) as avg_accesses_per_app
    FROM sso_events
    WHERE DATE(published) >= CURRENT_DATE() - 90
        AND target.id IS NOT NULL
    GROUP BY user_id, user_name
)
SELECT
    CASE
        WHEN unique_apps >= 10 THEN 'Multi-role (10+ apps)'
        WHEN unique_apps >= 5 THEN 'Cross-functional (5-9 apps)'
        WHEN unique_apps >= 3 THEN 'Specialized (3-4 apps)'
        ELSE 'Focused (1-2 apps)'
    END as work_type_proxy,
    COUNT(*) as user_count,
    ROUND(AVG(unique_apps), 1) as avg_apps,
    ROUND(AVG(total_accesses), 0) as avg_total_accesses
FROM user_app_stats
GROUP BY work_type_proxy
ORDER BY avg_apps DESC;
```

**Verification Criteria:**

- ✅ Distinct app usage clusters visible
- ✅ App co-occurrence patterns align with known roles
- ✅ Enough signal to train/validate LLM categorization (ground truth from HR)

---

## Hypothesis 3.1: User Segmentation ⭐⭐⭐⭐

**Goal:** Verify user clustering into power/regular/casual segments

**Target ROI:** $1.1M/year (license optimization)

### Query 1: User Segmentation by Activity

```sql
-- Segment users into power/regular/casual based on app access
SELECT
    CASE
        WHEN unique_apps >= 5 AND total_accesses >= 100 THEN 'Power User'
        WHEN unique_apps >= 2 AND total_accesses >= 20 THEN 'Regular User'
        WHEN unique_apps >= 1 OR total_accesses >= 5 THEN 'Casual User'
        ELSE 'Inactive/Auth-Only'
    END as user_segment,
    COUNT(*) as user_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as pct_of_users,
    ROUND(AVG(unique_apps), 1) as avg_apps,
    ROUND(AVG(total_accesses), 0) as avg_accesses,
    ROUND(AVG(total_accesses * 1.0 / NULLIF(unique_apps, 0)), 1) as avg_accesses_per_app
FROM (
    SELECT
        actor.id as user_id,
        COUNT(DISTINCT target.id) as unique_apps,
        COUNT(*) as total_accesses
    FROM sso_events
    WHERE DATE(published) >= CURRENT_DATE() - 30  -- Last 30 days
        AND target.id IS NOT NULL
    GROUP BY user_id
)
GROUP BY user_segment
ORDER BY
    CASE user_segment
        WHEN 'Power User' THEN 1
        WHEN 'Regular User' THEN 2
        WHEN 'Casual User' THEN 3
        ELSE 4
    END;
```

**Expected Distribution:**

- Power users: 20-30% (high app diversity + frequency)
- Regular users: 40-50% (moderate usage)
- Casual users: 20-30% (low usage)
- Inactive: 5-10% (license optimization candidates)

### Query 2: License Optimization Opportunities

```sql
-- Identify casual/inactive users for license reclamation
-- Focus on users with low app usage over 90 days
WITH user_activity AS (
    SELECT
        actor.id as user_id,
        actor.displayName as user_name,
        COUNT(DISTINCT target.id) as unique_apps,
        COUNT(*) as total_accesses,
        MAX(published) as last_access_date,
        DATE_DIFF(CURRENT_DATE(), DATE(MAX(published)), DAY) as days_since_access
    FROM sso_events
    WHERE DATE(published) >= CURRENT_DATE() - 90
    GROUP BY user_id, user_name
)
SELECT
    CASE
        WHEN days_since_access > 60 THEN 'Inactive (60+ days)'
        WHEN unique_apps = 0 OR total_accesses <= 5 THEN 'Minimal Usage'
        WHEN unique_apps = 1 AND total_accesses <= 10 THEN 'Single App Light User'
        ELSE 'Active'
    END as optimization_category,
    COUNT(*) as user_count,
    -- Potential license savings (assuming $100/user/month for SaaS licenses)
    COUNT(*) * 100 * 12 as potential_annual_savings
FROM user_activity
WHERE unique_apps <= 1  -- Focus on low app diversity
    OR days_since_access > 30
GROUP BY optimization_category
ORDER BY potential_annual_savings DESC;
```

**Expected Output:**

- 10-20% of users are license optimization candidates
- Annual savings: $100-$200k per 1,000 employees

### Query 3: Segment Stability Over Time

```sql
-- Verify that user segments are stable (not random fluctuation)
-- Compare 30-day segments across rolling windows
WITH segment_snapshots AS (
    SELECT
        actor.id as user_id,
        DATE_TRUNC(DATE(published), MONTH) as month,
        COUNT(DISTINCT target.id) as unique_apps,
        COUNT(*) as total_accesses,
        CASE
            WHEN COUNT(DISTINCT target.id) >= 5 THEN 'Power'
            WHEN COUNT(DISTINCT target.id) >= 2 THEN 'Regular'
            ELSE 'Casual'
        END as segment
    FROM sso_events
    WHERE DATE(published) >= CURRENT_DATE() - 180  -- Last 6 months
        AND target.id IS NOT NULL
    GROUP BY user_id, month
)
SELECT
    user_id,
    COUNT(DISTINCT segment) as segment_changes,
    STRING_AGG(segment, ' -> ' ORDER BY month) as segment_trajectory
FROM segment_snapshots
GROUP BY user_id
HAVING COUNT(*) >= 3  -- Users with at least 3 months of data
ORDER BY segment_changes DESC
LIMIT 100;
```

**Verification Criteria:**

- ✅ 70%+ of users stay in same segment across months (stable)
- ✅ Clear separation between power/regular/casual
- ✅ License optimization candidates identified (low usage 60+ days)

---

## Summary: Verification Checklist

### Hypothesis 2.1: Authentication Friction ✅

- [ ] Auth step distribution shows 10-20% at steps 8-9
- [ ] Time waste calculation yields $15k-$17k/year per affected user
- [ ] Organization-wide cost ~$2M-$3M matches prediction

### Hypothesis 2.7: Work Categorizer ✅

- [ ] Distinct app usage patterns visible (e.g., GitHub+Jira vs Salesforce)
- [ ] App co-occurrence pairs align with known work types
- [ ] Sufficient signal for LLM-based categorization (validate with HR ground truth)

### Hypothesis 3.1: User Segmentation ✅

- [ ] Clear segmentation into power/regular/casual (not uniform distribution)
- [ ] 10-20% optimization candidates (low usage or inactive)
- [ ] Segment stability >70% across rolling time windows

---
