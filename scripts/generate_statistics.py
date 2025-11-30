"""
Data Statistics & Data Dictionary
===========================================

Tasks: Create data dictionary and generate statistics
"""

import json
from collections import Counter, defaultdict

# Load parsed data
with open('data/parsed_data.json', 'r') as f:
    data = json.load(f)

print("=" * 80)
print("BASIC STATISTICS")
print("=" * 80)

print(f"\nTotal records: {len(data)}")

# Unique identifiers
source_ids = [r['source_identifier'] for r in data]
print(f"Unique source_identifiers: {len(set(source_ids))}")
print(f"Source IDs: {sorted(set(source_ids))}")

# Check for duplicates
duplicate_ids = [sid for sid, count in Counter(source_ids).items() if count > 1]
if duplicate_ids:
    print(f"\n⚠️  Duplicate source_identifiers found: {duplicate_ids}")
    for dup_id in duplicate_ids:
        indices = [i for i, sid in enumerate(source_ids) if sid == dup_id]
        print(f"   ID '{dup_id}' appears at indices: {indices}")

# Timestamps
print(f"\nTimestamp range:")
created_times = [r['created_utc_tstamp'] for r in data]
print(f"  created_utc_tstamp: {min(created_times)} to {max(created_times)}")
load_times = [r['load_utc_tstamp'] for r in data]
print(f"  load_utc_tstamp: {min(load_times)} to {max(load_times)}")

# ETL versions
etl_versions = [r['etl_version'] for r in data]
print(f"\nETL versions: {set(etl_versions)}")

print("\n" + "=" * 80)
print("OKTA AUDIT LOG STATISTICS")
print("=" * 80)

# Extract raw_data for analysis
raw_data_records = [r['raw_data'] for r in data]

# Event Types
event_types = [r['eventType'] for r in raw_data_records]
print(f"\nEvent Types (unique: {len(set(event_types))}):")
for event_type, count in Counter(event_types).most_common():
    print(f"  {event_type}: {count}")

# Legacy Event Types
legacy_event_types = [r.get('legacyEventType') for r in raw_data_records if r.get('legacyEventType')]
print(f"\nLegacy Event Types (unique: {len(set(legacy_event_types))}):")
for event_type, count in Counter(legacy_event_types).most_common():
    print(f"  {event_type}: {count}")

# Outcomes
outcomes = [r['outcome']['result'] for r in raw_data_records]
print(f"\nOutcome Results:")
for outcome, count in Counter(outcomes).most_common():
    print(f"  {outcome}: {count}")

# Actors (Users)
actors = [r['actor']['id'] for r in raw_data_records]
print(f"\nUnique Actors (users): {len(set(actors))}")
print(f"Actor frequency:")
for actor, count in Counter(actors).most_common(10):
    print(f"  {actor}: {count} events")

# Targets (Applications)
print(f"\nTarget Analysis:")
targets_list = []
for r in raw_data_records:
    if r['target']:
        for target in r['target']:
            targets_list.append({
                'id': target.get('id'),
                'displayName': target.get('displayName'),
                'type': target.get('type')
            })

print(f"  Total target entries: {len(targets_list)}")
print(f"  Unique target IDs: {len(set([t['id'] for t in targets_list]))}")

target_types = [t['type'] for t in targets_list]
print(f"\n  Target Types:")
for ttype, count in Counter(target_types).most_common():
    print(f"    {ttype}: {count}")

# Authentication Steps
auth_steps = [r['authenticationContext']['authenticationStep'] for r in raw_data_records]
print(f"\nAuthentication Steps:")
for step, count in Counter(auth_steps).most_common():
    print(f"  Step {step}: {count}")

# Geographical patterns
print(f"\nGeographical Context:")
cities = [r['client']['geographicalContext']['city'] for r in raw_data_records]
print(f"  Unique cities: {len(set(cities))}")
countries = [r['client']['geographicalContext']['country'] for r in raw_data_records]
print(f"  Unique countries: {len(set(countries))}")

# Device/Browser patterns
browsers = [r['client']['userAgent']['browser'] for r in raw_data_records]
print(f"\nBrowsers:")
for browser, count in Counter(browsers).most_common():
    print(f"  {browser}: {count}")

operating_systems = [r['client']['userAgent']['os'] for r in raw_data_records]
print(f"\nOperating Systems:")
for os, count in Counter(operating_systems).most_common():
    print(f"  {os}: {count}")

# Security Context
print(f"\nSecurity Context:")
as_numbers = [r['securityContext']['asNumber'] for r in raw_data_records]
print(f"  Unique AS Numbers: {len(set(as_numbers))}")
is_proxy_values = [r['securityContext']['isProxy'] for r in raw_data_records]
print(f"  isProxy values: {set(is_proxy_values)}")

# Severity
severities = [r['severity'] for r in raw_data_records]
print(f"\nSeverity levels:")
for severity, count in Counter(severities).most_common():
    print(f"  {severity}: {count}")

# Version
versions = [r['version'] for r in raw_data_records]
print(f"\nOkta API Versions:")
for version, count in Counter(versions).most_common():
    print(f"  v{version}: {count}")

# Debug context fields
print(f"\nDebug Context Fields Present:")
debug_fields = defaultdict(int)
for r in raw_data_records:
    if 'debugData' in r['debugContext']:
        for field in r['debugContext']['debugData'].keys():
            debug_fields[field] += 1

for field, count in sorted(debug_fields.items(), key=lambda x: -x[1]):
    print(f"  {field}: {count}/{len(raw_data_records)} records")

# Target detail entry types
print(f"\nTarget Detail Entry Types:")
detail_entry_fields = defaultdict(int)
for r in raw_data_records:
    if r['target']:
        for target in r['target']:
            if target.get('detailEntry'):
                for field in target['detailEntry'].keys():
                    detail_entry_fields[field] += 1

for field, count in sorted(detail_entry_fields.items(), key=lambda x: -x[1]):
    print(f"  {field}: {count}")

print("\n" + "=" * 80)
print("DATA QUALITY ASSESSMENT")
print("=" * 80)

# Check for null values in key fields
print("\nNull/Missing values in key fields:")
null_counts = defaultdict(int)

for r in raw_data_records:
    # Actor
    if not r['actor'].get('id'):
        null_counts['actor.id'] += 1
    if not r['actor'].get('displayName'):
        null_counts['actor.displayName'] += 1

    # Client
    if not r['client'].get('id'):
        null_counts['client.id'] += 1
    if not r['client'].get('ipAddress'):
        null_counts['client.ipAddress'] += 1

    # Device (expected to be null often)
    if r['device'] is None:
        null_counts['device'] += 1

    # Outcome reason
    if r['outcome'].get('reason') is None:
        null_counts['outcome.reason'] += 1

    # Target
    if not r['target']:
        null_counts['target (empty list)'] += 1

for field, count in sorted(null_counts.items(), key=lambda x: -x[1]):
    print(f"  {field}: {count}/{len(raw_data_records)} records")

print("\n" + "=" * 80)
print("ANONYMIZATION NOTES")
print("=" * 80)

print("""
⚠️  This is ANONYMIZED sample data:
  - file_name contains Lorem Ipsum text (not real filenames)
  - Many string fields contain Lorem Ipsum fragments
  - Values are truncated/obfuscated
  - Cannot draw real business conclusions from content
  - CAN analyze structure, patterns, and cardinality

✓  Still useful for understanding:
  - Data schema and relationships
  - Field presence/absence patterns
  - Cardinality (how many unique values)
  - Data types
  - Event type distributions
""")

print("\n" + "=" * 80)
print("Tasks Complete!")
print("=" * 80)
