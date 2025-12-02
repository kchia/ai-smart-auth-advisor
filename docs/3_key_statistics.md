## Key Statistics

### **Dataset Basics**

- **18 records** total (10 unique, 8 duplicates)
- **10 unique users** (actors)
- **11 unique applications** (targets)
- **10 unique event types**
- **Perfect SSO assumption:** Every app access = 1 SSO event
  per day

### **User Behavior**

- **10 unique users** across 18 events
- Each user has **1-2 events** in this sample
- Users have **varied auth steps** (1, 2, 4, 6, 8, 9)

### **Application Usage**

- **11 unique applications** accessed
- **20 target entries** total (some events have 2 targets)
- **7 events (39%)** have no targets (auth/policy events)

### **Authentication Patterns**

- **Most common auth step:** 8 (6 events)
- **Auth step distribution:** 1 (4), 6 (4), 8 (6), others (4)
- Higher auth steps = more friction (MFA, challenges)

### **Geographic & Device**

- 10 unique browsers, 10 unique operating systems
- 10 unique cities, 10 unique countries
- High diversity due to anonymization pattern

### **Outcomes**

- **10 different outcome.result values** (all unique - likely anonymized)
- In real data, expect: SUCCESS, FAILURE, CHALLENGE

### **Debug Context**

- **100% of events** have: dtHash, requestId, requestUri, threatSuspected, url
- **67% of events** have: logOnlySecurityData (risk/behavior data)
- **39% of events** have: targetEventHookIds, authnRequestId
