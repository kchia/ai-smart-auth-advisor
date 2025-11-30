# Phase 2: Hypotheses Summary (Table Format)

**Quick Reference for Parable Interview Prep**

**Parable Mission:** Help Fortune 1000 CEOs gain organizational observability to answer "Where is the time waste?"

**The 5 CEO Questions:**

1. Where is the waste?
2. Where is the friction?
3. Where is the bureaucracy?
4. Where can we automate?
5. How can we use AI to make my team 100x more productive?

**First 3-Month Deliverable:** Work Categorizer agentic workflow (Hypothesis 2.7)

---

## Overview: All Hypotheses

| ID      | Hypothesis                 | Priority   | Time Waste (1K employees)     | CEO Question                | Testable w/ Sample? | Notes                                               |
| ------- | -------------------------- | ---------- | ----------------------------- | --------------------------- | ------------------- | --------------------------------------------------- |
| **2.1** | **Auth Friction**          | ⭐⭐⭐⭐⭐ | **$2.4M/year**                | Friction, Bureaucracy       | ✅ **YES**          | Steps 1-9, avg 5.6, step 8 most common (33%)        |
| **2.7** | **Work Categorizer**       | ⭐⭐⭐⭐⭐ | $100M/year (generic policies) | 100x productivity, Automate | ⚠️ Partial          | First 3-month deliverable                           |
| **3.1** | **User Segmentation**      | ⭐⭐⭐⭐   | License optimization          | 100x productivity           | ⚠️ Partial          | 50% power (2 apps), 10% regular (1), 40% casual (0) |
| 1.1     | High App Switching         | ⭐⭐⭐     | $12.4M/year                   | Friction, Waste             | ❌ NO               | Need full day, not 13 seconds                       |
| 1.2     | Time Gaps Reveal Switching | ⭐⭐⭐     | $9M/year                      | Waste, Friction             | ❌ NO               | Need hours/days of data                             |
| 2.2     | Low Success Rates          | ⭐⭐       | Variable                      | Friction                    | ⚠️ Partial          | Can check success rates                             |
| 3.2     | Apps Used Together         | ⭐⭐⭐     | Workflow optimization         | Automate                    | ✅ YES              | Found 5 app pairs in sample                         |
| 3.3     | Rarely Used Apps           | ⭐⭐⭐     | $200k/year (licenses)         | Waste                       | ✅ YES              | All apps ≤2 users in sample                         |
| 4.1     | App = Role Detection       | ⭐⭐⭐     | Enables 2.7                   | 100x productivity           | ⚠️ Partial          | Overlap with 2.7                                    |
| 4.2     | New Employee Patterns      | ⭐⭐       | Onboarding efficiency         | Automate                    | ❌ NO               | Can't distinguish new vs established                |
| 5.1     | Remote Worker Apps         | ⭐⭐       | Tool optimization             | Automate                    | ❌ NO               | Sample too small                                    |
| 5.2     | Device Switching           | ⭐         | Fragmentation                 | Friction                    | ❌ NO               | No device diversity in sample                       |
| 6.1     | After-Hours Usage          | ⭐⭐       | Work-life balance             | Waste                       | ❌ NO               | All events in 13-second window                      |

---

## Top 3 Priority Hypotheses (Detailed Comparison)

### Hypothesis 2.1: Authentication Friction

| Aspect                      | Details                                                                                                                                                                                                                                                                                                                                                                    |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Statement**               | Users with higher authentication steps (MFA, challenges) waste time on auth and may access apps less frequently                                                                                                                                                                                                                                                            |
| **Pattern in Sample Data**  | • Auth steps range: 1-9 (average: 5.6)<br>• Step 8 most common (33% of events)<br>• User "mco laboris nisi ut" consistently faces step 9<br>• Clear variability indicates friction opportunities                                                                                                                                                                           |
| **Time Waste Calculation**  | • Per-step overhead: 30 sec/step<br>• Step 9 user: (9-1) × 30 sec = 4 min/auth<br>• 20 accesses/day × 4 min = **80 min/day (1.3 hrs)**<br>• **Weekly:** 6.5 hrs/week<br>• **Annual/employee:** $50/hr × 6.5 hrs × 50 weeks = **$16,250/year**<br>• **Org (15% face step 8-9):** 150 × $16k = **$2.4M/year**                                                                |
| **CEO Questions Answered**  | • "Where is the bureaucracy?"<br>• "Where is the friction?"                                                                                                                                                                                                                                                                                                                |
| **Testable with Sample?**   | ✅ **YES** - Auth step distribution clearly visible                                                                                                                                                                                                                                                                                                                        |
| **Agentic Workflow**        | **Smart Authentication Advisor Agent**<br>• Tools: query_user_auth_history, get_device_trust_score, recommend_auth_level, explain_decision<br>• Output to user: "We're using simplified auth because you're on your trusted work laptop at the office. Saved ~2 min."<br>• Output to IT: "150 employees face step 8-9. Adjusting policies could save $2.4M/year."          |
| **Why Agentic > ML**        | • ML: Static prediction "User needs high/low auth" - can't explain<br>• Agentic: Dynamic risk-based auth that explains decisions to user AND IT                                                                                                                                                                                                                            |
| **Evaluation**              | • Ground truth: IT labels users "high security need" vs "reduce friction"<br>• Agreement: Agent matches IT judgment (>85%)<br>• Time savings: A/B test (40% auth time reduction)<br>• Security: Track fraud (must not increase >1%)                                                                                                                                        |
| **Production Concerns**     | • **RBAC:** Only IT security sees individual patterns<br>• **Privacy:** Auth step data not PII, but reveals security posture<br>• **Tracing:** Log every decision with trust score + reasoning<br>• **Cost:** ~$50/day for 10k employees (pre-computed trust scores)<br>• **Latency:** <200ms (use cached scores)<br>• **Scale:** Materialize in BigQuery, refresh nightly |
| **Interview Talking Point** | "Auth complexity varies from step 1 to 9 (avg 5.6). Users at step 8-9 waste **6.5 hours/week** - that's **$16,250/year** per employee. For 1,000 employees, if 15% face this friction, that's **$2.4M annually**. This directly answers 'Where is the bureaucracy?'"                                                                                                       |

---

### Hypothesis 2.7: Work Categorizer

| Aspect                      | Details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Statement**               | Users' app access patterns can automatically categorize work type (Development, Sales, Support, HR) enabling role-based insights                                                                                                                                                                                                                                                                                                                                                                                                         |
| **Pattern to Look For**     | • Distinct app co-occurrence patterns per user segment<br>• Examples: GitHub+Jira+Slack = Engineering, Salesforce+Gmail = Sales<br>• App access frequency indicates work intensity                                                                                                                                                                                                                                                                                                                                                       |
| **Time Waste Calculation**  | • **Problem:** Without work categorization, IT can't provide role-specific optimizations<br>• **Impact:** Generic tools/policies = ~10% productivity loss<br>• **Waste:** 1,000 employees × $50/hr × 40 hrs/week × 10% = **$2M/week = $100M/year**                                                                                                                                                                                                                                                                                       |
| **CEO Questions Answered**  | • "How can we use AI to make my team 100x productive?"<br>• "Where can we automate?"                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| **Testable with Sample?**   | ⚠️ **Partial** - Can see app co-occurrence (5 pairs found), but sample too small for definitive clustering                                                                                                                                                                                                                                                                                                                                                                                                                               |
| **Agentic Workflow**        | **Work Categorizer Agent**<br>• Tools: query_user_app_history, query_app_cooccurrence, get_industry_benchmarks, categorize_work_pattern, explain_categorization, suggest_optimizations<br>• Flow: Query 90-day patterns → LLM analyzes with few-shot prompting → Categorize + explain → Suggest role-based optimizations<br>• Output: "**Category:** Software Engineer (Frontend). **Reasoning:** Heavy GitHub (250), Jira (90), Figma (30) = frontend signature. **Savings:** 3-5 hrs/week"                                             |
| **Why Agentic > ML**        | • ML: K-means → "User in cluster 3" - not explainable, needs retraining for new apps<br>• Agentic: LLM analyzes patterns, explains WHY, adapts to new apps (few-shot), CEO-friendly                                                                                                                                                                                                                                                                                                                                                      |
| **Evaluation**              | • **Ground truth:** HR job titles for 500 employees<br>• **Accuracy:** >80% correct categorization<br>• **Explainability:** Show 50 managers categorizations - >85% agree, >4.0/5 confidence<br>• **Adaptability:** New app introduced - agent incorporates without retraining<br>• **ROI:** A/B test role-based optimizations (10-15% productivity increase)                                                                                                                                                                            |
| **Production Concerns**     | • **RBAC:** HR/IT see all, managers see only their team categories, employees see own<br>• **Privacy:** Categorization reveals role - don't expose individual app details to managers<br>• **Tracing:** Track EVERY LLM call with cost, latency, tokens, prompt version<br>• **Cost:** ~$0.02/categorization, refresh every 90 days = **$67/month for 10k employees**<br>• **Latency:** NOT real-time (runs nightly), users query cached results<br>• **Scale:** 500k users across clients = 5,556/day = **$111/day across ALL clients** |
| **Interview Talking Point** | "This is the first 3-month deliverable! The agentic workflow analyzes app patterns over 90 days and uses LLM few-shot learning to categorize work types with natural language explanations. Unlike ML clustering, it adapts to new apps without retraining and explains WHY each categorization, making it CEO-friendly."                                                                                                                                                                                                                |

---

### Hypothesis 3.1: User Segmentation ⭐⭐⭐⭐

| Aspect                      | Details                                                                                                                                                                                                                                                                                                       |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Statement**               | Users cluster into distinct segments - power users access many apps frequently, casual users access few apps infrequently                                                                                                                                                                                     |
| **Pattern in Sample Data**  | **ACTUAL SEGMENTATION (not 30/40/30):**<br>• **50% power users** (5/10) - accessing 2 apps (max in sample)<br>• **10% regular users** (1/10) - accessing 1 app<br>• **40% casual users** (4/10) - accessing 0 apps (auth-only events)                                                                         |
| **Time Waste Calculation**  | • License optimization opportunities<br>• Casual users (0 apps) may have unused licenses<br>• Power users may need advanced features not provided                                                                                                                                                             |
| **CEO Questions Answered**  | • "How can we use AI to make my team 100x productive?"<br>• "Where is the waste?" (license optimization)                                                                                                                                                                                                      |
| **Testable with Sample?**   | ⚠️ **Partial** - Can see segmentation exists, but 13-second sample can't distinguish true casual from "not yet accessed"                                                                                                                                                                                      |
| **Agentic Workflow**        | • **Personalized Recommendations:** Power users get advanced workflows, casual get simplified UX<br>• **License Optimization:** Identify casual users for license reallocation<br>• **Onboarding Paths:** Different flows for different segments                                                              |
| **Why Agentic > ML**        | • ML: "User in low-activity cluster" - no context<br>• Agentic: "Based on 90-day patterns, this user accessed 0 apps - recommend license review"                                                                                                                                                              |
| **Evaluation**              | • Compare with actual usage over full quarter<br>• Validate license optimization ROI<br>• User satisfaction surveys for personalization                                                                                                                                                                       |
| **Production Concerns**     | • **RBAC:** Managers see team segments, not individual names<br>• **Privacy:** Segment labels may be sensitive<br>• **Cost:** Minimal (piggybacks on Work Categorizer data)                                                                                                                                   |
| **Interview Talking Point** | "The data shows clear user clustering: **50%** are power users accessing 2 apps, **10%** access 1 app, **40%** are in auth-only events. This enables personalized productivity interventions - power users get advanced workflow automation, casual users get simplified onboarding or license optimization." |

---

## Category Summary

| Category                         | Hypotheses                  | Interview Priority | Testable with Sample Data         |
| -------------------------------- | --------------------------- | ------------------ | --------------------------------- |
| **1. Context Switching & Focus** | 1.1, 1.2                    | ⭐⭐⭐             | ❌ Need full day/week data        |
| **2. Authentication Friction**   | 2.1 ⭐⭐⭐⭐⭐, 2.2, 2.7 🎯 | **HIGHEST**        | ✅ 2.1 = YES, 2.7 = Partial       |
| **3. Application Usage**         | 3.1 ⭐⭐⭐⭐, 3.2, 3.3      | **HIGH**           | ✅ 3.1/3.2/3.3 = Yes/Partial      |
| **4. Role & Team Patterns**      | 4.1, 4.2                    | ⭐⭐⭐             | ⚠️ Overlaps with 2.7              |
| **5. Location & Device**         | 5.1, 5.2                    | ⭐                 | ❌ No diversity in sample         |
| **6. Time-Based Patterns**       | 6.1                         | ⭐⭐               | ❌ All events in 13-second window |

---

## Production Concerns Comparison

| Concern                      | Auth Friction (2.1)        | Work Categorizer (2.7)              | User Segmentation (3.1)     |
| ---------------------------- | -------------------------- | ----------------------------------- | --------------------------- |
| **RBAC**                     | IT security only           | HR/IT all, managers team only       | Managers see team segments  |
| **Privacy Risk**             | Reveals security posture   | Reveals job role                    | Reveals usage patterns      |
| **Cost/Day (10k employees)** | $50                        | $67/month (~$2.20/day)              | Minimal (uses 2.7 data)     |
| **Latency Requirement**      | <200ms (real-time)         | Not real-time (nightly)             | Not real-time (cached)      |
| **Scale Challenge**          | Billions of auth events    | 500k users across clients           | Same as 2.7                 |
| **Tracing Complexity**       | Log decision + trust score | Log EVERY LLM call + prompt version | Simple (segment assignment) |
