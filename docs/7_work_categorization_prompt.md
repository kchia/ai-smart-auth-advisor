System: You are an enterprise work categorization expert specializing in analyzing employee app usage patterns to infer job roles and
responsibilities. You use quantitative pattern matching combined with domain expertise to provide accurate, explainable categorizations.

User: Analyze the following employee's app usage patterns from the last 90 days and categorize their primary work role using the industry
benchmarks provided.

App Access Data (90-day period):

- GitHub: 250 accesses (code repository, version control)
- Slack: 180 accesses (team communication)
- Jira: 90 accesses (project management, issue tracking)
- Figma: 30 accesses (design and prototyping tool)

Total accesses: 550
Observation period: 90 days
Daily average: ~6 accesses/day

---

Industry Role Benchmarks (90-day typical ranges):

Software Engineer (Frontend)

- GitHub: 200-400 (primary coding activity)
- Jira: 60-120 (sprint planning, tickets)
- Slack: 100-200 (team coordination)
- Figma: 20-60 (UI/UX collaboration)
- VS Code/IDEs: 150-300 (local development)

Software Engineer (Backend)

- GitHub: 200-400 (primary coding activity)
- Jira: 60-120 (sprint planning, tickets)
- Slack: 100-200 (team coordination)
- DataGrip/DB tools: 40-100 (database work)
- AWS Console/GCP: 30-80 (infrastructure)

Product Manager

- Jira: 150-300 (roadmap, backlog management)
- Slack: 200-400 (stakeholder communication)
- Figma: 40-100 (design reviews)
- Notion/Confluence: 80-150 (documentation)
- Google Meets/Zoom: 60-120 (meetings)

Designer (UI/UX)

- Figma: 300-500 (primary design work)
- Adobe Creative Suite: 100-200 (graphics)
- Slack: 80-150 (feedback loops)
- Jira: 20-60 (ticket tracking)
- Miro/FigJam: 40-100 (brainstorming)

Sales Representative

- Salesforce: 200-400 (CRM primary tool)
- Gmail: 400-700 (prospecting, follow-ups)
- Calendar: 200-400 (meeting scheduling)
- LinkedIn Sales Navigator: 80-150 (lead generation)
- Zoom: 60-120 (demos, calls)

Customer Support

- Zendesk/Intercom: 300-600 (ticketing primary)
- Slack: 150-300 (internal escalations)
- Gmail: 100-200 (customer emails)
- Jira: 30-80 (bug tracking)
- Knowledge base tools: 40-100

Data Scientist

- Jupyter/DataBricks: 200-400 (analysis primary)
- GitHub: 100-200 (code versioning)
- Tableau/Looker: 80-150 (visualization)
- Slack: 80-150 (stakeholder updates)
- SQL clients: 150-300 (data querying)

DevOps/SRE Engineer

- AWS/GCP/Azure Console: 200-400 (infrastructure primary)
- GitHub: 150-300 (IaC, CI/CD configs)
- PagerDuty: 40-100 (incident response)
- Datadog/Grafana: 100-200 (monitoring)
- Slack: 100-200 (incident coordination)

Marketing Manager

- HubSpot/Marketo: 150-300 (campaign management)
- Google Analytics: 100-200 (performance tracking)
- Canva/Adobe: 60-120 (creative assets)
- Gmail: 200-400 (vendor/team communication)
- Slack: 100-200 (internal coordination)

---

Task Instructions:

1. Comparative Analysis:

   - Compare the employee's pattern against ALL benchmark roles above
   - Calculate pattern similarity for top 3 matching roles
   - Identify primary role based on strongest pattern match

2. Evidence-Based Reasoning:

   - Primary indicators: Which top 3 apps account for majority of usage?
   - Supporting indicators: Which complementary tools reinforce the role?
   - Differentiators: What distinguishes this from similar roles?
   - Negative evidence: What key tools are ABSENT that would indicate other roles?

3. Confidence Scoring Rubric:

   - 0.90-1.0: Clear single-role match, primary apps align strongly with benchmark (±20%)
   - 0.70-0.89: Strong match with minor deviations or missing secondary tools
   - 0.50-0.69: Ambiguous pattern matching 2+ roles equally, likely hybrid or transitioning
   - 0.30-0.49: Weak match, unusual pattern, recommend human review
   - <0.30: No clear match, flag as uncategorizable

4. Hybrid Role Detection:

   - If pattern matches 2+ roles with similar strength (within 15% similarity), categorize as hybrid
   - Format: "Role A + Role B" (e.g., "Software Engineer + Product Manager")

5. Anomaly Detection:

   - Flag unusual patterns: very low total usage (<50 accesses/90 days)
   - Flag suspicious patterns: access to unrelated role tools (e.g., engineer accessing Salesforce heavily)
   - Flag career transitions: pattern shifting significantly over time (if detectable)

---

Required Output Format (JSON):

```json
{
"category": "Software Engineer (Frontend)",
"specialization": "Frontend-leaning full-stack with UX collaboration",
"confidence": 0.92,
"reasoning": {
"primary_indicators": "GitHub (250 accesses, 45% of total) indicates active coding as primary activity. This aligns strongly with
Software Engineer benchmark range of 200-400 accesses.",
"supporting_indicators": "Jira (90 accesses, 16%) matches sprint-based workflow typical of agile engineering teams (benchmark: 60-120).
Slack usage (180 accesses, 33%) is within normal team coordination range (benchmark: 100-200).",
"differentiators": "Figma usage (30 accesses, 5%) is the key differentiator. This is above backend engineers (who rarely use Figma) but
below dedicated designers (300-500). Suggests frontend or full-stack role with UI/UX collaboration.",
"negative_evidence": "Absence of backend-specific tools (DataGrip, AWS Console, database clients) rules out backend specialization.
Absence of IDE tracking data, but GitHub dominance confirms development role."
},
"pattern_match_scores": [
{
"role": "Software Engineer (Frontend)",
"similarity": 0.92,
"notes": "Strong match on GitHub, Jira, Slack. Figma usage confirms frontend focus."
},
{
"role": "Software Engineer (Backend)",
"similarity": 0.65,
"notes": "GitHub and Jira match, but lack of backend tools and presence of Figma reduces likelihood."
},
{
"role": "Product Manager",
"similarity": 0.35,
"notes": "Jira and Slack usage overlaps, but GitHub dominance (45%) indicates IC engineer, not PM."
}
],
"evidence": [
"GitHub accounts for 45% of total app usage (250/550 accesses) - primary activity",
"Engineering triad (GitHub + Jira + Slack) = 94% of activity, matching core engineering workflow",
"Figma at 5% of usage differentiates from pure backend (0-2%) and pure frontend/designer (>15%)",
"No backend-specific tools detected (DataGrip, AWS Console, Postgres clients)",
"Access frequency (6/day average) consistent with active development work"
],
"alternative_roles": [
"Full-stack Engineer (if backend work done via GitHub-tracked services)",
"Engineering Lead (if Jira usage increases to 150+ for roadmap planning)"
],
"anomalies": [],
"review_required": false,
"metadata": {
"total_accesses": 550,
"unique_apps": 4,
"days_analyzed": 90,
"primary_app_concentration": "45% (GitHub)",
"role_diversity_score": "Low (single clear role)"
}
}
```
