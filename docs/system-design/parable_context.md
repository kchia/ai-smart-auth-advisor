# Parable Context

---

## 🏢 About Parable

### **Company Overview**

- **Mission:** Make Time Matter - Help CEOs gain organizational observability
- **Product:** "Operating system for the enterprise"
- **What they do:** Connect petabytes of organizational data across siloed tools (Slack, Gmail, Salesforce, GitHub, Jira, SSO) and add a semantic layer
- **Customers:** C-suite executives at Fortune 1000 companies
- **Metrics:** $2M ARR in 6 months, $17M Series A funding
- **Team:** 11-50 employees, based in Brooklyn, NY
- **Investors:** HOF Capital, Story Ventures, 50+ founder/exec angels
- **Founders:** Multiple 9-figure exits (proven track record)

### **The 5 CEO Questions Parable Answers**

1. **Where is the bureaucracy?**
2. **Where is the friction?**
3. **Where is the waste?**
4. **Where can we automate?**
5. **How can we use AI to make my team 100x more productive?**

---

## 🔧 Tech Stack

### **Cloud & Infrastructure**

- **GCP** (primary cloud)
  - Cloud Run Jobs, Compute Engine
  - Pub/Sub (messaging)
  - Cloud Storage
  - Memorystore (Redis)
  - BigQuery (analytics)
  - Cloud SQL
  - Iceberg-based data lake

### **Architecture**

- **Single-tenant per customer** (each Fortune 1000 client gets own VPC)
- **Isolated compute, storage, KMS** per customer
- **Shared, parameterized pipelines** instantiated per tenant
- **No bespoke schema** per client (consistency)

---

## **Why Agentic Workflows > Traditional ML**

Parable's customers are CEOs who need explainable insights. An agentic
workflow can say 'Employee X wastes time BECAUSE...' with citations to
raw data. A clustering model says 'User in cluster 3' - that's not
actionable. At petabyte scale with hundreds of clients, explainability
and adaptability matter more than marginal accuracy gains.

**Traditional ML Approach:**

```
Train k-means clustering → "User is in cluster 3"
```

**Problems:**

- Not explainable to CEOs
- Requires retraining for new apps
- No natural language output
- Brittle edge cases

**Agentic Workflow Approach:**

```
LLM Agent with tools → "This user is an engineer BECAUSE they use GitHub, Jira, and Slack together 80% of the time. Confidence: 95%."
```

**Benefits:**

- Explainable with citations
- Adapts to new apps without retraining
- Natural language for CEOs
- Reasons through edge cases
- Few-shot learning (works with limited data)
