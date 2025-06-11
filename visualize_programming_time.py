#!/usr/bin/env python3
"""
Create comprehensive visualizations of programming time analysis.
"""

import subprocess
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import pandas as pd
from collections import defaultdict
import numpy as np


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

        commits.sort(key=lambda x: x["datetime"])
        return commits

    except Exception as e:
        print(f"Error getting git log: {e}")
        return []


def calculate_programming_sessions(commits, max_gap_minutes=120):
    """Calculate programming sessions based on commit gaps."""
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
            current_session["end"] = curr_commit["datetime"]
            current_session["commits"].append(curr_commit)
            current_session["duration_minutes"] = (
                current_session["end"] - current_session["start"]
            ).total_seconds() / 60
        else:
            sessions.append(current_session)
            current_session = {
                "start": curr_commit["datetime"],
                "end": curr_commit["datetime"],
                "commits": [curr_commit],
                "duration_minutes": 0,
            }

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


def create_comprehensive_visualization(sessions, daily_data):
    """Create comprehensive visualizations."""

    # Set up the figure with subplots
    fig = plt.figure(figsize=(20, 16))
    fig.suptitle(
        "Programming Time Analysis for BPlusTree Repository",
        fontsize=20,
        fontweight="bold",
    )

    # Calculate total stats for title
    total_hours = sum(s["duration_minutes"] for s in sessions) / 60
    total_commits = sum(len(s["commits"]) for s in sessions)

    fig.text(
        0.5,
        0.95,
        f"Total: {total_hours:.1f} hours • {total_commits} commits • {len(daily_data)} days",
        ha="center",
        fontsize=14,
        style="italic",
    )

    # 1. Daily programming time (top left)
    ax1 = plt.subplot(3, 3, (1, 2))
    dates = sorted(daily_data.keys())
    daily_hours = [daily_data[date]["duration_minutes"] / 60 for date in dates]

    bars = ax1.bar(
        dates,
        daily_hours,
        alpha=0.8,
        color="steelblue",
        edgecolor="navy",
        linewidth=0.5,
    )
    ax1.set_title("Daily Programming Time", fontsize=14, fontweight="bold")
    ax1.set_ylabel("Hours", fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis="x", rotation=45)

    # Add value labels on bars
    for bar, hours in zip(bars, daily_hours):
        if hours > 0.5:  # Only label significant bars
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                f"{hours:.1f}h",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    # 2. Session timeline (top right)
    ax2 = plt.subplot(3, 3, 3)
    session_starts = [s["start"] for s in sessions]
    session_durations = [s["duration_minutes"] / 60 for s in sessions]
    session_commits = [len(s["commits"]) for s in sessions]

    scatter = ax2.scatter(
        session_starts,
        session_durations,
        c=session_commits,
        s=60,
        alpha=0.7,
        cmap="viridis",
    )
    ax2.set_title("Programming Sessions", fontsize=14, fontweight="bold")
    ax2.set_ylabel("Duration (Hours)", fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis="x", rotation=45)

    # Add colorbar for commits
    cbar = plt.colorbar(scatter, ax=ax2)
    cbar.set_label("Commits per Session", fontsize=10)

    # 3. Commits per day (middle left)
    ax3 = plt.subplot(3, 3, 4)
    daily_commits = [daily_data[date]["commits"] for date in dates]

    ax3.bar(
        dates,
        daily_commits,
        alpha=0.8,
        color="green",
        edgecolor="darkgreen",
        linewidth=0.5,
    )
    ax3.set_title("Commits per Day", fontsize=14, fontweight="bold")
    ax3.set_ylabel("Number of Commits", fontsize=12)
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis="x", rotation=45)

    # 4. Hour of day heatmap (middle center)
    ax4 = plt.subplot(3, 3, 5)

    # Create hour/day matrix
    hour_day_matrix = np.zeros((24, 7))  # 24 hours x 7 days

    for session in sessions:
        for commit in session["commits"]:
            hour = commit["datetime"].hour
            day = commit["datetime"].weekday()
            hour_day_matrix[hour, day] += 1

    im = ax4.imshow(hour_day_matrix, cmap="YlOrRd", aspect="auto")
    ax4.set_title("Activity Heatmap", fontsize=14, fontweight="bold")
    ax4.set_xlabel("Day of Week", fontsize=12)
    ax4.set_ylabel("Hour of Day", fontsize=12)

    # Set ticks
    ax4.set_xticks(range(7))
    ax4.set_xticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    ax4.set_yticks(range(0, 24, 4))
    ax4.set_yticklabels([f"{h:02d}:00" for h in range(0, 24, 4)])

    plt.colorbar(im, ax=ax4, label="Commits")

    # 5. Session duration distribution (middle right)
    ax5 = plt.subplot(3, 3, 6)
    session_hours = [
        s["duration_minutes"] / 60 for s in sessions if s["duration_minutes"] > 0
    ]

    ax5.hist(
        session_hours,
        bins=15,
        alpha=0.8,
        color="purple",
        edgecolor="black",
        linewidth=0.5,
    )
    ax5.set_title("Session Duration Distribution", fontsize=14, fontweight="bold")
    ax5.set_xlabel("Session Duration (Hours)", fontsize=12)
    ax5.set_ylabel("Frequency", fontsize=12)
    ax5.grid(True, alpha=0.3)

    # 6. Cumulative programming time (bottom left)
    ax6 = plt.subplot(3, 3, 7)

    cumulative_hours = []
    cumulative_total = 0

    for date in dates:
        cumulative_total += daily_data[date]["duration_minutes"] / 60
        cumulative_hours.append(cumulative_total)

    ax6.plot(
        dates, cumulative_hours, marker="o", linewidth=2, markersize=4, color="red"
    )
    ax6.fill_between(dates, cumulative_hours, alpha=0.3, color="red")
    ax6.set_title("Cumulative Programming Time", fontsize=14, fontweight="bold")
    ax6.set_ylabel("Total Hours", fontsize=12)
    ax6.grid(True, alpha=0.3)
    ax6.tick_params(axis="x", rotation=45)

    # 7. Weekly pattern (bottom center)
    ax7 = plt.subplot(3, 3, 8)

    weekday_data = defaultdict(lambda: {"duration": 0, "commits": 0, "days": 0})
    weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    for date, data in daily_data.items():
        weekday = date.weekday()
        weekday_data[weekday]["duration"] += data["duration_minutes"]
        weekday_data[weekday]["commits"] += data["commits"]
        weekday_data[weekday]["days"] += 1

    avg_hours_by_day = []
    for i in range(7):
        if weekday_data[i]["days"] > 0:
            avg_hours_by_day.append(
                weekday_data[i]["duration"] / 60 / weekday_data[i]["days"]
            )
        else:
            avg_hours_by_day.append(0)

    bars = ax7.bar(
        weekday_names,
        avg_hours_by_day,
        alpha=0.8,
        color="orange",
        edgecolor="darkorange",
    )
    ax7.set_title("Average Hours by Day of Week", fontsize=14, fontweight="bold")
    ax7.set_ylabel("Average Hours", fontsize=12)
    ax7.grid(True, alpha=0.3)

    # Add value labels
    for bar, hours in zip(bars, avg_hours_by_day):
        if hours > 0.1:
            ax7.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.05,
                f"{hours:.1f}",
                ha="center",
                va="bottom",
                fontsize=10,
            )

    # 8. Top sessions timeline (bottom right)
    ax8 = plt.subplot(3, 3, 9)

    # Show top 10 longest sessions
    top_sessions = sorted(sessions, key=lambda x: x["duration_minutes"], reverse=True)[
        :10
    ]

    session_labels = []
    session_hours = []
    colors = plt.cm.Set3(np.linspace(0, 1, len(top_sessions)))

    for i, session in enumerate(top_sessions):
        hours = session["duration_minutes"] / 60
        date_str = session["start"].strftime("%m/%d")
        session_labels.append(f"{date_str}\n{hours:.1f}h")
        session_hours.append(hours)

    bars = ax8.barh(range(len(top_sessions)), session_hours, color=colors, alpha=0.8)
    ax8.set_title("Top 10 Longest Sessions", fontsize=14, fontweight="bold")
    ax8.set_xlabel("Duration (Hours)", fontsize=12)
    ax8.set_yticks(range(len(top_sessions)))
    ax8.set_yticklabels(session_labels, fontsize=9)
    ax8.grid(True, alpha=0.3, axis="x")

    # Invert y-axis to show longest at top
    ax8.invert_yaxis()

    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    plt.savefig("programming_time_comprehensive.png", dpi=300, bbox_inches="tight")
    plt.show()


def main():
    print("Creating comprehensive programming time visualization...")

    commits = parse_git_log()
    if not commits:
        print("No commits found!")
        return

    sessions = calculate_programming_sessions(commits, max_gap_minutes=120)
    daily_data = analyze_daily_programming(sessions)

    create_comprehensive_visualization(sessions, daily_data)

    print(f"Visualization saved as 'programming_time_comprehensive.png'")
    print(
        f"Analysis complete: {len(commits)} commits, {len(sessions)} sessions, {len(daily_data)} days"
    )


if __name__ == "__main__":
    main()
