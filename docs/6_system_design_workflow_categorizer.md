## 🎨 Whiteboard Diagram: Work Categorizer Architecture

### Single-Tenant View (Client A - 50k employees)

https://miro.com/app/board/uXjVJi6KsTw=/

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CEO DASHBOARD (Client A)                         │
│  "Engineering (45%): $2.1M/year opportunity in tool friction"       │
└─────────────────────────────────────────────────────────────────────┘
                              ↑
                              │ Query (< 3 sec)
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│              BIGQUERY (Client A - Isolated Dataset)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ work_        │  │ productivity_│  │ sso_events_  │              │
│  │ categories   │  │ metrics      │  │ raw          │              │
│  │ (50k users)  │  │ (aggregated) │  │ (30 TB)      │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
         ↑                                        ↑
         │ Write categorizations                 │ Ingest SSO events
         │ (~635 users/night, ~15 min)           │ (real-time stream)
         ↓                                        ↓
┌──────────────────────┐  ┌────────────────────────────┐      ┌─────────────────┐
│  HR SYSTEM           │  │  CLOUD RUN JOB             │      │  PUB/SUB +      │
│  (Workday/BambooHR)  │  │  "work-categorizer-batch"  │      │  CLOUD RUN      │
│                      │  │                            │      │                 │
│  Role changes        │──┤  EVENT-DRIVEN TRIGGERS:    │      │  Parse, validate│
│  New hires           │  │  • HR webhooks: ~10/day    │◄─────┤  enrich SSO     │
│  Promotions          │  │  • New hires: ~5/day       │      │  events         │
│                      │  │  • Periodic: ~600/day      │      │                 │
└──────────────────────┘  │  • Anomalies: ~5-10/day    │      └─────────────────┘
         webhooks         │  = ~635 users/day total    │               ↑
                          │                            │               │ Webhooks
                          │  For each triggered user:  │               │
                          │  1. Query 90-day history   │       ┌──────────────────┐
                          │  2. Call Categorizer Agent │       │  SSO PROVIDERS   │
                          │  3. Store result           │       │  (Okta, Google)  │
                          └────────────────────────────┘       │                  │
                                      ↓                        │  10M events/day  │
                                      │ 2 LLM calls per user   └──────────────────┘
                                      ↓
                          ┌────────────────────────────┐
                          │  WORK CATEGORIZER AGENT    │
                          │                            │
                          │  Tools:                    │
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
                          │  • Cost: $380/month        │
                          │  • Latency: p95 < 3 sec    │
                          │  • Accuracy: >80%          │
                          │  • Alerts: Slack/PagerDuty │
                          └────────────────────────────┘
```

---

### 🏗️ Architecture Context: Single-Tenant Deployment Model

**This diagram shows ONE client's architecture (Client A - 50,000 employees)**

We replicate this entire stack for each Fortune 1000 client. Each gets their own isolated deployment:

```
Client A (Acme - 50k employees)          Client B (TechCo - 100k employees)
┌─────────────────────────────┐          ┌─────────────────────────────┐
│  VPC A (isolated)           │          │  VPC B (isolated)           │
│  • BigQuery Dataset A       │          │  • BigQuery Dataset B       │
│  • Cloud Run Jobs A         │          │  • Cloud Run Jobs B         │
│  • KMS Keys A               │          │  • KMS Keys B               │
│  • Pub/Sub Topics A         │          │  • Pub/Sub Topics B         │
└─────────────────────────────┘          └─────────────────────────────┘
```

**What's Isolated vs. Shared:**

| Component               | Model                          | Rationale                                       |
| ----------------------- | ------------------------------ | ----------------------------------------------- |
| **BigQuery datasets**   | ✅ Isolated per tenant         | Data security, compliance (SOC2, HIPAA)         |
| **Cloud Run jobs**      | ✅ Isolated per tenant         | Resource isolation, blast radius containment    |
| **KMS encryption keys** | ✅ Isolated per tenant         | Customer owns their encryption keys             |
| **Pub/Sub topics**      | ✅ Isolated per tenant         | Event stream isolation                          |
| **VPC network**         | ✅ Isolated per tenant         | Network security boundary                       |
| **LLM API keys**        | 🔄 Shared (Parable-owned)      | Cost efficiency, rate limit pooling             |
| **Terraform pipelines** | 🔄 Shared, parameterized       | Same infra code, different variables per tenant |
| **Application code**    | 🔄 Shared (same Docker images) | No client customization, consistent behavior    |
| **Monitoring backend**  | 🔄 Shared, tenant-tagged       | Parable ops sees all, data tagged by tenant_id  |

**Interview Script (30 seconds):**

> "This diagram shows the Work Categorizer for **a single Fortune 1000 client** - let's call them Client A with **50,000 employees**.
>
> We use **single-tenant architecture** - each client gets their own isolated VPC, BigQuery dataset, Cloud Run jobs, and KMS encryption keys. Client A's data never touches Client B's infrastructure.
>
> We currently have **10 clients** (500k employees total), but let me walk through one tenant's deployment. What we share are the **parameterized Terraform pipelines** - same infrastructure code, different `tenant_id` variable - and the **application Docker images**. This gives us single-tenant security with multi-tenant operational efficiency."

---

## 🎤 System Walkthrough Script

### Opening Overview (30 seconds)

**[Gesture to entire diagram]**

> "Let me walk you through the Work Categorizer architecture for **a single 50,000-employee Fortune 1000 client**. This is a **batch processing system** that runs nightly to categorize users based on their 90-day app usage patterns.
>
> The key design decision: we're NOT doing real-time categorization because work patterns emerge over 90 days, not per-event. This saves massive costs while maintaining accuracy. We replicate this architecture for each client - currently serving 10 Fortune 1000 companies."

---

### 1️⃣ Data Ingestion Layer (Bottom → Up, 45 seconds)

**[Point to SSO Providers at bottom]**

> "Starting at the source: **SSO providers** - Okta, Google Workspace, Azure AD for this client. These generate authentication and app access events every time a user logs in or accesses an application."

**Event Volume (Client A - 50k employees):**

- **50k employees × 200 events/user/day = 10M events/day** for this client
- **Design capacity: 20M events/day** (2x headroom for growth)
- **Across all 10 clients: ~100M events/day aggregate** (but each tenant isolated)

**[Move to Pub/Sub + Cloud Run]**

> "Events stream through **Pub/Sub** via webhooks from SSO providers. Each tenant has their own Pub/Sub topic - Client A's events never touch Client B's infrastructure.
>
> The **Cloud Run ingestion service** parses, validates, and enriches each event in real-time. This is the only real-time component - we need fresh data for other use cases like security monitoring and anomaly detection."

**[Move to BigQuery sso_events_raw]**

> "Raw events land in **BigQuery** - partitioned by date, clustered by user_id for efficient queries. Client A's dataset contains **30 terabytes** - that's 2 years of retention for their 50k employees at 10M events/day.
>
> Each tenant has their own isolated dataset. Across all 10 clients, we're storing ~300TB total, but Client A only accesses their 30TB."

---

### 2️⃣ Categorization Pipeline (Middle, 75 seconds)

**[Point to Cloud Run Job]**

> "Every night at 2 AM UTC, Client A's **Cloud Run batch job** runs. It's isolated - only processes their 50k employees, never touches other clients' data.
>
> Here's the key: we DON'T recategorize all 50k users every night. Categories rarely change for stable employees - an engineer stays an engineer. Instead, we use **event-driven + periodic refresh**:
>
> **1. HR system webhooks:** ~10 users/day get promoted or change roles → recategorize them
>
> **2. New hire detection:** ~5 new employees/day complete onboarding → first categorization
>
> **3. Periodic defensive refresh:** Recategorize 1-2% daily (rotating through everyone over 60 days) to catch drift, prompt changes, edge cases → ~600 users/day
>
> **4. Anomaly detection:** ~5-10 users/day whose patterns diverged significantly from their category
>
> **Total: ~620-650 users recategorized/day** instead of 50k. This saves 99% of LLM costs while catching all real category changes."

**[Walk through the numbered steps]**

> "For each user who needs recategorization:
>
> **1. Query app history** - Pull their 90-day pattern from BigQuery: which apps, how many accesses
>
> **2. Call Work Categorizer Agent** - This is where the LLM comes in
>
> **3. Store result** - Write categorization back to BigQuery materialized view
>
> The whole batch takes about **15 minutes** for ~635 users - that's ~1.4 seconds per user including query time and LLM latency."

**[Point to Work Categorizer Agent]**

> "The agent orchestrates **five tools** in sequence:
>
> **Tool 1:** `query_user_app_history` - Gets the 90-day pattern (GitHub: 250, Jira: 90, Figma: 30)
>
> **Tool 2:** `query_app_cooccurrence` - Finds similar users for few-shot examples
>
> **Tool 3:** `categorize` - **LLM call #1** - Uses few-shot learning with industry benchmarks to assign role: 'Frontend Engineer'
>
> **Tool 4:** `explain` - **LLM call #2** - Generates natural language reasoning: 'Heavy GitHub + Jira + Figma indicates frontend work'
>
> **Tool 5:** `suggest_optimizations` - Maps category to role-specific productivity tips
>
> Notice I'm making **2 LLM calls per user** - categorize + explain. This is intentional for explainability. The categorization alone would be cheaper, but managers need to understand WHY."

**Cost Breakdown (Client A):**

- 2 LLM calls/user × $0.01/call = $0.02/user/categorization
- ~635 users/day × $0.02 = $12.70/day
- $12.70/day × 30 days = **$380/month in LLM costs**
- Infrastructure (BigQuery + Cloud Run + Pub/Sub): ~$1,800/month
- **Total: $2,180/month** for 50k employees
- **Unit economics: $0.044 per employee per month** ($2,180 ÷ 50k)
- Across 10 clients = ~$3,800/month aggregate LLM spend, ~$22k total

---

### 3️⃣ Storage & Access Layer (Top, 45 seconds)

**[Point to BigQuery materialized views]**

> "Categorization results are stored in three **materialized views** in Client A's dataset:
>
> **`work_categories`** - All 50k employees with their categorizations, confidence scores, reasoning, and recommendations. This is the source of truth for role-based features.
>
> **`productivity_metrics`** - Pre-aggregated metrics by role, team, department for Client A. Example: 'Engineering team (45% of company) has $2.1M/year friction opportunity in GitHub workflows.'
>
> **`sso_events_raw`** - The original 30TB dataset for ad-hoc analysis by Client A's data teams.
>
> Views refresh nightly after the batch completes - around 4 AM UTC."

**[Point to CEO Dashboard]**

> "Client A's CEO dashboard queries these materialized views - **sub-3-second response** because we pre-aggregated everything during the batch. No LLM calls at query time, no scanning the full 30TB raw dataset - just simple SQL on pre-computed tables.
>
> Example: 'Show me productivity opportunities by department' hits `productivity_metrics`, scans ~1MB, returns in under 3 seconds. The CEO is always looking at their 50k employees, never seeing other clients' data."

---

### 4️⃣ Observability & Monitoring (Right side, 30 seconds)

**[Point to Tracing & Monitoring]**

> "Every LLM call is traced with structured logging:
>
> **Cost tracking:** Running total per tenant, alert if any client exceeds $5k/month
>
> **Latency:** p95 under 3 seconds per categorization (p50 is ~1.5 seconds)
>
> **Accuracy:** Weekly sampled validation - compare 100 random categorizations to HR ground truth, target >80% accuracy
>
> **Alerts:** Slack for warnings (accuracy drops below 75%), PagerDuty for critical failures (batch doesn't complete within 4 hour SLA)
>
> This is multi-tenant monitoring - we see all clients in one dashboard, but data is tagged by `tenant_id` so we can drill down."

---

## 📊 Key Numbers Reference

### Client A (50k employees) - Single-Tenant View

| Metric                          | Value            | Context                                     |
| ------------------------------- | ---------------- | ------------------------------------------- |
| **Employees**                   | 50,000           | Fortune 1000 client                         |
| **Events per day**              | 10M              | 50k users × 200 events/user                 |
| **Design capacity**             | 20M events/day   | 2x headroom for growth                      |
| **BigQuery storage**            | 30 TB            | 2 years retention                           |
| **Users recategorized daily**   | ~635             | Event-driven + 1-2% periodic refresh        |
| **Categorization triggers**     | 4 types          | HR webhooks, new hires, periodic, anomalies |
| **LLM calls per user**          | 2                | Categorize (1) + Explain (1)                |
| **Batch duration**              | 15 min           | 635 users at ~1.4 sec/user                  |
| **Batch SLA**                   | 1 hour           | Must complete before 3 AM UTC               |
| **Dashboard query latency**     | <3 sec           | p95, materialized views                     |
| **Monthly LLM cost**            | $380             | 635/day × 30 days × $0.02                   |
| **Monthly infrastructure cost** | ~$1,800          | BigQuery + Cloud Run + Pub/Sub              |
| **Total monthly cost**          | ~$2,180          | LLM + infrastructure                        |
| **Cost per employee**           | **$0.044/month** | $2,180 ÷ 50k employees                      |
| **Accuracy target**             | >80%             | Validated against HR ground truth           |

### Aggregate Across All 10 Clients (For Context)

| Metric                 | Value   |
| ---------------------- | ------- |
| **Total employees**    | 500k    |
| **Total events/day**   | ~100M   |
| **Total storage**      | ~300 TB |
| **Monthly LLM cost**   | ~$3,800 |
| **Monthly total cost** | ~$22k   |

---

### Two-Minute Condensed Walkthrough

> "This is the Work Categorizer for **Client A - a 50,000-employee Fortune 1000 company**. We replicate this architecture for each client with full isolation.
>
> **Data flow:** Their SSO events from Okta stream through Pub/Sub into BigQuery in real-time - **10 million events per day**. That's stored in their isolated 30TB dataset with 2-year retention.
>
> **Categorization:** Every night, a Cloud Run batch job runs for ~15 minutes. Here's the smart part: we don't recategorize all 50k users - categories rarely change. Instead, we use **event-driven triggers**:
>
> - HR system webhooks when someone gets promoted (~10/day)
> - New hire detection when onboarding completes (~5/day)
> - Periodic refresh of 1-2% daily for defensive coverage (~600/day)
> - Anomaly detection for pattern divergence (~5-10/day)
>
> **Total: ~635 users/day**. For each, we call an LLM agent twice - once to categorize using few-shot learning, once to explain why. Costs **$380/month** in LLM calls.
>
> **Access:** Results are stored in materialized views. Client A's CEO dashboard queries these pre-aggregated tables - sub-3-second response, no LLM calls at query time, just SQL.
>
> **Isolation:** This entire stack is duplicated per client - they get their own VPC, BigQuery dataset, Cloud Run jobs, encryption keys. Client A's data never touches Client B's infrastructure. We use shared Terraform pipelines to deploy consistently - same code, different `tenant_id`.
>
> **Key design decisions:** Event-driven instead of recategorizing everyone daily saves 99% of costs. Batch instead of real-time saves another 99% ($100k/day → $13/day). Few-shot prompting adapts to new apps without retraining. Single-tenant isolation is non-negotiable for Fortune 1000 security. **Unit economics: 4.4 cents per employee per month** to enable $100M/year in productivity gains."

---
