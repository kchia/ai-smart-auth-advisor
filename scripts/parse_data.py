"""
Phase 1: Data Understanding - Okta SSO Audit Logs
==================================================

Goal: Understand the structure, fields, and quality of the SSO data
"""

import json
from collections import Counter, defaultdict

# Load the raw fixture data
print("=" * 80)
print("LOADING DATA")
print("=" * 80)

with open('data/raw_fixture.json', 'r') as f:
    data = json.load(f)

print(f"Total records: {len(data)}")
print(f"\nTop-level fields in each record:")
print(list(data[0].keys()))

# Parse the raw_data field (it's JSON stored as a string)
print("\n" + "=" * 80)
print("PARSING NESTED raw_data FIELD")
print("=" * 80)

parsed_records = []
for record in data:
    parsed = {
        'source_identifier': record['source_identifier'],
        'file_name': record['file_name'],
        'created_utc_tstamp': record['created_utc_tstamp'],
        'load_utc_tstamp': record['load_utc_tstamp'],
        'etl_version': record['etl_version'],
        'raw_data': json.loads(record['raw_data'])  # Parse the JSON string
    }
    parsed_records.append(parsed)

print(f"Successfully parsed {len(parsed_records)} records")

# Explore the structure of raw_data (the Okta audit log)
print("\n" + "=" * 80)
print("OKTA AUDIT LOG STRUCTURE (raw_data)")
print("=" * 80)

sample_raw = parsed_records[0]['raw_data']
print("\nTop-level fields in Okta audit log:")
for key in sorted(sample_raw.keys()):
    print(f"  - {key}: {type(sample_raw[key]).__name__}")

# Deep dive into each major section
print("\n" + "=" * 80)
print("DETAILED FIELD BREAKDOWN")
print("=" * 80)

def explore_nested_structure(obj, prefix="", max_depth=3, current_depth=0):
    """Recursively explore nested structure"""
    if current_depth >= max_depth:
        return

    if isinstance(obj, dict):
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key
            value_type = type(value).__name__

            if isinstance(value, (dict, list)):
                print(f"{'  ' * current_depth}{full_key}: {value_type}")
                explore_nested_structure(value, full_key, max_depth, current_depth + 1)
            else:
                # Show sample value (truncated if too long)
                sample = str(value)[:50] if value is not None else "null"
                print(f"{'  ' * current_depth}{full_key}: {value_type} = {sample}")

    elif isinstance(obj, list) and len(obj) > 0:
        print(f"{'  ' * current_depth}{prefix}[0]: {type(obj[0]).__name__}")
        explore_nested_structure(obj[0], f"{prefix}[0]", max_depth, current_depth + 1)

print("\nFull schema of first record:")
explore_nested_structure(sample_raw)

# Collect all unique fields across all records
print("\n" + "=" * 80)
print("COLLECTING ALL FIELDS ACROSS ALL RECORDS")
print("=" * 80)

def get_all_paths(obj, prefix=""):
    """Get all field paths in a nested structure"""
    paths = set()

    if isinstance(obj, dict):
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key
            paths.add(full_key)
            if isinstance(value, (dict, list)):
                paths.update(get_all_paths(value, full_key))

    elif isinstance(obj, list) and len(obj) > 0:
        # Check all items in list as they might have different fields
        for i, item in enumerate(obj):
            if isinstance(item, (dict, list)):
                paths.update(get_all_paths(item, f"{prefix}[{i}]"))

    return paths

all_fields = set()
for record in parsed_records:
    all_fields.update(get_all_paths(record['raw_data']))

print(f"\nTotal unique field paths: {len(all_fields)}")
print("\nAll field paths (sorted):")
for field in sorted(all_fields):
    print(f"  {field}")

# Save parsed data for further analysis
print("\n" + "=" * 80)
print("SAVING PARSED DATA")
print("=" * 80)

with open('data/parsed_data.json', 'w') as f:
    json.dump(parsed_records, f, indent=2)

print("✓ Saved to data/parsed_data.json")
print("\Complete: Raw data structure parsed!")
