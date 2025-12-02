# Analytical Questions: App Co-Occurrence Discovery

**Goal**: Discover which apps are used together and what that reveals about work types.

### Q1: Which applications are accessed together by the same users?

**Finding**:

- **5 users** access 2 apps each (50% of sample)
- **5 distinct app pairs** discovered
- Even in 13 seconds, co-occurrence patterns are visible

### Q2: How do users segment by their app usage?

**Finding**:

- **50% multi-app/power users** (2 apps) - show co-occurrence patterns
- **10% single-app/regular users** (1 app) - specialized roles
- **40% auth-only/casual users** (0 apps) - auth-only in this snapshot

User segmentation + app co-occurrence = role-based insights. Power users with GitHub + Figma get frontend-specific optimizations. Regular users with only Salesforce get CRM-specific tips. This is personalized productivity at scale.

### Hypothesis: App combinations reveal work types

App co-occurrence patterns are proxies for job roles - without needing HR data. By analyzing which applications users access together over 90 days, we can automatically categorize work types (Engineering, Sales, Support, HR) without requiring HR data, enabling personalized productivity interventions at scale.

**Analysis Framework**:

In production, app co-occurrence patterns map to job roles:

| Role                  | App Signature                        | What it Suggests                       |
| --------------------- | ------------------------------------ | -------------------------------------- |
| **Frontend Engineer** | GitHub + Jira + Figma + Slack        | Code + tickets + design collaboration  |
| **Sales**             | Salesforce + Gmail + LinkedIn + Zoom | CRM + communication + outreach         |
| **Customer Support**  | Zendesk + Intercom + Slack           | Ticketing + customer messaging + comms |
| **HR**                | Workday + BambooHR + Slack           | HRIS + docs + team communication       |
| **Marketing**         | Mailchimp + HubSpot + Canva          | Email campaigns + CRM + design         |

**The Insight**:

```python
# Example: If user's 90-day pattern shows...
user_pattern = {
    'GitHub': 250,
    'Jira': 90,
    'Figma': 30,
    'Slack': 180
}

# → This is a Frontend Engineer signature
# → Can provide role-specific productivity optimizations
```

---

## Production Validation Queries

**Goal**: Demonstrate how to validate app co-occurrence patterns at production scale.

### Q1: App Usage Patterns by User (90-day)

In production, this query gives the input for role categorization - each user's 90-day app access frequency. Look out for patterns: engineers have heavy GitHub + Jira, sales have heavy Salesforce + Gmail.

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
FROM okta_audit_logs
WHERE event_date >= CURRENT_DATE - 90  -- 90-day window
    AND target.id IS NOT NULL  -- Only app access events
GROUP BY user_id, user_name
ORDER BY unique_apps DESC
LIMIT 100;
```

**Expected Patterns**:

- Engineers: GitHub (250), Jira (90), Figma (30), Slack (180)
- Sales: Salesforce (100+), Gmail (300+), LinkedIn (50+)
- Support: Zendesk (150+), Slack (100+), Intercom (80+)
- HR: Workday (regular), BambooHR, DocuSign

---

### Q2: App Co-Occurrence Analysis (Finding Common Pairs)

This query finds the most common app pairs across the organization. GitHub + Jira with 230 users = engineering team signature. Salesforce + Gmail with 180 users = sales team. These pairs are the foundation for role detection.

```sql
-- Find app pairs frequently accessed together
-- Helps identify work pattern signatures
WITH user_apps AS (
    SELECT
        user_id,
        app_name,
        COUNT(*) as access_count
    FROM okta_audit_logs
    WHERE event_date >= CURRENT_DATE - 90
        AND app_name IS NOT NULL
    GROUP BY user_id, app_name
),
app_pairs AS (
    SELECT
        a1.user_id,
        a1.app_name as app1,
        a2.app_name as app2,
        a1.access_count as app1_count,
        a2.access_count as app2_count
    FROM user_apps a1
    JOIN user_apps a2
        ON a1.user_id = a2.user_id
        AND a1.app_name < a2.app_name  -- Avoid duplicates
)
SELECT
    app1,
    app2,
    COUNT(DISTINCT user_id) as users_with_pair,
    AVG(app1_count) as avg_app1_usage,
    AVG(app2_count) as avg_app2_usage
FROM app_pairs
GROUP BY app1, app2
HAVING COUNT(DISTINCT user_id) >= 10  -- At least 10 users
ORDER BY users_with_pair DESC
LIMIT 20;
```

**Expected Output** (production example):

```
app1           app2        users_with_pair  avg_app1_usage  avg_app2_usage
GitHub         Jira        230              245             85
Salesforce     Gmail       180              120             310
Slack          Zoom        450              200             45
Zendesk        Intercom    95               160             75
```

---

### Q3: User Segmentation by App Diversity

App diversity is another signal. Someone accessing 10+ apps is likely cross-functional (manager, PM). Someone with 3-4 apps is specialized (engineer, support). Combined with app co-occurrence, this gives us strong role detection signal.

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
    FROM okta_audit_logs
    WHERE event_date >= CURRENT_DATE - 90
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

**Expected Distribution**:

- Multi-role (10+ apps): 15% of users - managers, cross-functional
- Cross-functional (5-9 apps): 35% of users - mid-level ICs
- Specialized (3-4 apps): 30% of users - focused roles (eng, sales)
- Focused (1-2 apps): 20% of users - highly specialized or casual
