## Evaluation framework

### 1. Ground Truth Establishment

**Data Needed:**

- 90-day SSO audit logs for 500-1000 employees
- HR job titles/roles for the same employees (ground truth labels)
- App catalog with descriptions

Why 90 days? Long enough to capture work patterns, short enough to avoid role changes.

### 2. Core Validation Metrics

#### Accuracy Metrics

```python
# Confusion matrix approach

from sklearn.metrics import classification_report, accuracy_score

ground_truth_roles = ["Software Engineer", "Sales", "Support", ...] # From HR
predicted_roles = ["Software Engineer", "Sales", "Customer Support", ...] # From agent

accuracy = accuracy_score(ground_truth_roles, predicted_roles)

# Target: >80% accuracy

report = classification_report(ground_truth_roles, predicted_roles)

# Check precision/recall per role
```

**Key Question:** Does the agent's categorization match HR job titles at least 80% of the time?

#### Explainability Validation

```python
# Show 50 managers their team's categorizations with reasoning

for categorization in sample_categorizations:
    show_manager({
        'employee': categorization.user_name,
        'predicted_role': categorization.role,
        'reasoning': categorization.explanation, # "Heavy GitHub (250), Jira (90), Figma (30) = frontend"
        'app_pattern': categorization.app_usage
    })

    manager_agreement = ask("Does this match your understanding? 1-5")
    confidence = ask("How confident are you in this categorization? 1-5")

# Target: >85% agreement, >4.0/5 average confidence
```

**Key Question:** Do managers trust and agree with the categorizations?

### 3. Experimental Design

#### A/B Test for ROI Validation

- **Group A (Control):** 500 employees receive generic productivity tips
- **Group B (Treatment):** 500 employees receive role-specific optimizations
  - Frontend engineers: GitHub workflow automation, Figma collaboration tips
  - Sales: Salesforce + Gmail integration shortcuts
  - Support: Zendesk macro suggestions

**Measure over 30 days:**

- Time saved per employee (self-reported + activity logs)
- Task completion rates
- App switching frequency (should decrease)

**Target:** 10-15% productivity increase in Group B

### 4. Adaptability Test (Why Agentic > ML)

**Scenario:** New app introduced (e.g., Notion) mid-study

**ML Approach:**

- K-means clustering breaks (new feature dimension)
- Needs retraining on historical data
- Can't explain why clusters changed

**Agentic Approach:**

```python
# Few-shot prompt automatically incorporates new app

industry_benchmarks = """
Frontend Engineer: GitHub (200+), Jira (80+), Figma (30+)
Product Manager: Jira (100+), Confluence (50+), Notion (40+) # <-- NEW
Sales: Salesforce (100+), Gmail (300+), LinkedIn (50+)
"""

# Agent sees user with: GitHub (250), Jira (90), Notion (45)

# Output: "Frontend Engineer transitioning to PM role - showing PM tool adoption"
```

**Test:** Introduce 3 new apps to org, measure:

- ML model: Requires retraining, accuracy drops to ~60%
- Agentic: Updates few-shot examples, maintains >80% accuracy
- Agentic provides explanations: "Notion usage suggests cross-functional collaboration"

### 5. Edge Case Validation

**Test on challenging cases:**

- Cross-functional roles (PM using eng + sales tools)
- Career transitions (engineer → manager, app patterns shift)
- Specialized roles (DevOps, Data Science, Security)

**Expected:** Agent should either:

1. Correctly identify hybrid roles: "Frontend Engineer + PM duties"
2. Flag uncertainty: "Pattern unclear - needs manual review"

### 6. Production Validation Queries

From your docs/4_analytical_questions.md, these SQL queries would provide the validation data:

```sql
-- Q1: Get 90-day app usage patterns
SELECT
    actor.id,
    ARRAY_AGG(STRUCT(target.displayName, COUNT(*)) ORDER BY COUNT(*) DESC) as app_pattern
FROM okta_audit_logs
WHERE event_date >= CURRENT_DATE - 90 AND target.id IS NOT NULL
GROUP BY actor.id;

-- Q2: Find app co-occurrence patterns
-- (Validates that certain app pairs = role signatures)
SELECT app1, app2, COUNT(DISTINCT user_id) as users_with_pair
FROM app_pairs
GROUP BY app1, app2
HAVING COUNT(DISTINCT user_id) >= 10
ORDER BY users_with_pair DESC;
```

**Expected Findings:**

- GitHub + Jira appears in 230 users → Engineering cluster
- Salesforce + Gmail appears in 180 users → Sales cluster
- These patterns should align with HR ground truth

### 7. Cost-Benefit Analysis

**Prove the $100M ROI claim:**

**Baseline (no categorization):**

- Generic productivity tools = 10% waste
- 1,000 employees × $50/hr × 40 hrs/week × 10% waste = $2M/week

**With Work Categorizer:**

- Role-specific optimizations reduce waste to 2% (8% improvement)
- Savings: $1.6M/week × 50 weeks = $80M/year

**Agent Cost:**

- $0.02/categorization × 10k employees / 90 days = $67/month
- ROI: $80M / $804 = ~99,000x return

**Validation:** Measure actual productivity gains in A/B test, extrapolate to full org.

### 8. The Proof Pipeline

1. Collect 90-day SSO logs for 500 employees
2. Run Work Categorizer agent → Get role predictions with reasoning
3. Compare predictions to HR ground truth → Measure accuracy (>80%)
4. Show 50 managers the categorizations → Get agreement (>85%) and confidence (>4.0/5)
5. Run A/B test with role-specific interventions → Measure productivity gain (10-15%)
6. Introduce new apps → Validate adaptability (agentic maintains >80%, ML drops to ~60%)
7. Calculate ROI from productivity gains → Validate $80M+ annual savings claim
