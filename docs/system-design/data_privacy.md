## Data Privacy & RBAC Considerations

**Context:** Parable handles SSO logs for Fortune 1000 companies - highly sensitive data requiring strict access controls.

### **PII Fields in SSO Data**

| Field                          | PII Risk                                | Mitigation                                                                      |
| ------------------------------ | --------------------------------------- | ------------------------------------------------------------------------------- |
| `actor.id`                     | **HIGH** - Likely contains employee ID  | Hash or pseudonymize in analytics layer                                         |
| `actor.alternateId`            | **VERY HIGH** - Often contains email    | Must encrypt, restrict access to HR/managers only                               |
| `actor.displayName`            | **VERY HIGH** - Contains employee name  | Anonymize in dashboards, show only to authorized viewers                        |
| `client.ipAddress`             | **MEDIUM** - Can reveal location        | Aggregate to city/country level for non-IT users                                |
| `client.geographicalContext.*` | **MEDIUM** - Location tracking          | Aggregate for privacy, don't show individual traces                             |
| `target[].id`                  | **LOW** - App IDs usually not PII       | Generally safe, but could reveal sensitive app usage (mental health apps, etc.) |
| `debugContext.debugData.*`     | **VARIES** - May contain session tokens | Redact sensitive debug info in analytics                                        |

### **RBAC Requirements**

**Principle:** "Managers see their team only, CEOs see aggregates, IT sees everything"

#### **Access Level Matrix:**

| Role                  | Data Access                                   | Example Query Restriction                   |
| --------------------- | --------------------------------------------- | ------------------------------------------- |
| **CEO**               | Organization-wide aggregates only             | `GROUP BY department` - no individual names |
| **VP/Director**       | Department aggregates + manager-level details | `WHERE department = 'Engineering'`          |
| **Manager**           | Direct reports only, identifiable             | `WHERE actor.id IN (manager's_team_ids)`    |
| **IT/Security**       | Full access with audit trail                  | All data, but every query logged            |
| **Employee (Self)**   | Own data only                                 | `WHERE actor.id = current_user_id`          |
| **Contractor/Vendor** | No access                                     | Forbidden                                   |

#### **Implementation in BigQuery:**

```sql
-- Row-level security example
CREATE ROW ACCESS POLICY manager_team_filter
ON employee_sso_logs
GRANT TO ('group:managers@company.com')
FILTER USING (
    actor.id IN (
        SELECT employee_id
        FROM org_hierarchy
        WHERE manager_id = SESSION_USER()
    )
);

-- Column-level security
CREATE ROW ACCESS POLICY ceo_aggregates_only
ON employee_sso_logs
GRANT TO ('group:executives@company.com')
FILTER USING (
    -- Force GROUP BY, no individual rows
    COUNT(*) OVER (PARTITION BY actor.id) > 1
);
```

### **Data Retention & Deletion**

**GDPR/CCPA Compliance:**

- **Retention:** SSO logs should be retained for 90 days operational, 2 years for audit
- **Right to deletion:** Employee departure = anonymize within 30 days
- **Right to access:** Employees can request their own SSO history
- **Purpose limitation:** SSO data used ONLY for productivity analytics, not performance reviews (must be explicit in policy)

**Implementation:**

```sql
-- Anonymization job (runs nightly)
UPDATE employee_sso_logs
SET
    actor.id = SHA256(actor.id),
    actor.alternateId = 'deleted@example.com',
    actor.displayName = 'Former Employee'
WHERE
    actor.id IN (SELECT id FROM departed_employees)
    AND anonymized_at IS NULL;
```

### **Audit Trail Requirements**

**Every query must be logged:**

- Who queried
- What data (which users, time range)
- When
- Why (purpose field)
- Result set size

**Example audit log:**

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "user": "manager@company.com",
  "query": "SELECT actor.id, auth_waste_hours FROM productivity_metrics WHERE team = 'Engineering'",
  "rows_returned": 47,
  "purpose": "Weekly team review",
  "approved_by": "IT compliance system"
}
```

### **Anonymization for Different Roles**

**For CEO dashboards:**

```sql
SELECT
    'Anonymous User ' || ROW_NUMBER() OVER (ORDER BY waste_hours DESC) as user_label,
    auth_waste_hours,
    context_switch_waste_hours
FROM productivity_metrics
ORDER BY waste_hours DESC
LIMIT 100;
```

**For managers (team visible):**

```sql
SELECT
    actor.displayName,  -- Names visible for their team
    auth_waste_hours,
    context_switch_waste_hours
FROM productivity_metrics
WHERE actor.id IN (SELECT id FROM managers_team WHERE manager = CURRENT_USER())
ORDER BY waste_hours DESC;
```

### **Sensitive App Detection**

Some apps reveal sensitive information:

- Mental health apps (BetterHelp, Talkspace)
- Job search tools (LinkedIn Jobs, Indeed)
- Personal finance (Mint, Personal Capital)
- Legal services (LegalZoom, Rocket Lawyer)

**Handling:**

```sql
-- Flag sensitive apps
CREATE TABLE sensitive_apps (
    app_id STRING,
    sensitivity_level STRING,  -- 'high', 'medium', 'low'
    category STRING  -- 'health', 'legal', 'finance', 'job-search'
);

-- Exclude from manager view
SELECT ...
FROM sso_logs
WHERE target.id NOT IN (SELECT app_id FROM sensitive_apps WHERE sensitivity_level = 'high')
```

### **Production Best Practices**

1. **Encryption at Rest:** All SSO data encrypted with customer-managed keys (KMS)
2. **Encryption in Transit:** TLS 1.3 for all data transfers
3. **Data Isolation:** Each customer has own VPC, own BigQuery dataset (Parable's architecture)
4. **Access Logging:** CloudAudit logs for every data access
5. **Regular Audits:** Quarterly access reviews, annual penetration testing
6. **Minimal Data Collection:** Only collect SSO fields needed for analytics
7. **Data Minimization:** Aggregate early, don't store raw IPs/session tokens longer than needed
