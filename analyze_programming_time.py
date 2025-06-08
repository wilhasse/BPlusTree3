#!/usr/bin/env python3
"""
Analyze programming time based on commit patterns.
Calculate time gaps between commits and visualize the results.
"""

import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import pandas as pd
from collections import defaultdict


def parse_git_log(log_output):
    """Parse git log output into structured data."""
    commits = []
    lines = log_output.strip().split("\n")

    for line in lines:
        if "|" in line:
            parts = line.split("|", 2)
            if len(parts) >= 3:
                commit_hash = parts[0]
                date_str = parts[1]
                message = parts[2]

                # Parse the date
                try:
                    # Format: 2025-06-08 14:56:12 -0700
                    dt = datetime.strptime(date_str.strip(), "%Y-%m-%d %H:%M:%S %z")
                    commits.append(
                        {
                            "hash": commit_hash,
                            "datetime": dt,
                            "message": message,
                            "date_str": date_str.strip(),
                        }
                    )
                except ValueError as e:
                    print(f"Error parsing date '{date_str}': {e}")

    # Sort by datetime (oldest first)
    commits.sort(key=lambda x: x["datetime"])
    return commits


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


def create_visualizations(sessions, daily_data):
    """Create visualizations of programming time."""

    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(
        "Programming Time Analysis for BPlusTree3 Repository",
        fontsize=16,
        fontweight="bold",
    )

    # 1. Daily programming time
    dates = sorted(daily_data.keys())
    daily_hours = [daily_data[date]["duration_minutes"] / 60 for date in dates]

    ax1.bar(dates, daily_hours, alpha=0.7, color="steelblue")
    ax1.set_title("Daily Programming Time (Hours)")
    ax1.set_ylabel("Hours")
    ax1.tick_params(axis="x", rotation=45)
    ax1.grid(True, alpha=0.3)

    # 2. Session timeline
    session_starts = [s["start"] for s in sessions]
    session_durations = [s["duration_minutes"] / 60 for s in sessions]

    ax2.scatter(session_starts, session_durations, alpha=0.6, color="orange", s=50)
    ax2.set_title("Programming Sessions Timeline")
    ax2.set_ylabel("Session Duration (Hours)")
    ax2.tick_params(axis="x", rotation=45)
    ax2.grid(True, alpha=0.3)

    # 3. Commits per day
    daily_commits = [daily_data[date]["commits"] for date in dates]

    ax3.bar(dates, daily_commits, alpha=0.7, color="green")
    ax3.set_title("Commits per Day")
    ax3.set_ylabel("Number of Commits")
    ax3.tick_params(axis="x", rotation=45)
    ax3.grid(True, alpha=0.3)

    # 4. Session duration distribution
    session_hours = [
        s["duration_minutes"] / 60 for s in sessions if s["duration_minutes"] > 0
    ]

    ax4.hist(session_hours, bins=20, alpha=0.7, color="purple", edgecolor="black")
    ax4.set_title("Session Duration Distribution")
    ax4.set_xlabel("Session Duration (Hours)")
    ax4.set_ylabel("Frequency")
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("programming_time_analysis.png", dpi=300, bbox_inches="tight")
    plt.show()


def print_summary(sessions, daily_data):
    """Print summary statistics."""
    total_minutes = sum(s["duration_minutes"] for s in sessions)
    total_hours = total_minutes / 60
    total_commits = sum(len(s["commits"]) for s in sessions)

    print("=" * 60)
    print("PROGRAMMING TIME ANALYSIS SUMMARY")
    print("=" * 60)
    print(
        f"Total Programming Time: {total_hours:.1f} hours ({total_minutes:.0f} minutes)"
    )
    print(f"Total Commits: {total_commits}")
    print(f"Total Sessions: {len(sessions)}")
    print(f"Average Session Length: {total_minutes/len(sessions):.1f} minutes")
    print(f"Programming Days: {len(daily_data)}")
    print(f"Average Hours per Day: {total_hours/len(daily_data):.1f} hours")
    print()

    # Top programming days
    top_days = sorted(
        daily_data.items(), key=lambda x: x[1]["duration_minutes"], reverse=True
    )[:5]
    print("TOP 5 PROGRAMMING DAYS:")
    for date, data in top_days:
        hours = data["duration_minutes"] / 60
        print(
            f"  {date}: {hours:.1f} hours ({data['commits']} commits, {data['sessions']} sessions)"
        )
    print()

    # Longest sessions
    longest_sessions = sorted(
        sessions, key=lambda x: x["duration_minutes"], reverse=True
    )[:5]
    print("LONGEST PROGRAMMING SESSIONS:")
    for i, session in enumerate(longest_sessions, 1):
        hours = session["duration_minutes"] / 60
        start_time = session["start"].strftime("%Y-%m-%d %H:%M")
        print(
            f"  {i}. {start_time}: {hours:.1f} hours ({len(session['commits'])} commits)"
        )


def main():
    # Read git log data from file or use command output
    try:
        # Try to get fresh git log data
        import subprocess

        result = subprocess.run(
            ["git", "log", "--pretty=format:%H|%ad|%s", "--date=iso", "--all"],
            capture_output=True,
            text=True,
            cwd=".",
        )
        if result.returncode == 0:
            git_log_output = result.stdout
        else:
            raise Exception("Git command failed")
    except:
        # Fallback to hardcoded data if git command fails
        git_log_output = """f94aa9479bba269ffa10dae4098b94fea8d0c86a|2025-06-08 14:56:12 -0700|feat: implement complete dictionary API for Python B+ Tree
1cde4ca8a86d3f1ddc6bba2033dde06600a65eca|2025-06-08 14:49:21 -0700|fix: resolve critical segfaults in C extension
b31b6b75955dba7608ea0faa116aba32014eb9c4|2025-06-08 13:19:24 -0700|style: apply code formatting to Rust implementation
150515273ea331ebe68c9fea15d6b6c7795d4494|2025-06-08 13:19:11 -0700|docs: add comprehensive GA readiness plan for Python implementation
e1f539e238077bfb1cdc72ee2adeeaf12febc780|2025-06-08 10:18:36 -0700|refactor: reorganize project structure for dual-language implementation
79a19eee2a4dac5c5574f79c895af8db58c92db6|2025-06-08 09:49:15 -0700|docs: add performance benchmark charts demonstrating optimization impact
054d1bd1db709e91525c2bd691c2a8cfc4bddf03|2025-06-08 09:48:06 -0700|Merge pull request #6 from KentBeck/feature/fuzz-testing-and-benchmarks"""

    # Parse commits
    commits = parse_git_log(git_log_output)

    if not commits:
        print("No commits found to analyze!")
        return

    # Calculate programming sessions (assuming gaps > 2 hours indicate breaks)
    sessions = calculate_programming_sessions(commits, max_gap_minutes=120)

    # Analyze daily data
    daily_data = analyze_daily_programming(sessions)

    # Print summary
    print_summary(sessions, daily_data)

    # Create visualizations
    create_visualizations(sessions, daily_data)


if __name__ == "__main__":
    main()
