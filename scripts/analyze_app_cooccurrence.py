"""
Phase 3: App Co-Occurrence Analysis

Analyzes which apps are used together by the same users and segments users
by their app usage patterns.

Findings:
- App pairs discovered (co-occurrence)
- User segmentation (power/regular/casual users)
"""

import json
from collections import Counter
from itertools import combinations

def load_data(file_path='data/parsed_data.json'):
    """Load parsed Okta audit log data"""
    with open(file_path, 'r') as f:
        return json.load(f)

def extract_user_apps(data):
    """
    Extract mapping of users to the apps they accessed.

    Returns:
        dict: {user_id: [app_names]}
    """
    user_apps = {}

    for record in data:
        raw_data = record['raw_data']
        user_id = raw_data['actor']['id']

        # Initialize user if not seen
        if user_id not in user_apps:
            user_apps[user_id] = []

        # Extract app names from targets
        targets = raw_data.get('target')
        if targets:
            for target in targets:
                if isinstance(target, dict) and target.get('displayName'):
                    app_name = target['displayName']
                    user_apps[user_id].append(app_name)

    # Remove duplicates per user
    for user_id in user_apps:
        user_apps[user_id] = list(set(user_apps[user_id]))

    return user_apps

def analyze_app_pairs(user_apps):
    """
    Find which apps are accessed together by the same users.

    Returns:
        Counter: {(app1, app2): count}
    """
    app_pairs = []

    for user_id, apps in user_apps.items():
        if len(apps) >= 2:
            # Generate all pairs for this user
            pairs = list(combinations(sorted(apps), 2))
            app_pairs.extend(pairs)

    return Counter(app_pairs)

def segment_users(user_apps):
    """
    Segment users by their app usage patterns.

    Returns:
        dict: {segment: [user_ids]}
    """
    segments = {
        'power_users': [],      # 2+ apps
        'regular_users': [],    # 1 app
        'casual_users': []      # 0 apps (auth-only)
    }

    for user_id, apps in user_apps.items():
        app_count = len(apps)

        if app_count >= 2:
            segments['power_users'].append(user_id)
        elif app_count == 1:
            segments['regular_users'].append(user_id)
        else:  # app_count == 0
            segments['casual_users'].append(user_id)

    return segments

def print_analysis(user_apps, app_pairs, segments):
    """Print the analysis results"""

    total_users = len(user_apps)

    print("=" * 70)
    print("APP CO-OCCURRENCE ANALYSIS")
    print("=" * 70)

    # Summary statistics
    print("\n📊 SUMMARY STATISTICS")
    print(f"  Total unique users: {total_users}")
    print(f"  Users accessing 2+ apps: {len(segments['power_users'])} ({len(segments['power_users'])/total_users*100:.0f}%)")
    print(f"  Distinct app pairs found: {len(app_pairs)}")

    # App pairs discovered
    print("\n🎯 APP PAIRS DISCOVERED (Co-occurrence)")
    print("  " + "-" * 60)
    if app_pairs:
        for (app1, app2), count in app_pairs.most_common():
            print(f"  {app1} + {app2}: {count} user(s)")
    else:
        print("  No app pairs found (no users accessed 2+ apps)")

    # User segmentation
    print("\n👥 USER SEGMENTATION BY APP USAGE")
    print("  " + "-" * 60)

    power_count = len(segments['power_users'])
    regular_count = len(segments['regular_users'])
    casual_count = len(segments['casual_users'])

    print(f"  Power users (2+ apps):   {power_count:2d} users ({power_count/total_users*100:5.0f}%)")
    print(f"  Regular users (1 app):   {regular_count:2d} users ({regular_count/total_users*100:5.0f}%)")
    print(f"  Casual users (0 apps):   {casual_count:2d} users ({casual_count/total_users*100:5.0f}%)")

    # Detailed breakdown
    print("\n📋 DETAILED USER BREAKDOWN")
    print("  " + "-" * 60)

    # Sort users by app count (descending)
    sorted_users = sorted(user_apps.items(), key=lambda x: len(x[1]), reverse=True)

    for user_id, apps in sorted_users:
        app_count = len(apps)
        if app_count > 0:
            apps_str = ", ".join(apps)
            print(f"  {user_id}: {app_count} apps - [{apps_str}]")
        else:
            print(f"  {user_id}: 0 apps (auth-only events)")

    # Key insights
    print("\n💡 KEY INSIGHTS")
    print("  " + "-" * 60)
    print(f"  • {power_count} users ({power_count/total_users*100:.0f}%) access multiple apps - co-occurrence patterns visible")
    print(f"  • {len(app_pairs)} distinct app pairs suggest workflow patterns")
    print(f"  • {casual_count} users ({casual_count/total_users*100:.0f}%) in auth-only events - potential license waste")
    print("  • Even in 13-second snapshot, role signatures are detectable")
    print("\n" + "=" * 70)

def main():
    # Load data
    print("Loading parsed data...")
    data = load_data()

    # Extract user-to-app mappings
    user_apps = extract_user_apps(data)

    # Analyze app pairs
    app_pairs = analyze_app_pairs(user_apps)

    # Segment users
    segments = segment_users(user_apps)

    # Print analysis
    print_analysis(user_apps, app_pairs, segments)

if __name__ == '__main__':
    main()
