# Okta SSO Audit Log - Data Dictionary

**Dataset:** raw_fixture.json
**Total Records:** 18 (10 unique source_identifiers, 8 duplicates)
**Structure:** Top-level metadata + nested Okta audit log in `raw_data` field

---

## Data Schema (Quick Visual)

```
raw_fixture.json
├── source_identifier
├── file_name (lorem ipsum)
├── created_utc_tstamp
├── load_utc_tstamp
├── etl_version (lorem ipsum)
└── raw_data (JSON string) ↓

    Okta Audit Log
    ├── actor (WHO)
    │   ├── id ★★★
    │   ├── alternateId
    │   ├── displayName
    │   └── type
    │
    ├── target[] (WHAT APP) ★★★
    │   ├── id ★★★
    │   ├── displayName
    │   ├── type
    │   └── detailEntry
    │       ├── signOnModeType
    │       ├── policyType/policyName
    │       └── expires/hash/subject
    │
    ├── published (WHEN) ★★★
    ├── eventType ★★
    ├── outcome ★★
    │   ├── result
    │   └── reason
    │
    ├── authenticationContext
    │   ├── authenticationStep ★
    │   ├── externalSessionId
    │   └── rootSessionId
    │
    ├── client
    │   ├── ipAddress
    │   ├── device
    │   ├── userAgent
    │   │   ├── browser
    │   │   ├── os
    │   │   └── rawUserAgent
    │   └── geographicalContext
    │       ├── city
    │       ├── country
    │       ├── state
    │       └── geolocation (lat/lon)
    │
    ├── debugContext
    │   └── debugData
    │       ├── dtHash
    │       ├── requestId
    │       ├── threatSuspected
    │       ├── logOnlySecurityData ★
    │       │   ├── risk.level
    │       │   ├── risk.reasons
    │       │   └── behaviors
    │       │       ├── Velocity ★ (context switching!)
    │       │       ├── New Device
    │       │       ├── New IP
    │       │       └── New Geo-Location
    │       └── (OAuth fields when present)
    │
    ├── request
    │   └── ipChain[]
    │       └── geographicalContext
    │
    ├── securityContext
    │   ├── asNumber
    │   ├── asOrg
    │   ├── isProxy
    │   └── isp
    │
    └── transaction
        ├── id
        └── type

Legend: ★★★ Critical  ★★ Important  ★ Interesting
```

---

## Key Fields for Productivity Analysis

### **Primary Dimensions:**

1. **`actor.id`** - Who is the user?
2. **`target[].id`** - Which app did they access?
3. **`published`** - When did they access it?

### **Secondary Dimensions:**

4. **`eventType`** - What type of action? (login, logout, app switch)
5. **`outcome.result`** - Did it succeed or fail?
6. **`authenticationContext.authenticationStep`** - How much friction?
7. **`client.device`** / **`client.userAgent.browser`** - What device/browser?
8. **`client.geographicalContext.*`** - Where are they working from?

---

## Data Quality Notes

### **Missing/Null Values:**

- `device`: **100% null** (18/18 records) - cannot rely on this
- `client.id`: **78% null** (14/18 records) - unreliable
- `outcome.reason`: **72% null** (13/18 records) - only present
  on failures
- `target`: **39% empty** (7/18 records) - some events don't have
  apps

### **Duplicates:**

- **8 duplicate `source_identifier` values** (appears twice each)
- This suggests the dataset is intentionally duplicated for
  testing purposes

### **Anonymization:**

- All string values contain **Lorem Ipsum** fragments
- Field names and structure are real Okta
- Values are obfuscated but **cardinality is preserved** (10
  unique actors, 11 unique apps, etc.)

### **Timestamps:**

- All `created_utc_tstamp` are **identical** (2025-05-21)
- All `load_utc_tstamp` are **identical** (2025-05-22)
- Only `published` varies (2025-04-01 range)
- Use `published` for temporal analysis

---

## Top-Level Fields (ETL Metadata)

| Field                | Type        | Description                                    | Sample Value                       |
| -------------------- | ----------- | ---------------------------------------------- | ---------------------------------- |
| `source_identifier`  | string      | Unique ID for the audit log event              | "847"                              |
| `file_name`          | string      | Source file name (anonymized with Lorem Ipsum) | "amet, consectetur adipiscing..."  |
| `created_utc_tstamp` | timestamp   | When the event was created                     | "2025-05-21T01:33:38.743+00:00"    |
| `load_utc_tstamp`    | timestamp   | When the event was loaded into the system      | "2025-05-22T23:09:32.199425+00:00" |
| `etl_version`        | string      | ETL pipeline version (anonymized)              | "dolor"                            |
| `raw_data`           | JSON string | The actual Okta audit log (see below)          | {...}                              |

**Note:** All records have the same `created_utc_tstamp` and `load_utc_tstamp`, indicating this is a batch load of events from the same time window.

---

## Okta Audit Log Structure (`raw_data`)

### **1. Event Metadata**

| Field             | Type      | Null?     | Description                                                 | Productivity Relevance                     |
| ----------------- | --------- | --------- | ----------------------------------------------------------- | ------------------------------------------ |
| `uuid`            | string    | No        | Unique identifier for this event                            | Event deduplication                        |
| `published`       | timestamp | No        | When Okta published this event                              | Time-based analysis, sequences             |
| `eventType`       | string    | No        | Type of event (e.g., user.session.start, app.generic.login) | **HIGH** - Identifies what action occurred |
| `legacyEventType` | string    | Sometimes | Older event type format                                     | Backward compatibility                     |
| `version`         | string    | No        | Okta API version (v1, v3, v5, v8)                           | Schema understanding                       |
| `displayMessage`  | string    | No        | Human-readable event description                            | Understanding event intent                 |
| `severity`        | string    | No        | Event severity level                                        | Risk/anomaly detection                     |

**Productivity Insights:**

- `eventType` describes WHAT the user did (logged in, switched apps, etc.)
- `published` timestamp is key for temporal analysis (when do people work? app switching frequency?)

---

### **2. Actor (The User)**

Path: `actor.*`

| Field               | Type   | Null?        | Description                     | Productivity Relevance                   |
| ------------------- | ------ | ------------ | ------------------------------- | ---------------------------------------- |
| `actor.id`          | string | No           | Unique user identifier          | **HIGH** - Primary key for user analysis |
| `actor.alternateId` | string | No           | Alternate user ID (often email) | User lookup                              |
| `actor.displayName` | string | No           | User's display name             | Human-readable identification            |
| `actor.type`        | string | No           | Actor type (User, App, etc.)    | Distinguish human vs system events       |
| `actor.detailEntry` | object | Usually null | Additional actor details        | Extended attributes                      |

**Productivity Insights:**

- `actor.id` is the primary dimension for user-level analysis
- Aggregate by `actor.id` to find:
  - Power users vs casual users
  - App switching patterns per user
  - Individual productivity profiles

**Statistics:**

- **10 unique actors** in the dataset
- Each actor has 1-2 events

---

### **3. Target (The Application/Resource)**

Path: `target[*].*` (Array of targets)

| Field                  | Type   | Null?     | Description                              | Productivity Relevance            |
| ---------------------- | ------ | --------- | ---------------------------------------- | --------------------------------- |
| `target[].id`          | string | No        | Unique app/resource identifier           | **HIGH** - Which app was accessed |
| `target[].displayName` | string | No        | Human-readable app name                  | Understanding app usage           |
| `target[].type`        | string | No        | Target type (AppInstance, AppUser, etc.) | Categorizing resources            |
| `target[].alternateId` | string | Sometimes | Alternate identifier                     | Secondary lookup                  |
| `target[].detailEntry` | object | Sometimes | Target-specific details                  | Additional metadata               |

**Common `detailEntry` fields:**

- `signOnModeType`: How user authenticated to app
- `policyType`: Policy applied
- `policyName`: Policy name
- `expires`: Token/session expiration
- `hash`: Certificate/token hash
- `subject`: Certificate subject

**Productivity Insights:**

- `target[].id` tells you which application the user accessed
- With perfect SSO data, every app access = one SSO event
- Analyze:
  - Which apps are most used?
  - Which apps are used together (sequences)?
  - Which apps are never used (wasted licenses)?
  - Role-based app clusters (engineers use GitHub+Slack+Jira, sales use Salesforce+HubSpot)

**Statistics:**

- **20 target entries** across 18 events (some events have multiple targets)
- **11 unique target IDs**
- **7 events have no targets** (empty list) - likely authentication or policy events

---

### **4. Authentication Context**

Path: `authenticationContext.*`

| Field                                          | Type    | Null?        | Description                                       | Productivity Relevance       |
| ---------------------------------------------- | ------- | ------------ | ------------------------------------------------- | ---------------------------- |
| `authenticationContext.authenticationStep`     | integer | No           | Which step in auth flow (e.g., 1=password, 2=MFA) | Multi-step auth detection    |
| `authenticationContext.authenticationProvider` | string  | Usually null | Auth provider (OKTA, LDAP, etc.)                  | SSO vs direct auth           |
| `authenticationContext.credentialProvider`     | string  | Usually null | Credential provider                               | Auth method tracking         |
| `authenticationContext.credentialType`         | string  | Usually null | Type of credential used                           | Password vs SSO vs MFA       |
| `authenticationContext.externalSessionId`      | string  | No           | External session ID                               | Session correlation          |
| `authenticationContext.rootSessionId`          | string  | No           | Root session ID                                   | Session tracking across apps |
| `authenticationContext.interface`              | string  | Usually null | Interface used                                    | Web vs mobile                |
| `authenticationContext.issuer`                 | string  | Usually null | Token issuer                                      | Federation analysis          |

**Productivity Insights:**

- `authenticationStep`: Higher values = more friction (MFA steps)
- `rootSessionId`: Group events in the same user session
- **Hypothesis to test:** Do users with frequent MFA prompts (step > 1) have lower productivity due to interruptions?

**Statistics:**

- **Auth steps:** 1, 2, 4, 6, 8, 9 (varied, not always simple 1-2)
- Most common: Step 8 (6 events), Step 1 (4 events), Step 6 (4 events)

---

### **5. Client (Device & Browser)**

Path: `client.*`

| Field                                        | Type   | Null?      | Description            | Productivity Relevance    |
| -------------------------------------------- | ------ | ---------- | ---------------------- | ------------------------- |
| `client.id`                                  | string | Often null | Client application ID  | Device identification     |
| `client.ipAddress`                           | string | No         | IP address of request  | Location/network analysis |
| `client.device`                              | string | No         | Device type            | Mobile vs desktop         |
| `client.zone`                                | string | No         | Okta zone              | Network zone              |
| `client.userAgent.browser`                   | string | No         | Browser type           | Browser patterns          |
| `client.userAgent.os`                        | string | No         | Operating system       | OS patterns               |
| `client.userAgent.rawUserAgent`              | string | No         | Full user agent string | Detailed device info      |
| `client.geographicalContext.city`            | string | No         | City                   | Location analysis         |
| `client.geographicalContext.country`         | string | No         | Country                | Location analysis         |
| `client.geographicalContext.state`           | string | No         | State/province         | Location analysis         |
| `client.geographicalContext.postalCode`      | string | No         | Postal code            | Precise location          |
| `client.geographicalContext.geolocation.lat` | float  | No         | Latitude               | GPS coordinates           |
| `client.geographicalContext.geolocation.lon` | float  | No         | Longitude              | GPS coordinates           |

**Productivity Insights:**

- **Device switching:** Does user access apps from multiple devices? (friction)
- **Remote work patterns:** Geographic diversity, VPN usage
- **Browser/OS standardization:** Are employees using supported platforms?
- **Hypothesis to test:** Do users who switch devices frequently have fragmented workflows?

**Statistics:**

- **10 unique browsers, 10 unique operating systems**
- **10 unique cities, 10 unique countries**
- `client.id` is **null in 14/18 records** (may not be reliable)

---

### **6. Request Context**

Path: `request.*`

| Field                                     | Type   | Description                  | Productivity Relevance |
| ----------------------------------------- | ------ | ---------------------------- | ---------------------- |
| `request.ipChain[]`                       | array  | Chain of IPs (proxies, VPNs) | Network path analysis  |
| `request.ipChain[].ip`                    | string | IP address in chain          | VPN/proxy detection    |
| `request.ipChain[].geographicalContext.*` | object | Location of this IP          | Network routing        |
| `request.ipChain[].version`               | string | IP version (v4/v6)           | Network type           |
| `request.ipChain[].source`                | string | IP source                    | Origin identification  |

**Productivity Insights:**

- **VPN detection:** ipChain length > 1 may indicate VPN/proxy
- **Network reliability:** Consistent IP = stable connection, changing IP = mobile/unstable

**Statistics:**

- All records have 1 IP in chain (no multi-hop proxy detection in this sample)

---

### **7. Security Context**

Path: `securityContext.*`

| Field                      | Type    | Description                   | Productivity Relevance     |
| -------------------------- | ------- | ----------------------------- | -------------------------- |
| `securityContext.asNumber` | integer | Autonomous System Number      | ISP/network identification |
| `securityContext.asOrg`    | string  | AS organization name          | Network provider           |
| `securityContext.domain`   | string  | Domain                        | Company network            |
| `securityContext.isProxy`  | integer | Proxy indicator (boolean-ish) | Proxy detection            |
| `securityContext.isp`      | string  | Internet service provider     | ISP analysis               |

**Productivity Insights:**

- **Corporate vs personal network:** ASN can indicate if user is on corporate VPN
- **Security friction:** Proxy usage may indicate additional security layers
- **Hypothesis:** Users on corporate networks may have smoother SSO experience

**Statistics:**

- **10 unique AS Numbers**
- `isProxy` values: 1, 2, 5, 6, 7, 9 (unclear if boolean or risk score)

---

### **8. Outcome**

Path: `outcome.*`

| Field            | Type   | Null?      | Description                       | Productivity Relevance             |
| ---------------- | ------ | ---------- | --------------------------------- | ---------------------------------- |
| `outcome.result` | string | No         | SUCCESS, FAILURE, CHALLENGE, etc. | **HIGH** - Did the action succeed? |
| `outcome.reason` | string | Often null | Failure/challenge reason          | Error analysis                     |

**Productivity Insights:**

- **Friction detection:** FAILURE or CHALLENGE outcomes indicate authentication friction
- **Success rate:** Users with low success rates may need help/training
- **Hypothesis to test:** Do users with frequent failures have lower productivity?

**Statistics:**

- All unique outcome.result values in this sample (10 different values)
- `outcome.reason` is **null in 13/18 records** (only populated on failures/challenges)

---

### **9. Debug Context**

Path: `debugContext.debugData.*`

**Always Present Fields:**

- `dtHash`: Debug hash (18/18 records)
- `requestId`: Unique request ID (18/18 records)
- `requestUri`: URI requested (18/18 records)
- `threatSuspected`: Threat detection flag (18/18 records)
- `url`: Full URL (18/18 records)

**Sometimes Present Fields:**

- `logOnlySecurityData`: JSON with risk/behavior data (12/18 records)
  - Contains: `risk.level`, `risk.reasons`, `behaviors.*` (New Geo-Location, New Device, New IP, etc.)
- `targetEventHookIds`: Event hook IDs (7/18 records)
- `authnRequestId`: Auth request ID (7/18 records)
- `redirectUri`: OAuth redirect URI (4/18 records)
- `initiationType`: How auth was initiated (2/18 records)
- `signOnMode`: Sign-on mode (2/18 records)
- `authCode`, `grantType`, `grantedScopes`, `requestedScopes`: OAuth fields (2/18 records)
- `responseTime`: API response time (2/18 records)

**Productivity Insights:**

- **`logOnlySecurityData.behaviors`:** Detect anomalies (New Device, New IP, Velocity)
  - "Velocity" behavior = rapid app switching = context switching!
  - "New Device" = user got new device or sharing account?
- **`responseTime`:** API latency (when present) - slow auth = friction
- **`threatSuspected`:** Risk score - high risk = more challenges = friction

**Example `logOnlySecurityData` structure:**

```json
{
  "risk": {
    "level": "commod",
    "reasons": " incididunt ut l"
  },
  "behaviors": {
    "New Geo-Location": " amet, c",
    "New Device": "im veniam, ",
    "New IP": "ostrud e",
    "New State": " consequ",
    "New Country": "orem ips",
    "Velocity": "n ullamc",
    "New City": "or incid"
  }
}
```

---

### **10. Transaction**

Path: `transaction.*`

| Field                | Type   | Description                            |
| -------------------- | ------ | -------------------------------------- |
| `transaction.id`     | string | Transaction ID                         |
| `transaction.type`   | string | Transaction type                       |
| `transaction.detail` | object | Transaction details (usually empty {}) |

**Productivity Insights:**

- Groups related events in a single transaction
- `transaction.detail` is empty in all sample records

---

### **11. Device**

Path: `device`

**Value:** `null` in all 18 records

This field may be populated in other Okta events but is not used in these SSO audit logs.
