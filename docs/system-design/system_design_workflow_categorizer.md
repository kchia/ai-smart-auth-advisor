# System Design & Production Architecture

**Purpose:** Prepare for the system design portion of the Parable interview
**Focus:** Designing production-grade agentic workflows at petabyte scale for Fortune 1000 clients

**⭐ CRITICAL:** This interview is testing your ability to design the ACTUAL Parable product:

- Work categorizer agentic workflow (first 3-month deliverable)
- Organizational observability platform
- CEO-facing insights at Fortune 1000 scale
- Production concerns: RBAC, privacy, tracing, evaluation

---

## 🎯 Interview Flow: Data Analysis → System Design

### Typical Transition (60-minute interview)

**Minutes 1-30:** Collaborative data analysis

- You've just finished coding together, tested a hypothesis
- Found interesting patterns (e.g., auth friction, user segmentation)
- Quantified time waste with ROI calculations

**Minutes 30-60:** System design discussion

- **Interviewer:** "Interesting findings! Now, how would you build a production system that delivers these insights to CEOs at scale?"
- **You:** _This is where Phase 3 preparation kicks in_

---

## 🏗️ System Design Framework (Parable-Specific)

### The 7 Key Areas to Cover

When designing ANY agentic workflow solution for Parable, address these 7 areas:

1. **Business Requirements** (CEO-level)

   - Which of the 5 CEO questions does this answer?
   - What is the quantified ROI? (time saved, $ saved)
   - What decisions can CEOs make with this insight?

2. **Agentic Workflow Architecture**

   - Agent design (tools, LLM prompting, flow)
   - Why agentic > traditional ML?
   - Natural language outputs for CEO audience

3. **Data Pipeline**

   - Ingestion (SSO logs from 50+ Fortune 1000 clients)
   - Storage (BigQuery, Iceberg data lake)
   - Processing (Cloud Run jobs, Pub/Sub)

4. **RBAC & Privacy**

   - Who can see what data?
   - Row-level security in BigQuery
   - PII handling, anonymization

5. **Evaluation & Quality**

   - Ground truth labels (how to validate agent outputs)
   - A/B testing framework
   - Success metrics

6. **Tracing & Monitoring**

   - LLM call logging (cost, latency, tokens)
   - Error tracking, alerting
   - Cost management across 500k users

7. **Scale & Performance**
   - Petabyte-scale data processing
   - Latency requirements (< 3 sec for dashboards)
   - Cost optimization ($3k/month LLM costs for 10k employees)

---

## 🎯 Example: Work Categorizer Agentic Workflow (First 3-Month Deliverable)

### 1. Business Requirements

**Problem Statement:**
CEOs need to understand how employees spend their time, but they lack visibility into work patterns across thousands of employees.

**CEO Questions Answered:**

- "How can we use AI to make teams 100x productive?" (personalized interventions)
- "Where can we automate?" (role-based optimizations)

**ROI:**

- Without categorization: Generic IT policies → 5-10% productivity loss (conservative estimate)
- 1,000 employees × $50/hr × 40 hrs/week × 5% = **$1M/week = $50M/year waste**
- With categorization: Role-specific optimizations → 10-15% productivity gain
- **Note:** These are assumptions to be validated through A/B testing in production

**CEO-Level Decisions Enabled:**

- "Our engineering team wastes 4.2 hrs/week on tool friction → invest in dev tools integration"
- "Sales team underutilizes CRM → provide training or consolidate tools"

---

### 2. Agentic Workflow Architecture

**Why Agentic > Traditional ML:**

| Aspect             | Traditional ML (K-means)         | Agentic Workflow                                                                                              |
| ------------------ | -------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| **Output**         | "User in cluster 3"              | "Software Engineer (Frontend) BECAUSE..."                                                                     |
| **Explainability** | Black box                        | Natural language with citations                                                                               |
| **Adaptability**   | Requires retraining for new apps | Few-shot learning, adapts immediately                                                                         |
| **CEO-friendly**   | No                               | Yes - actionable insights                                                                                     |
| **Example**        | "Cluster 3 has 450 employees"    | "Engineers (450) waste 4.2 hrs/week on context switching. ROI: $2.1M/year if we implement workflow bundling." |

**Agent Design:**

```
Work Categorizer Agent
└── Input: user_id
└── Tools:
    ├── query_user_app_history(user_id, days=90)
    │   └── Returns: {GitHub: 250 accesses, Slack: 180, Jira: 90, Figma: 30}
    ├── query_app_cooccurrence(apps_list)
    │   └── Returns: Apps commonly used together in sessions
    ├── get_industry_benchmarks(industry)
    │   └── Returns: Typical app patterns for known roles
    ├── categorize_work_pattern(app_signature) [LLM]
    │   └── Input: App usage metrics
    │   └── Output: Work category + confidence + reasoning
    └── suggest_optimizations(category, current_setup) [LLM]
        └── Input: Category + current IT policies
        └── Output: Personalized productivity recommendations

└── Flow:
    1. Query BigQuery for user's app access patterns (last 90 days)
    2. Extract app signature: frequency, recency, co-occurrence
    3. LLM analyzes with few-shot prompting:
       Prompt: "Given these app access patterns, what type of work
               does this user do? Evidence: [app metrics]. Known
               patterns: [industry benchmarks]. Categorize with
               reasoning and confidence."
    4. LLM responds with structured output:
       {
         "category": "Software Engineer (Frontend/Full-stack)",
         "confidence": 0.95,
         "reasoning": "Heavy GitHub usage (250) + Jira (90) +
                      Figma (30) indicates frontend engineering",
         "evidence": ["GitHub access 88% of activity",
                     "Figma suggests UI work"]
       }
    5. Generate optimization recommendations (another LLM call):
       "For engineers: reduce auth steps for GitHub/Jira,
        bundle dev tools, alert on excessive Slack switching.
        Potential savings: 3-5 hrs/week = $7.5k-12.5k/year per eng."
    6. Store results in BigQuery for CEO dashboard

└── Output to CEO Dashboard:
    "Work Category Distribution:
     - Engineering (45%) - 450 employees
       → Opportunity: Reduce tool friction → $2.1M/year savings
     - Sales (20%) - 200 employees
       → Opportunity: CRM consolidation → $800k/year savings
     - Customer Support (15%) - 150 employees
     - Operations (10%) - 100 employees
     - Management (10%) - 100 employees

     Top Recommendation:
     Implement role-based IT policies to reduce context switching
     and auth friction for engineering team. Projected ROI: $2.1M/year."
```

**Actual LLM Prompt (Memorize for Interview):**

```
System: You are a work categorization expert for enterprise productivity analysis.

User: Analyze the following employee's app usage patterns from the last 90 days and categorize their primary work role.

App Access Data:
- GitHub: 250 accesses (code repository, version control)
- Slack: 180 accesses (team communication)
- Jira: 90 accesses (project management, issue tracking)
- Figma: 30 accesses (design and prototyping tool)

Industry Benchmarks (few-shot examples):
- Software Engineers typically use: GitHub (high), Jira (medium), Slack (medium), IDEs
- Designers typically use: Figma (high), Adobe Suite (high), Slack (medium)
- Sales typically use: Salesforce (high), Gmail (high), Calendar (high), HubSpot
- Product Managers typically use: Jira (high), Figma (medium), Slack (high), Notion

Task:
1. Categorize this employee's primary work role
2. Provide confidence score (0.0 to 1.0)
3. Explain reasoning with specific citations to the data
4. List supporting evidence

Output format (JSON):
{
  "category": "Software Engineer (Frontend/Full-stack)",
  "confidence": 0.95,
  "reasoning": "Heavy GitHub usage (250 accesses) indicates active coding and version control work. Jira access (90 times) suggests agile development workflow with sprint planning. Figma usage (30 accesses) indicates involvement in UI/UX work, suggesting frontend or full-stack engineering rather than pure backend. This pattern strongly matches typical frontend engineer signature.",
  "evidence": [
    "GitHub accounts for 44% of total app usage (250/570 total accesses)",
    "GitHub + Jira + Slack = 88% of activity, matching core engineering workflow",
    "Figma presence (5% of usage) differentiates from backend engineers",
    "No backend-specific tools (database clients, cloud consoles) detected"
  ],
  "sub_category": "Frontend-leaning full-stack engineer"
}
```

**Why this prompt works:**

- Few-shot examples guide the LLM (shows patterns for different roles)
- Structured output format ensures consistent, parseable responses
- Requires explicit confidence scoring for downstream filtering
- Asks for evidence/citations (explainability for CEO dashboards)
- Includes sub-categorization for nuanced roles

---

### 3. Data Pipeline (GCP Architecture)

**Ingestion:**

```
SSO Providers (Okta, Google Workspace, Azure AD)
    ↓ Webhooks / Polling
Cloud Pub/Sub Topic: "sso-events-raw"
    ↓ Subscribe
Cloud Run Job: "sso-event-ingestion"
    ↓ Parse, validate, enrich
BigQuery Table: "sso_events_raw"
    ├── Partitioned by: date (YYYYMMDD)
    ├── Clustered by: actor_id, target_id
    └── Row-level security: tenant_id (single-tenant isolation)
```

**Processing (Nightly Batch):**

```
Cloud Scheduler (cron: 0 2 * * *)  # Run at 2am daily
    ↓ Trigger
Cloud Run Job: "work-categorizer-batch"
    ├── Query BigQuery for users needing recategorization:
    │   ├── 90 days since last categorization (scheduled refresh)
    │   ├── OR manager override flag (immediate recategorization)
    │   ├── OR pattern change score > threshold (cheap heuristic:
    │   │   count of new apps accessed > 3, or 50% change in app mix)
    │   └── Pre-compute pattern change scores daily (simple SQL, no LLM)
    ├── For each user (5,556 users/day across 50 clients):
    │   ├── Extract app usage metrics (last 90 days)
    │   ├── Call Work Categorizer Agent (2 LLM calls)
    │   ├── Cost: ~$0.02 per categorization
    │   └── Store result in BigQuery
    └── Refresh materialized views for CEO dashboard
        └── Total runtime: ~2 hours for 5,556 users
```

**Storage:**

```
BigQuery Dataset: "organizational_insights"
├── Table: "sso_events_raw"
│   └── 1 billion events/day × 365 days = 365B events
│   └── ~100 bytes/event = 36.5 TB/year
│   └── Cost: ~$750/month storage + $50k-500k/month queries
│
├── Table: "work_categories"
│   ├── Schema: user_id, category, confidence, reasoning, last_updated
│   ├── Rows: 500k users (50 clients × 10k avg employees)
│   └── Cost: Negligible (~500 MB)
│
└── Materialized View: "productivity_metrics_dashboard"
    ├── Refreshed every 6 hours
    ├── Pre-aggregates for CEO dashboard (< 3 sec load time)
    └── Partitioned by: client_id, department
```

**Iceberg Data Lake (Long-term Archive):**

```
Cloud Storage Bucket: "parable-data-lake"
├── Format: Apache Iceberg (ACID transactions, schema evolution)
├── Data: SSO events older than 90 days
├── Cost: ~$0.02/GB/month (~$20/TB/year) vs BigQuery ($20/TB/month)
│   └── 12x cheaper for archival! $750/year vs $9,000/year for 365 TB
└── Use case: Historical analysis, compliance, audit trails, 7-year retention
```

---

### 4. RBAC & Privacy

**Access Control Matrix:**

| Role                 | Data Access                                             | Example Query Restriction                                                                     |
| -------------------- | ------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **CEO**              | Org-wide aggregates ONLY (no names, no individual data) | `SELECT category, COUNT(*) FROM work_categories WHERE tenant_id = X GROUP BY category`        |
| **Manager**          | Direct reports ONLY (identifiable)                      | `WHERE actor_id IN (SELECT employee_id FROM org_hierarchy WHERE manager_id = SESSION_USER())` |
| **IT/Security**      | Full access with audit trail                            | All data, but every query logged to `access_audit_log`                                        |
| **Employee**         | Own data ONLY                                           | `WHERE actor_id = SESSION_USER()`                                                             |
| **External Auditor** | Anonymized aggregates ONLY                              | No PII, only statistical summaries                                                            |

**BigQuery Row-Level Security (RLS):**

```sql
-- CEO policy: Only aggregates, no individual access
CREATE ROW ACCESS POLICY ceo_aggregate_only
ON organizational_insights.work_categories
GRANT TO ('group:ceos@company.com')
FILTER USING (FALSE);  -- CEOs can't query this table directly
-- Instead, they query pre-aggregated materialized views

-- Manager policy: Direct reports only
CREATE ROW ACCESS POLICY manager_team_filter
ON organizational_insights.sso_events_raw
GRANT TO ('group:managers@company.com')
FILTER USING (
    actor_id IN (
        SELECT employee_id
        FROM organizational_insights.org_hierarchy
        WHERE manager_id = SESSION_USER()
    )
);

-- IT/Security policy: Full access with audit logging
CREATE ROW ACCESS POLICY it_full_access_audited
ON organizational_insights.sso_events_raw
GRANT TO ('group:it-security@company.com')
FILTER USING (TRUE);  -- Full access
-- Note: All queries from this group logged via BigQuery audit logs
```

**PII Handling:**

```
Sensitive Fields in SSO Logs:
├── actor.id (employee ID) → Hash with SHA-256 + salt per tenant
├── actor.displayName → Redact entirely for CEO dashboards
├── client.ipAddress → Anonymize last octet (e.g., 192.168.1.XXX)
├── client.geographicalContext.city → Keep (not PII)
└── target[].id (app ID) → Keep (not PII)

Data Retention:
├── Raw SSO events: 90 days in BigQuery (hot storage)
├── Aggregated metrics: 7 years in Iceberg (compliance)
└── PII purge: GDPR right-to-be-forgotten requests honored within 30 days
```

**Privacy-Preserving Analytics:**

```
Differential Privacy for CEO Dashboards:
- Add Laplace noise to small counts (< 10 users) to prevent re-identification
- Example: "Engineering: 7 employees" → "Engineering: 5-10 employees"
- Use BigQuery's differential privacy SQL functions

k-Anonymity:
- Ensure every reported group has ≥ k users (k=10 recommended)
- If "ML Engineer" has only 3 users → group into "Engineering (Other)"
```

---

### 5. Evaluation & Quality

**Ground Truth Labels:**

```
HR System Integration:
├── Extract: employee_id, job_title, department, hire_date
├── Map job titles to categories:
│   "Software Engineer" → Engineering
│   "Account Executive" → Sales
│   "Customer Success Manager" → Customer Support
└── Create labeled dataset: 500 employees across diverse roles

Evaluation Pipeline:
├── Run work categorizer on labeled users
├── Compare agent category vs HR job title
├── Accuracy = % of correct matches (Target: >80%)
├── Confusion matrix: Which categories are confused?
└── Iterate on prompt engineering to improve accuracy
```

**Explainability Testing:**

```
Manager Validation:
├── Show 50 managers their team's categorizations + reasoning
├── Survey: "Does this match reality?" (Yes/No + confidence 1-5)
├── Target: >85% "Yes" responses, >4.0/5 avg confidence
└── Use feedback to refine LLM prompts
```

**Multi-Role Categorization:**

```
Challenge: Many employees have multiple roles (e.g., "Engineering Manager")

Solution: Allow multiple categories with confidence scores
├── LLM outputs array of categories:
│   [
│     {"role": "Engineering", "confidence": 0.7, "time_allocation": "60%"},
│     {"role": "Management", "confidence": 0.6, "time_allocation": "40%"}
│   ]
├── Primary category = highest confidence
├── Secondary categories shown in dashboard with percentages
└── Enables hybrid role-based optimizations:
    "This Engineering Manager needs both dev tools AND leadership training"

Evaluation:
├── Compare to HR titles: "Engineering Manager" → should detect BOTH categories
├── Target: >75% accuracy for hybrid roles (harder than single-role)
└── Edge case: IC promoted to manager mid-quarter → watch for category drift
```

**Adaptability Testing (Key advantage of agentic over ML):**

```
New App Introduction:
├── Scenario: Company adopts "Linear" (project management tool)
├── Traditional ML: Requires retraining entire model (weeks)
├── Agentic workflow: Adapts immediately via few-shot learning
│   └── Prompt includes: "Linear is a project management tool
│                         similar to Jira. Update your reasoning."
├── Test: Does agent correctly incorporate Linear into categorization?
└── Success: Agent categorizes users with Linear as "Engineering" or "Product"
```

**A/B Testing Framework:**

```
Experiment: Work Categorizer Impact on Productivity
├── Control Group (1,000 employees):
│   └── Generic IT policies (no role-based optimizations)
├── Treatment Group (1,000 employees):
│   └── Role-specific optimizations based on work categorization
│       (e.g., reduced auth for engineers, bundled tools)
├── Metrics:
│   ├── Self-reported productivity (weekly survey: 1-5 scale)
│   ├── Time savings (measured via auth time, context switches)
│   ├── Task completion rate (sprint velocity for eng teams)
│   └── User satisfaction with IT tools (quarterly NPS)
├── Duration: 3 months
└── Success: Treatment group shows 10-15% productivity improvement
```

**Success Metrics:**
| Metric | Target | Measurement |
|--------|--------|-------------|
| **Accuracy** | >80% correct categorization | Compare to HR job titles |
| **Explainability** | >4.0/5 stakeholder confidence | Manager surveys |
| **Adoption** | >70% of recommendations implemented | IT team tracking |
| **Impact** | $1M+ quantified time savings in 6 months | A/B test results |
| **Latency** | <3 sec dashboard load time | p95 latency monitoring |
| **Cost** | <$5k/month LLM costs for 10k employees | BigQuery + LLM billing |

---

### 6. Tracing & Monitoring

**LLM Call Tracing (CRITICAL for agentic workflows):**

```json
Every LLM call logged to BigQuery table: "llm_call_traces"
{
  "trace_id": "abc123-def456",
  "timestamp": "2025-01-15T10:30:00Z",
  "agent": "work_categorizer",
  "user_id": "hash_abc123",
  "tenant_id": "fortune1000_client_42",

  "llm_calls": [
    {
      "call_id": "llm_1",
      "model": "claude-sonnet-4.5",
      "purpose": "categorize_work_pattern",
      "prompt_tokens": 850,
      "completion_tokens": 420,
      "cost_usd": 0.0128,
      "latency_ms": 1850,
      "prompt_version": "v2.3",
      "temperature": 0.2,
      "max_tokens": 500
    },
    {
      "call_id": "llm_2",
      "model": "claude-sonnet-4.5",
      "purpose": "suggest_optimizations",
      "prompt_tokens": 650,
      "completion_tokens": 380,
      "cost_usd": 0.0104,
      "latency_ms": 1620,
      "prompt_version": "v1.8",
      "temperature": 0.3,
      "max_tokens": 400
    }
  ],

  "total_cost_usd": 0.0232,
  "total_latency_ms": 3470,
  "category_output": "Software Engineer (Frontend)",
  "confidence": 0.95,
  "error": null
}
```

**Monitoring Dashboards (Grafana + BigQuery):**

```
1. LLM Cost Dashboard
   ├── Total LLM spend: $X/day, $Y/month
   ├── Cost per client (top 10 by spend)
   ├── Cost per agent type (work categorizer, auth advisor, etc.)
   └── Alert: If daily cost > $500 (10% over budget)

2. LLM Performance Dashboard
   ├── p50, p95, p99 latency by agent type
   ├── Error rate (timeouts, rate limits, invalid responses)
   ├── Token usage trends (prompt vs completion)
   └── Alert: If p95 latency > 5 seconds

3. Agent Quality Dashboard
   ├── Categorization accuracy (vs ground truth)
   ├── Confidence score distribution
   ├── User feedback ratings (helpfulness 1-5)
   └── Alert: If accuracy drops below 75%

4. Data Pipeline Dashboard
   ├── BigQuery query costs (top 10 expensive queries)
   ├── Data freshness (time since last refresh)
   ├── Ingestion lag (SSO event → BigQuery)
   └── Alert: If ingestion lag > 5 minutes
```

**Error Tracking & Alerting:**

```
Scenarios to Monitor:
├── LLM timeout (> 10 seconds)
├── LLM rate limit exceeded (429 errors)
├── Invalid LLM response (unparseable JSON)
├── Low confidence categorization (< 0.6)
├── BigQuery quota exceeded
├── Data pipeline failure (Cloud Run job fails)
└── Dashboard load time > 5 seconds

Alert Routing:
├── Critical (PagerDuty): Data pipeline down, BigQuery quota exceeded
├── Warning (Slack): LLM latency p95 > 5 sec, cost > budget
└── Info (Email): Weekly summary of agent performance
```

**Prompt Version Control:**

```
Git Repository: "parable-prompts"
├── prompts/
│   ├── work_categorizer_v2.3.txt (current production)
│   ├── work_categorizer_v2.2.txt (previous)
│   └── work_categorizer_v2.4_beta.txt (A/B testing)
├── Track which prompt version generated which categorization
├── A/B test new prompts before rolling out to all users
└── Rollback if new prompt version degrades quality
```

---

### 7. Scale & Performance

**Petabyte-Scale Data Processing:**

```
Current State: 18 events (sample)
Production State: 1 billion events/day across 50 clients

Scaling Strategy:
├── Partition BigQuery tables by date + client (tenant_id)
├── Cluster by actor_id, target_id for query performance
├── Materialize common aggregations to avoid full scans
└── Archive events > 90 days to Iceberg (cheaper storage)

Example Query Optimization:
-- BAD: Full table scan (scans 365 TB!)
SELECT actor_id, COUNT(*)
FROM sso_events_raw
WHERE published > '2024-01-01';

-- GOOD: Partition pruning + clustering (scans 100 GB)
SELECT actor_id, COUNT(*)
FROM sso_events_raw
WHERE published BETWEEN '2025-01-01' AND '2025-01-31'  -- Partition pruning
  AND tenant_id = 'fortune1000_client_42'              -- Cluster pruning
GROUP BY actor_id;
```

**Latency Optimization:**

```
CEO Dashboard Requirements: < 3 seconds load time

Techniques:
├── 1. Materialized Views (refresh every 6 hours)
│   └── Pre-aggregate work category distributions, productivity metrics
├── 2. BigQuery BI Engine (in-memory cache)
│   └── Cache 100 GB of hot data for sub-second queries
├── 3. Frontend Caching (Memorystore Redis)
│   └── Cache dashboard JSON for 1 hour
└── 4. Lazy Loading (only fetch visible charts initially)

Latency Budget Breakdown (3 sec total):
├── Frontend render: 500ms
├── API call: 200ms
├── BigQuery query (cached materialized view): 800ms
├── Data serialization: 200ms
└── Network: 300ms
```

**Cost Optimization:**

```
Monthly Costs for 50 Clients × 10k Employees (500k users):

BigQuery:
├── Storage: 365 TB @ $20/TB/month = $7,300/month
├── Queries: ~$50k-100k/month (depends on usage)
└── Optimization: Materialize views, partition pruning

LLM (Work Categorizer):
├── 500k users ÷ 90 days = 5,556 categorizations/day
├── $0.02 per categorization × 5,556 = $111/day
└── Monthly: $3,330/month (very cheap!)

Cloud Run:
├── Batch jobs: $500/month (2 hrs/day processing)
└── API endpoints: $2k/month (auto-scaling)

Pub/Sub:
├── 1 billion messages/day @ $40/million = $40/day
└── Monthly: $1,200/month

Total: ~$64k-114k/month for 500k users
Per user: $0.13-0.23/month (very reasonable!)
```

**Infrastructure (GCP Single-Tenant Architecture):**

```
Per Client (Fortune 1000 company):
├── Isolated GCP Project
│   └── VPC, KMS keys, service accounts (no shared resources)
├── Dedicated BigQuery dataset
│   └── Row-level security enforced per tenant_id
├── Dedicated Cloud Run services
│   └── Environment variables configure client-specific settings
└── Shared Code Pipeline
    └── Same Docker image deployed across all client projects
    └── Parameterized by tenant_id
```

**Failure Scenarios & Disaster Recovery:**

```
1. BigQuery Outage
   ├── Problem: BigQuery region goes down, CEO dashboard unavailable
   ├── Mitigation:
   │   ├── Multi-region BigQuery dataset replication (us-central1 + us-east1)
   │   ├── Fallback to cached dashboard data (Memorystore Redis, 1 hour stale)
   │   ├── Read replicas in secondary region (eventual consistency, <5 min lag)
   │   └── Graceful degradation: Show "Data delayed" banner, serve cached results
   └── SLA: 99.9% uptime (8.76 hrs downtime/year acceptable)

2. LLM API Rate Limits / Outages
   ├── Problem: Anthropic API rate limits hit during batch job (429 errors)
   ├── Mitigation:
   │   ├── Exponential backoff with jitter (retry after 1s, 2s, 4s, 8s...)
   │   ├── Circuit breaker: Pause batch job if error rate > 10%
   │   ├── Fallback to cached categorizations (use yesterday's results)
   │   ├── Multi-provider strategy: Fallback to OpenAI GPT-4 if Claude unavailable
   │   └── Queue overflow handling: Defer low-priority recategorizations
   └── Monitoring: Alert on-call if LLM error rate > 5%

3. Data Pipeline Failure
   ├── Problem: Cloud Run job crashes during batch processing
   ├── Mitigation:
   │   ├── Checkpointing: Store progress every 500 users processed
   │   ├── Auto-restart from last checkpoint (don't reprocess 5,000 users)
   │   ├── Idempotency: Safe to retry same user multiple times
   │   ├── Dead letter queue: Users that consistently fail → manual review
   │   └── Parallel sharding: Process 10 shards of 556 users concurrently
   │       (if shard 3 fails, shards 1-2, 4-10 continue)
   └── Alert: PagerDuty notification if batch job fails 3 times

4. Data Corruption / Bad LLM Outputs
   ├── Problem: LLM hallucinates and categorizes all users as "CEO"
   ├── Mitigation:
   │   ├── Validation layer: Reject if confidence < 0.6 or category not in allowlist
   │   ├── Anomaly detection: Alert if >20% of users change category in one batch
   │   ├── Rollback mechanism: Store previous 3 categorization versions
   │   ├── Canary deployment: Test new prompt on 1% of users before full rollout
   │   └── Human review queue: Flag suspicious categorizations for manager override
   └── Recovery: Rollback to previous categorization version (stored in BigQuery)

5. Cost Overrun
   ├── Problem: LLM costs spike from $3k/month to $30k/month unexpectedly
   ├── Mitigation:
   │   ├── Budget alerts: Alert at 80% and 100% of monthly budget
   │   ├── Auto-throttling: Pause batch jobs if daily spend > 2× expected
   │   ├── Cost attribution: Track per-client spend (identify which client driving costs)
   │   └── Emergency shutdown: Kill switch to halt all LLM calls if needed
   └── Root cause analysis: Review tracing logs to identify cost spike source
```

---

## 📊 Interview Talking Points: System Design

### Opening (2 min)

**Interviewer:** "Great analysis! Now how would you build a production system to deliver these insights?"

**You:** "I'd design an agentic workflow that runs at petabyte scale for Fortune 1000 clients. Let me break this down into 7 key areas: business requirements, agent architecture, data pipeline, RBAC, evaluation, tracing, and scale. Should I start with the agent design since that's the core deliverable, or would you prefer to discuss data pipeline first?"

### Agent Architecture (5 min)

"The Work Categorizer Agent uses LLM + tool calling rather than traditional ML. Here's why:

**Traditional ML approach:** Train k-means clustering, get 'User in cluster 3' - not explainable to CEOs.

**Agentic approach:**

1. Agent queries BigQuery for user's app access patterns (last 90 days)
2. LLM analyzes with few-shot prompting: 'Given GitHub: 250 accesses, Slack: 180, Jira: 90, what type of work does this user do?'
3. LLM responds: 'Software Engineer (Frontend) BECAUSE heavy GitHub + Jira + Figma usage. Confidence: 95%.'
4. Agent suggests optimizations: 'Reduce auth steps for dev tools, bundle GitHub+Jira+Slack, alert on excessive Slack switching. Potential savings: 3-5 hrs/week per engineer = $1.5M-2.5M/year for 200 engineers.'

The key advantage: explainability for CEOs, adaptability to new apps without retraining, and natural language output."

### Data Pipeline (5 min)

"At Parable scale, we're processing 1 billion SSO events per day across 50 Fortune 1000 clients:

**Ingestion:** SSO providers (Okta, Google) → Pub/Sub → Cloud Run → BigQuery
**Storage:** BigQuery partitioned by date + tenant_id, clustered by actor_id
**Processing:** Nightly Cloud Run batch job categorizes 5,556 users/day
**Scale:** 365 TB/year in BigQuery, archived to Iceberg after 90 days

**Single-tenant architecture:** Each client gets isolated GCP project, VPC, KMS keys. No shared data, but shared parameterized pipeline code."

### RBAC & Privacy (3 min)

"Row-level security in BigQuery:

- CEOs see only org-wide aggregates (no individual names)
- Managers see direct reports only
- IT/Security has full access with audit trail
- Employees see only their own data

PII handling: Hash employee IDs, anonymize IP addresses, add differential privacy noise to small groups."

### Evaluation (3 min)

"Three-pronged validation:

1. **Ground truth:** Compare agent categories to HR job titles (Target: >80% accuracy)
2. **Explainability:** Show managers categorizations, survey 'Does this match reality?' (Target: >85% yes)
3. **A/B test:** Treatment group gets role-based optimizations, control group generic policies. Measure productivity improvement (Target: 10-15% gain)"

### Tracing (2 min)

"Every LLM call logged to BigQuery with full metadata: model, tokens, cost, latency, prompt version. This enables:

- Cost monitoring: Alert if daily LLM spend > $500
- Performance monitoring: Alert if p95 latency > 5 sec
- Quality monitoring: Track accuracy vs ground truth
- Prompt version control: A/B test new prompts before rollout"

### Scale & Cost (3 min)

"At 500k users:

- LLM costs: ~$3.3k/month (very cheap! $0.02 per categorization)
- BigQuery: ~$60k-110k/month (storage + queries)
- Total: ~$0.13-0.23 per user/month

Latency: CEO dashboards load in <3 sec via materialized views + caching

Cost optimization: Partition pruning, materialize common aggregations, archive old data to Iceberg"

---

## 🎨 Whiteboard Diagram: Work Categorizer Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CEO DASHBOARD                               │
│  "Engineering (45%): $2.1M/year opportunity in tool friction"       │
└─────────────────────────────────────────────────────────────────────┘
                              ↑
                              │ Query (< 3 sec)
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                   BIGQUERY (Materialized Views)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ work_        │  │ productivity_│  │ sso_events_  │              │
│  │ categories   │  │ metrics      │  │ raw          │              │
│  │ (500k users) │  │ (aggregated) │  │ (365 TB)     │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
         ↑                                        ↑
         │ Write categorizations                 │ Ingest SSO events
         │ (nightly batch)                       │ (real-time stream)
         ↓                                        ↓
┌────────────────────────────┐      ┌────────────────────────────┐
│  CLOUD RUN JOB             │      │  PUB/SUB + CLOUD RUN       │
│  "work-categorizer-batch"  │      │  "sso-event-ingestion"     │
│                            │      │                            │
│  For each user:            │      │  Parse, validate, enrich   │
│  1. Query app history      │◄─────┤  SSO events from Okta/etc  │
│  2. Call Work Categorizer  │      │                            │
│     Agent (LLM)            │      └────────────────────────────┘
│  3. Store result           │                   ↑
│                            │                   │ Webhooks
└────────────────────────────┘                   │
         ↓                                       │
         │ 2 LLM calls per user          ┌──────────────────┐
         ↓                               │  SSO PROVIDERS   │
┌────────────────────────────┐           │  (Okta, Google)  │
│  WORK CATEGORIZER AGENT    │           │                  │
│                            │           │  1B events/day   │
│  Tools:                    │           └──────────────────┘
│  • query_user_app_history  │
│  • query_app_cooccurrence  │
│  • categorize (LLM)        │
│  • explain (LLM)           │
│  • suggest_optimizations   │
│                            │
│  Output: Category +        │
│          Confidence +      │
│          Reasoning +       │
│          Recommendations   │
└────────────────────────────┘
         ↓
         │ All LLM calls traced
         ↓
┌────────────────────────────┐
│  TRACING & MONITORING      │
│  • Cost: $3.3k/month       │
│  • Latency: p95 < 3 sec    │
│  • Accuracy: >80%          │
│  • Alerts: Slack/PagerDuty │
└────────────────────────────┘
```

---

## 🗣️ Common Interview Questions & Answers

### Q: "How would this handle 100x scale growth?"

**A:** "Great question. Let's say we grow from 500k to 50M users:

**Bottlenecks:**

1. LLM costs: $3.3k/month → $330k/month (still reasonable, 1/3 of BigQuery costs)
2. BigQuery queries: Need aggressive caching, may hit quotas
3. Batch processing: 5,556 users/day → 555k users/day

**Solutions:**

1. **Sampling:** Categorize power users (>50 app accesses/month) weekly, casual users monthly
   - Reduces from 555k/day to ~150k/day (70% reduction)
2. **Incremental updates:** Only recategorize when significant pattern change detected
   - Further reduces to ~50k/day (saves $200k/month in LLM costs)
3. **Distributed processing:** Shard Cloud Run jobs by tenant_id, run in parallel
   - 100 shards × 500 users each = 2 hours → 20 minutes with parallelization
4. **Response caching:** For common app signatures, cache LLM responses
   - 'GitHub+Jira+Slack' always → 'Engineering' (no LLM call needed)
   - Cache hit rate ~40% → saves $120k/month
5. **BigQuery BI Engine:** Cache 1 TB of hot data in-memory for sub-second queries
   - Dashboard queries drop from $50k to $10k/month

**Cost at 50M users with optimizations:**

- LLM: $330k/month → $110k/month (caching + sampling)
- BigQuery: $100k/month → $150k/month (scales sub-linearly with caching)
- Infrastructure: $10k/month → $40k/month (distributed compute)
- **Total: ~$300k/month = $3.60/year per user** (economies of scale!)

Much cheaper than current $0.13-0.23/month × 12 = $1.56-2.76/year because of caching and sampling."

---

### Q: "What if the LLM hallucinates or gives wrong categories?"

**A:** "Excellent question. Three layers of defense:

**1. Validation layer (pre-LLM):**

- Require minimum data: ≥30 days of app accesses, ≥10 events
- Reject nonsensical inputs (e.g., user with 0 app accesses)

**2. Confidence thresholding (post-LLM):**

- LLM must output confidence score (0-1)
- If confidence < 0.6 → flag as 'Uncertain, needs manual review'
- Show these to managers for validation

**3. Human-in-the-loop (ongoing):**

- Managers can override agent categories ('This is wrong, user is actually a PM not Eng')
- Use overrides as ground truth for model retraining (few-shot examples in prompt)
- A/B test prompt improvements before rolling out

**Safety mechanism:**

- Never make automated IT policy changes based solely on agent output
- Always surface to manager/IT for approval
- Treat agent as 'recommendation engine' not 'decision engine'

**Monitoring:**

- Track manager override rate (if > 30% → prompt needs improvement)
- Track user feedback ('Was this categorization helpful?' 1-5 rating)
- Alert if accuracy drops below 75%"

---

### Q: "How do you handle data privacy regulations like GDPR?"

**A:** "Privacy-by-design architecture:

**1. Data minimization:**

- Only collect SSO logs necessary for categorization (app access, timestamp)
- Don't log app CONTENT (e.g., email body, Slack messages)

**2. Anonymization:**

- Hash employee IDs with tenant-specific salt
- CEO dashboards show aggregates only (no individual names)

**3. Access controls:**

- Row-level security in BigQuery (managers see only direct reports)
- Audit log every data access (who, what, when)

**4. Right-to-be-forgotten:**

- GDPR deletion request → purge user from BigQuery + Iceberg within 30 days
- Recalculate aggregates without that user

**5. Differential privacy:**

- Add Laplace noise to small groups (< 10 users) to prevent re-identification
- k-anonymity: Every reported group has ≥ 10 users

**6. Data residency:**

- EU clients → GCP europe-west1 region (GDPR-compliant)
- US clients → GCP us-central1 region

**7. Consent:**

- Employee onboarding: 'Your work tool usage will be analyzed to improve productivity. Opt-out available.'
- Opt-out: User data excluded from analysis (but still logged for security/compliance)"

---

### Q: "Why agentic workflow instead of just training a classifier?"

**A:** "Great question - this is the core of Parable's value prop. Let me contrast:

**Traditional ML Classifier:**

```
Input: User app usage vector [GitHub: 0.4, Slack: 0.3, Jira: 0.15, ...]
Model: Random Forest / SVM / Neural Net
Output: Class label [0, 1, 2, 3] → 'Cluster 3'
```

**Problems:**

1. **Not explainable:** Why is user in cluster 3? Black box.
2. **Not CEO-friendly:** 'Cluster 3' means nothing. Need data scientist to interpret.
3. **Requires retraining:** New app (Linear) added → retrain entire model (weeks of work)
4. **No natural language:** Can't say 'User is Engineer BECAUSE...'
5. **Static:** Can't adapt to edge cases or ask follow-up questions

**Agentic Workflow:**

```
Input: User app usage metrics
Agent: LLM with tools (query, analyze, explain)
Output: "Software Engineer (Frontend/Full-stack). Confidence: 95%.
         Reasoning: Heavy GitHub usage (250 accesses) indicates active coding.
         Jira access (90) suggests agile workflow. Figma access (30) suggests
         frontend work. This pattern matches typical frontend engineer signature.
         Recommendation: Reduce auth steps for GitHub/Jira, bundle dev tools."
```

**Advantages:**

1. **Explainable:** LLM provides reasoning with citations to raw data
2. **CEO-friendly:** Natural language anyone can understand
3. **Adapts immediately:** New app → just update prompt, no retraining
4. **Handles edge cases:** User with unusual app combo → LLM can reason through it
5. **Actionable:** Provides recommendations, not just labels

**When would you use traditional ML?**

- High-frequency, low-latency predictions (< 100ms) → ML model in memory
- Well-defined, narrow task with tons of labeled data → supervised learning
- Cost-sensitive (millions of predictions/day) → ML inference cheaper than LLM

**For Parable:**

- CEO-facing insights (explainability critical) → Agentic
- Adaptability to new apps (no retraining) → Agentic
- Modest scale (5,556 categorizations/day) → LLM costs acceptable ($3.3k/month)"

---

### Q: "Why not implement the agent in TypeScript since that's Parable's primary language?"

**A:** "Great question - the job description does emphasize TypeScript. Here's how I'd approach it:

**Recommended Architecture:**

- **Orchestration layer: TypeScript** (Parable's primary language)

  - API endpoints (Express.js or Fastify)
  - Job scheduling (Cloud Scheduler → TypeScript Cloud Run)
  - Business logic, data transformations
  - BigQuery queries (using @google-cloud/bigquery TypeScript client)

- **LLM agent layer: TypeScript OR Python** (both work well)
  - TypeScript option: Use Anthropic's TypeScript SDK + LangChain.js
    - Pros: Single language, easier for Parable team to maintain
    - Cons: LangChain.js less mature than Python version
  - Python option: Lightweight Python microservice just for agent logic
    - Pros: Rich ecosystem (LangChain, better prompt libraries)
    - Cons: Extra deployment complexity

**My recommendation for Parable:**
Go full TypeScript to match team skillset. Here's why:

1. **Team consistency:** Job description requires 'strong TypeScript skills'
2. **Maintainability:** One language = simpler codebase
3. **Anthropic SDK:** TypeScript SDK is production-ready
4. **Example TypeScript agent:**

```typescript
import Anthropic from "@anthropic-ai/sdk";

async function categorizeUser(userId: string): Promise<WorkCategory> {
  const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

  // Tool: Query BigQuery for user app history
  const appHistory = await queryUserAppHistory(userId, 90);

  // LLM call with structured output
  const response = await client.messages.create({
    model: "claude-sonnet-4.5",
    max_tokens: 500,
    messages: [
      {
        role: "user",
        content: buildPrompt(appHistory) // Prompt template
      }
    ]
  });

  // Parse JSON response
  const category: WorkCategory = JSON.parse(response.content[0].text);

  // Tracing: Log to BigQuery
  await logLLMCall({
    userId,
    model: "claude-sonnet-4.5",
    promptTokens: response.usage.input_tokens,
    completionTokens: response.usage.output_tokens,
    cost: calculateCost(response.usage),
    latency: response.latencyMs,
    category: category.category,
    confidence: category.confidence
  });

  return category;
}
```

**This shows:**

- TypeScript can absolutely handle agentic workflows
- Maintains Parable's tech stack consistency
- Production-ready with tracing, error handling
- Team can maintain without Python expertise"

---

### Q: "Why nightly batch instead of real-time categorization?"

**A:** "Excellent question - this is a deliberate trade-off. Let me explain:

**Real-Time Categorization:**

```
Every SSO event → Trigger categorization → LLM call
Pros: Always up-to-date
Cons:
  - Expensive: 1 billion events/day × $0.02 = $20M/day in LLM costs!
  - Noisy: Category fluctuates daily based on single app access
  - Latency: 2-second LLM call delays SSO login flow
  - Unnecessary: Work category doesn't change daily
```

**Nightly Batch Categorization:**

```
Aggregate 90 days → Categorize once → Cache result
Pros:
  - Cheap: 5,556 users/day × $0.02 = $111/day (1,800x cheaper!)
  - Stable: Category based on 90-day trend, not daily noise
  - No latency impact: Doesn't block SSO login
  - Accurate: Long-term patterns more predictive than single day
Cons:
  - Stale: Up to 24 hours delay for category updates
  - Miss rapid changes: User promoted yesterday, category updates tomorrow
```

**Hybrid Approach (Best of Both Worlds):**

```
1. Nightly batch: Standard recategorization every 90 days
2. Real-time triggers for events:
   - Manager override: "This category is wrong" → immediate recategorization
   - Anomaly detection: User accesses 5+ new apps in one day → trigger review
   - New hire onboarding: First 30 days → weekly categorization (more dynamic)
3. Incremental updates: Daily pattern change score (cheap SQL heuristic)
   - If score > threshold → queue for next batch run
```

**For Parable's use case:**
Nightly batch with real-time triggers is optimal because:

- Work categories are stable (engineers don't become salespeople overnight)
- CEO dashboards show trends (weekly/monthly), not real-time
- Cost savings are massive ($111/day vs $20M/day)
- Can still handle rapid changes via trigger system"

---

### Q: "How would you roll this out to 50 existing Parable clients?"

**A:** "Great question - rolling out a new feature to Fortune 1000 clients requires careful phasing. Here's my approach:

**Phase 1: Single Pilot Client (Weeks 1-2)**

```
Goal: Validate core functionality with one friendly client
Client: Mid-size company (5k employees), tech-savvy IT team

Activities:
├── Deploy work categorizer to pilot client's isolated GCP project
├── Run categorization on all 5k employees
├── Manual validation: IT team reviews 100 random categorizations
│   └── Target: >80% accuracy before proceeding
├── Show CEO dashboard to client executives
│   └── Gather feedback: Is this useful? What's missing?
├── Iterate on prompt based on feedback
│   └── Example: Client uses "Product Engineering" not "Engineering"
│         → Update prompt with client-specific terminology
└── Measure: Latency, cost, accuracy, user feedback

Success criteria:
- >80% categorization accuracy
- <3 sec dashboard load time
- Positive feedback from client CEO
- No production incidents
```

**Phase 2: Beta Rollout (Weeks 3-4)**

```
Goal: Validate at scale with 5 diverse clients
Clients: Mix of industries (finance, healthcare, tech, retail, manufacturing)

Activities:
├── Deploy to 5 clients (50k employees total)
├── A/B test within each client:
│   ├── 50% of employees: Get role-based optimizations
│   └── 50% control: Generic IT policies
├── Measure productivity impact:
│   ├── Self-reported productivity surveys (weekly)
│   ├── Auth time reduction (from SSO logs)
│   ├── Context switching reduction (time gaps between app accesses)
│   └── Manager satisfaction with recommendations
├── Collect edge cases:
│   └── Example: Healthcare client has "Nurse" category not in our prompt
│         → Add healthcare-specific roles to prompt
└── Cost monitoring: Ensure LLM costs align with projections

Success criteria:
- Treatment group shows 10-15% productivity improvement
- All clients report >4.0/5 satisfaction with insights
- No cost overruns (actual within 20% of projected)
- Prompt handles diverse industries without major customization
```

**Phase 3: Gradual Rollout (Weeks 5-12)**

```
Goal: Scale to all 50 clients (500k employees) with risk mitigation
Strategy: 10% per week (5 clients/week)

Week-by-week:
├── Week 5: 10 clients (100k employees)
├── Week 6: 15 clients (150k employees)
├── Week 7: 20 clients (200k employees)
├── ...
└── Week 12: 50 clients (500k employees) ✅

Risk mitigation:
├── Gradual increases allow monitoring for issues
├── Rollback capability: If week 6 shows problems, pause rollout
├── Canary monitoring: Alert if any metric degrades
│   ├── Accuracy drops below 75%
│   ├── LLM costs spike >50% from projection
│   ├── Dashboard latency >5 sec
│   └── Error rate >5%
└── Client-by-client customization:
    └── Some clients need industry-specific categories (add to prompt)

Parallel activities:
├── Onboarding docs for each client IT team
├── CEO dashboard training sessions
├── Slack channel for client feedback
└── Weekly status updates to Parable leadership
```

**Phase 4: Production Monitoring & Iteration (Week 13+)**

```
Goal: Continuous improvement based on production data

Activities:
├── Aggregate metrics across all 50 clients:
│   ├── Overall categorization accuracy (target: >80%)
│   ├── Productivity improvement (target: 10-15%)
│   ├── ROI delivered (target: $1M+ time savings in 6 months)
│   └── Client satisfaction (target: >90% renewal rate)
├── Identify improvement opportunities:
│   └── Example: Accuracy for "Product Manager" category is 65%
│         → Add more PM-specific app patterns to prompt
├── Prompt iteration:
│   ├── A/B test new prompts with 10% of users
│   ├── Roll out improvements if accuracy increases >5%
│   └── Track prompt version performance over time
└── Feature expansion based on client requests:
    └── Example: Client wants "Team collaboration score" in addition to categorization

Success criteria:
- 100% of clients live with no major incidents
- Demonstrable productivity gains (quantified ROI)
- Feature requests prioritized for next quarter
- System scales to projected costs and latency
```

**Key Principles:**

1. **Start small:** 1 client → 5 clients → 50 clients (de-risk)
2. **Measure everything:** Accuracy, cost, latency, productivity, satisfaction
3. **Rollback ready:** Can revert any client if issues arise
4. **Client-specific:** Allow customization (industry terminology, categories)
5. **Gradual scale:** 10% per week allows catching issues early

This phased approach ensures we deliver value to Fortune 1000 clients without risking their production environments."

---

_For tips and checklists, see INTERVIEW_TIPS_AND_CHECKLISTS.md_
