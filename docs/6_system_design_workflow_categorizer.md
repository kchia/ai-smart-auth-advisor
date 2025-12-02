## 🎨 Whiteboard Diagram: Work Categorizer Architecture

### Single-Tenant View (Client A - 50k employees)

https://miro.com/app/board/uXjVJi6KsTw=/

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
