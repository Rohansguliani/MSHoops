from datetime import datetime, timedelta
import random
from collections import defaultdict
import pandas as pd

# List of matchup files for different leagues
matchup_files = [
    'a_matchups.txt',
    'b_matchups.txt',
    'c_matchups.txt'
]

# Available courts and times
courts = ["43", "92", "redwest"]
times = ["4:30", "5:30", "6:30"]
start_date = datetime(2024, 7, 15)
end_date = datetime(2024, 8, 23)
days_of_week = 5  # Monday to Friday

# Read existing schedule to avoid conflicts
existing_schedule_path = "2024 Schedule_intern.csv"
existing_schedule = pd.read_csv(existing_schedule_path)

# Convert existing schedule to a set of (date, court, time) tuples for fast lookup
existing_slots = set(zip(existing_schedule['Date'], existing_schedule['Court'], existing_schedule['Time']))

# Function to read matchups from a text file
def read_matchups(file_path):
    with open(file_path, 'r') as file:
        return [line.strip().split(' vs ') for line in file.readlines()]

# Function to generate the schedule
def generate_schedule(matchups, start_date, end_date, days_of_week, existing_slots):
    schedule = []
    team_play_counts = defaultdict(int)
    team_daily_play = defaultdict(set)
    daily_schedule = defaultdict(lambda: defaultdict(set))

    for matchup in matchups:
        match_scheduled = False
        retry_count = 0

        while not match_scheduled and retry_count < 5:
            current_date = start_date

            while current_date <= end_date:
                home_team, away_team = matchup

                # Check if either team has already played 2 times this week
                if team_play_counts[(home_team, current_date.isocalendar()[1])] >= 2 or team_play_counts[(away_team, current_date.isocalendar()[1])] >= 2:
                    current_date += timedelta(days=1)
                    continue

                # Check if either team has already played on this date
                if current_date in team_daily_play[home_team] or current_date in team_daily_play[away_team]:
                    current_date += timedelta(days=1)
                    continue

                # Try to find an available court and time
                for _ in range(5):
                    court = random.choice(courts)
                    time = random.choice(times)
                    slot = (current_date.strftime('%m/%d/%Y'), court, time)

                    if slot not in existing_slots and time not in daily_schedule[current_date][court]:
                        # Schedule the match
                        home_team, away_team = random.sample([home_team, away_team], 2)
                        title = f"{home_team} vs {away_team}"

                        schedule.append({
                            "Title": title,
                            "Home": home_team,
                            "Away": away_team,
                            "Court": court,
                            "Date": current_date.strftime('%m/%d/%Y'),
                            "Time": time
                        })

                        # Increment the play count for the teams
                        team_play_counts[(home_team, current_date.isocalendar()[1])] += 1
                        team_play_counts[(away_team, current_date.isocalendar()[1])] += 1

                        # Mark the date and time the teams are playing
                        team_daily_play[home_team].add(current_date)
                        team_daily_play[away_team].add(current_date)
                        daily_schedule[current_date][court].add(time)

                        # Add slot to existing slots to avoid future conflicts
                        existing_slots.add(slot)

                        match_scheduled = True
                        break

                if match_scheduled:
                    break

                current_date += timedelta(days=1)
                if current_date.weekday() >= days_of_week:  # Skip to next Monday if weekend
                    current_date += timedelta(days=(7 - current_date.weekday()))

            retry_count += 1

    return schedule

# Loop through each matchup file and generate the schedule
for matchup_file in matchup_files:
    matchups = read_matchups(matchup_file)
    schedule = generate_schedule(matchups, start_date, end_date, days_of_week, existing_slots)

    # Convert the schedule to a DataFrame for display
    generated_schedule = pd.DataFrame(schedule)

    # Save the DataFrame to a CSV file
    league_name = matchup_file.split('Matchups.txt')[0]
    csv_file_path = f"{league_name}Schedule.csv"
    generated_schedule.to_csv(csv_file_path, index=False)
