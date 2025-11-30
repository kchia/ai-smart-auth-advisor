## Production Scale Reality

**Sample vs Reality Gap**

### **Sample Data (This Dataset):**

- **18 events** from **10 users** over **1 day**
- **11 unique applications**
- **~2 events per user per day**
- **File size:** ~50 KB

### **Typical Enterprise (1,000 employees):**

- **200,000 events/day** (1,000 users × 200 events/day)
- **~100 unique applications**
- **~200 events per user per day** (every app access, re-auth, logout)
- **File size:** ~500 MB/day, **15 GB/month**, **180 GB/year**
- **BigQuery cost:** ~$9/month for storage, $100-500/month for queries

### **Fortune 1000 Company (100,000 employees):**

- **20,000,000 events/day** = **20 million rows/day**
- **~500 unique applications**
- **File size:** **50 GB/day**, **1.5 TB/month**, **18 TB/year**
- **BigQuery cost:** ~$300/month storage, $5,000-20,000/month for queries

### **Parable Scale (Multiple Fortune 1000 Clients):**

- **Clients:** 50+ Fortune 1000 companies
- **Total daily events:** **1 billion events/day**
- **Total data:** **2.5 TB/day**, **75 TB/month**, **900 TB/year** (**~1 PB/year**)
- **Infrastructure:** GCP single-tenant per customer (50+ isolated VPCs)
- **Cost:** $15k/month storage, $100k-500k/month queries at scale
- **Latency requirements:** CEO dashboards must load in < 3 seconds

**This is "petabyte-scale" they mention in the job description.**

### **Performance Implications**

#### **Query Optimization Required:**

**Bad Query (works on 18 events, fails at scale):**

```sql
-- This works on sample data
SELECT actor.id, COUNT(*)
FROM events
GROUP BY actor.id;
```

**Good Query (production-ready):**

```sql
-- Partitioned by date, clustered by actor.id
SELECT actor.id, COUNT(*)
FROM `project.dataset.sso_events_partitioned`
WHERE published BETWEEN '2025-01-01' AND '2025-01-31'  -- Partition pruning
  AND actor.id IN UNNEST(@user_ids)  -- Parameter for RBAC
GROUP BY actor.id;
```

#### **Caching Strategy:**

**Problem:** CEO asks "Show me top 10 employees wasting time" - can't scan 1B rows in < 3 sec.

**Solution:** Materialized views + incremental updates

```sql
-- Materialized view (refreshed every 6 hours)
CREATE MATERIALIZED VIEW productivity_metrics_mv AS
SELECT
    actor.id,
    DATE(published) as date,
    COUNT(*) as total_events,
    AVG(authenticationContext.authenticationStep) as avg_auth_step,
    COUNT(DISTINCT target[].id) as unique_apps,
    -- Pre-calculated waste metrics
    (AVG(authenticationContext.authenticationStep) - 1) * 0.5 * COUNT(*) / 60.0 as auth_waste_hours,
    (COUNT(DISTINCT target[].id) * 5) / 60.0 as context_switch_waste_hours
FROM events
WHERE published >= CURRENT_DATE() - 90  -- Rolling 90 days
GROUP BY actor.id, DATE(published);

-- CEO query now scans materialized view (1M rows) instead of raw events (1B rows)
SELECT * FROM productivity_metrics_mv ORDER BY auth_waste_hours DESC LIMIT 10;
```

#### **Partitioning Strategy:**

```sql
CREATE TABLE sso_events (
    published TIMESTAMP,
    actor STRUCT<id STRING, ...>,
    target ARRAY<STRUCT<...>>,
    ...
)
PARTITION BY DATE(published)  -- Daily partitions
CLUSTER BY actor.id, target[0].id;  -- Cluster for common queries

-- Automatic partition expiration (GDPR compliance)
ALTER TABLE sso_events
SET OPTIONS (
    partition_expiration_days = 730  -- 2 years
);
```

### **Cost Management**

**At petabyte scale, query costs add up fast:**

- **BigQuery pricing:** $6.25 per TB scanned
- **Scanning 1 PB:** $6,250 per query (!)
- **CEO dashboard with 10 queries:** $62,500 per dashboard load

**Cost optimization techniques:**

1. **Partition pruning:** Scan only relevant dates
2. **Clustering:** Reduce data scanned by clustering on common filters
3. **Materialized views:** Pre-aggregate common metrics
4. **BI Engine:** In-memory caching for dashboards ($100-500/month, saves $10k+ in query costs)
5. **Query quotas:** Limit per-user query budget
6. **Result caching:** Cache query results for 24 hours

### **Latency Constraints**

**Job description:** "Frontend latency constraints" - dashboards must be fast.

**CEO expectations:**

- **< 3 seconds:** Dashboard load time
- **< 1 second:** Filter updates
- **< 5 seconds:** Complex analysis (agentic workflow result)

**How to achieve at petabyte scale:**

1. **Pre-aggregation:** Compute daily/hourly aggregates, not on-demand
2. **Streaming:** Use Pub/Sub + Dataflow for real-time metrics
3. **Caching layers:** Redis/Memorystore for frequently accessed data
4. **Pagination:** Never load all 100k employees at once
5. **Lazy loading:** Load summary first, details on demand
6. **Progressive rendering:** Stream results as they arrive
7. **Agentic workflows:** Run async, notify when complete (for complex analysis)

### **Infrastructure at Scale**

**Parable's architecture (from job description):**

- **Single-tenant per customer:** Each Fortune 1000 client gets own VPC
- **Isolated compute:** Cloud Run Jobs, Compute Engine per customer
- **Isolated storage:** Cloud Storage buckets, BigQuery datasets per customer
- **Shared pipelines:** Parameterized pipelines instantiated per tenant
- **Customer-managed encryption:** Each customer has own KMS keys

**Why single-tenant?**

- **Data privacy:** Customer A can't see Customer B's data
- **Compliance:** Easier to meet regulatory requirements
- **Performance isolation:** One customer's query load doesn't affect others
- **Custom SLAs:** Different customers can have different performance guarantees

**Scaling challenge:**

- 50 customers = 50 VPCs, 50 BigQuery datasets, 50 Cloud Run deployments
- Infrastructure as code (Terraform) to manage all deployments
- Monitoring across 50 tenants

### **Real-Time vs Batch Processing**

**Sample data:** Batch load (all events have same load_utc_tstamp)

**Production:**

- **Real-time:** Okta → Pub/Sub → Dataflow → BigQuery streaming inserts (< 1 min latency)
- **Batch:** Daily aggregation jobs for complex metrics
- **Hybrid:** Real-time for dashboards, batch for ML training/evaluation

**Cost tradeoff:**

- **Streaming inserts:** $0.05 per GB = $500/day for 10 GB/day = $15k/month
- **Batch loads:** Free (up to 1,500 loads/day)
- **Decision:** Stream critical metrics, batch historical analysis
