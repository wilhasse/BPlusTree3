#!/usr/bin/env python3
"""
Analyze programming time based on commit patterns.
Simple version without matplotlib dependencies.
"""

import subprocess
from datetime import datetime, timedelta
from collections import defaultdict


def parse_git_log():
    """Get git log data and parse into structured format."""
    try:
        result = subprocess.run(
            ["git", "log", "--pretty=format:%H|%ad|%s", "--date=iso", "--all"],
            capture_output=True,
            text=True,
            cwd=".",
        )

        if result.returncode != 0:
            print("Error running git log command")
            return []

        commits = []
        lines = result.stdout.strip().split("\n")

        for line in lines:
            if "|" in line:
                parts = line.split("|", 2)
                if len(parts) >= 3:
                    commit_hash = parts[0]
                    date_str = parts[1].strip()
                    message = parts[2]

                    try:
                        # Parse date: 2025-06-08 14:56:12 -0700
                        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S %z")
                        commits.append(
                            {
                                "hash": commit_hash,
                                "datetime": dt,
                                "message": message,
                                "date_str": date_str,
                            }
                        )
                    except ValueError as e:
                        print(f"Error parsing date '{date_str}': {e}")

        # Sort by datetime (oldest first)
        commits.sort(key=lambda x: x["datetime"])
        return commits

    except Exception as e:
        print(f"Error getting git log: {e}")
        return []


def calculate_programming_sessions(commits, max_gap_minutes=120):
    """
    Calculate programming sessions based on commit gaps.
    If gap between commits is <= max_gap_minutes, assume continuous work.
    """
    if not commits:
        return []

    sessions = []
    current_session = {
        "start": commits[0]["datetime"],
        "end": commits[0]["datetime"],
        "commits": [commits[0]],
        "duration_minutes": 0,
    }

    for i in range(1, len(commits)):
        prev_commit = commits[i - 1]
        curr_commit = commits[i]

        gap_minutes = (
            curr_commit["datetime"] - prev_commit["datetime"]
        ).total_seconds() / 60

        if gap_minutes <= max_gap_minutes:
            # Continue current session
            current_session["end"] = curr_commit["datetime"]
            current_session["commits"].append(curr_commit)
            current_session["duration_minutes"] = (
                current_session["end"] - current_session["start"]
            ).total_seconds() / 60
        else:
            # Start new session
            sessions.append(current_session)
            current_session = {
                "start": curr_commit["datetime"],
                "end": curr_commit["datetime"],
                "commits": [curr_commit],
                "duration_minutes": 0,
            }

    # Add the last session
    sessions.append(current_session)

    return sessions


def analyze_daily_programming(sessions):
    """Group sessions by day and calculate daily totals."""
    daily_data = defaultdict(
        lambda: {"duration_minutes": 0, "sessions": 0, "commits": 0}
    )

    for session in sessions:
        date_key = session["start"].date()
        daily_data[date_key]["duration_minutes"] += session["duration_minutes"]
        daily_data[date_key]["sessions"] += 1
        daily_data[date_key]["commits"] += len(session["commits"])

    return dict(daily_data)


def create_ascii_chart(daily_data):
    """Create a simple ASCII chart of daily programming time."""
    if not daily_data:
        return

    dates = sorted(daily_data.keys())
    max_hours = max(daily_data[date]["duration_minutes"] / 60 for date in dates)

    print("\nDAILY PROGRAMMING TIME CHART")
    print("=" * 60)

    for date in dates:
        hours = daily_data[date]["duration_minutes"] / 60
        commits = daily_data[date]["commits"]

        # Create bar chart with asterisks
        bar_length = int((hours / max_hours) * 40) if max_hours > 0 else 0
        bar = "*" * bar_length

        print(f"{date} |{bar:<40}| {hours:5.1f}h ({commits:2d} commits)")


def print_summary(sessions, daily_data):
    """Print comprehensive summary statistics."""
    total_minutes = sum(s["duration_minutes"] for s in sessions)
    total_hours = total_minutes / 60
    total_commits = sum(len(s["commits"]) for s in sessions)

    print("=" * 70)
    print("PROGRAMMING TIME ANALYSIS SUMMARY")
    print("=" * 70)
    print(
        f"Total Programming Time: {total_hours:.1f} hours ({total_minutes:.0f} minutes)"
    )
    print(f"Total Commits: {total_commits}")
    print(f"Total Sessions: {len(sessions)}")
    print(f"Programming Days: {len(daily_data)}")

    if len(sessions) > 0:
        print(f"Average Session Length: {total_minutes/len(sessions):.1f} minutes")
    if len(daily_data) > 0:
        print(f"Average Hours per Day: {total_hours/len(daily_data):.1f} hours")

    print()

    # Date range
    if daily_data:
        dates = sorted(daily_data.keys())
        print(f"Project Duration: {dates[0]} to {dates[-1]}")
        total_days = (dates[-1] - dates[0]).days + 1
        print(f"Total Calendar Days: {total_days}")
        print(
            f"Programming Days: {len(daily_data)} ({len(daily_data)/total_days*100:.1f}% of days)"
        )
        print()

    # Top programming days
    if daily_data:
        top_days = sorted(
            daily_data.items(), key=lambda x: x[1]["duration_minutes"], reverse=True
        )[:10]
        print("TOP 10 PROGRAMMING DAYS:")
        for i, (date, data) in enumerate(top_days, 1):
            hours = data["duration_minutes"] / 60
            print(
                f"  {i:2d}. {date}: {hours:5.1f} hours ({data['commits']:2d} commits, {data['sessions']} sessions)"
            )
        print()

    # Longest sessions
    if sessions:
        longest_sessions = sorted(
            sessions, key=lambda x: x["duration_minutes"], reverse=True
        )[:10]
        print("LONGEST PROGRAMMING SESSIONS:")
        for i, session in enumerate(longest_sessions, 1):
            hours = session["duration_minutes"] / 60
            start_time = session["start"].strftime("%Y-%m-%d %H:%M")
            end_time = session["end"].strftime("%H:%M")
            print(
                f"  {i:2d}. {start_time}-{end_time}: {hours:5.1f} hours ({len(session['commits']):2d} commits)"
            )
        print()


def analyze_patterns(sessions, daily_data):
    """Analyze programming patterns."""
    print("PROGRAMMING PATTERNS ANALYSIS")
    print("=" * 40)

    # Hour of day analysis
    hour_counts = defaultdict(int)
    hour_duration = defaultdict(float)

    for session in sessions:
        for commit in session["commits"]:
            hour = commit["datetime"].hour
            hour_counts[hour] += 1
            # Distribute session time across commits
            hour_duration[hour] += session["duration_minutes"] / len(session["commits"])

    print("MOST ACTIVE HOURS (by commits):")
    top_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    for hour, count in top_hours:
        avg_duration = hour_duration[hour] / count if count > 0 else 0
        print(f"  {hour:2d}:00 - {count:3d} commits ({avg_duration:.1f} min avg)")
    print()

    # Day of week analysis
    weekday_data = defaultdict(lambda: {"duration": 0, "commits": 0, "days": 0})
    weekday_names = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    for date, data in daily_data.items():
        weekday = date.weekday()
        weekday_data[weekday]["duration"] += data["duration_minutes"]
        weekday_data[weekday]["commits"] += data["commits"]
        weekday_data[weekday]["days"] += 1

    print("PROGRAMMING BY DAY OF WEEK:")
    for i in range(7):
        data = weekday_data[i]
        if data["days"] > 0:
            avg_hours = data["duration"] / 60 / data["days"]
            avg_commits = data["commits"] / data["days"]
            print(
                f"  {weekday_names[i]:<9}: {avg_hours:5.1f}h avg ({avg_commits:4.1f} commits avg, {data['days']} days)"
            )


def main():
    print("Analyzing programming time for BPlusTree repository...")
    print("Fetching commit data...")

    # Parse commits
    commits = parse_git_log()

    if not commits:
        print("No commits found to analyze!")
        return

    print(f"Found {len(commits)} commits")

    # Calculate programming sessions (assuming gaps > 2 hours indicate breaks)
    sessions = calculate_programming_sessions(commits, max_gap_minutes=120)

    # Analyze daily data
    daily_data = analyze_daily_programming(sessions)

    # Print comprehensive analysis
    print_summary(sessions, daily_data)
    create_ascii_chart(daily_data)
    print()
    analyze_patterns(sessions, daily_data)


if __name__ == "__main__":
    main()
