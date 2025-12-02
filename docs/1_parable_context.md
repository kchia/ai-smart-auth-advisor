# Parable Context

---

## 🏢 About Parable

### **Company Overview**

- **Mission:** Make Time Matter - Help CEOs gain organizational observability
- **Product:** "Operating system for the enterprise"
- **What they do:** Connect petabytes of organizational data across siloed tools (Slack, Gmail, Salesforce, GitHub, Jira, SSO) and add a semantic layer
- **Customers:** C-suite executives at Fortune 1000 companies

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
