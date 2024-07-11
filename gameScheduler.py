from datetime import datetime, timedelta
import random
from collections import defaultdict
import pandas as pd
from conflictChecker import check_conflicts, save_conflicts

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

# Function to resolve conflicts by moving games to the next week
def resolve_conflicts(schedule_df, slot_conflicts, daily_conflicts, weekly_conflicts, weekend_conflicts):
    for conflict in slot_conflicts:
        for title in slot_conflicts[conflict]:
            index = schedule_df[schedule_df['Title'] == title].index[0]
            date = pd.to_datetime(schedule_df.at[index, 'Date'], format='%m/%d/%Y')
            new_date = date + timedelta(weeks=1)
            while new_date > end_date:
                new_date -= timedelta(weeks=1)
            print(f"Moving {schedule_df.at[index, 'Home']} vs {schedule_df.at[index, 'Away']} from {date.strftime('%m/%d/%Y')} to {new_date.strftime('%m/%d/%Y')}")
            schedule_df.at[index, 'Date'] = new_date.strftime('%m/%d/%Y')
    
    for team, dates in daily_conflicts.items():
        for date, count in dates.items():
            if count > 1:
                index = schedule_df[(schedule_df['Date'] == date.strftime('%m/%d/%Y')) & ((schedule_df['Home'] == team) | (schedule_df['Away'] == team))].index[0]
                new_date = date + timedelta(weeks=1)
                while new_date > end_date:
                    new_date -= timedelta(weeks=1)
                print(f"Moving {team} game from {date.strftime('%m/%d/%Y')} to {new_date.strftime('%m/%d/%Y')}")
                schedule_df.at[index, 'Date'] = new_date.strftime('%m/%d/%Y')
    
    for team, weeks in weekly_conflicts.items():
        for week in weeks:
            for date in pd.date_range(start=week[0], end=week[1]):
                if date.weekday() < days_of_week:
                    index = schedule_df[(schedule_df['Date'] == date.strftime('%m/%d/%Y')) & ((schedule_df['Home'] == team) | (schedule_df['Away'] == team))].index[0]
                    new_date = date + timedelta(weeks=1)
                    while new_date > end_date:
                        new_date -= timedelta(weeks=1)
                    print(f"Moving {team} game from {date.strftime('%m/%d/%Y')} to {new_date.strftime('%m/%d/%Y')}")
                    schedule_df.at[index, 'Date'] = new_date.strftime('%m/%d/%Y')
    
    for team, dates in weekend_conflicts.items():
        for date in dates:
            index = schedule_df[(schedule_df['Date'] == date.strftime('%m/%d/%Y')) & ((schedule_df['Home'] == team) | (schedule_df['Away'] == team))].index[0]
            new_date = date + timedelta(weeks=1)
            while new_date > end_date:
                new_date -= timedelta(weeks=1)
            print(f"Moving {team} game from weekend {date.strftime('%m/%d/%Y')} to {new_date.strftime('%m/%d/%Y')}")
            schedule_df.at[index, 'Date'] = new_date.strftime('%m/%d/%Y')
    
    return schedule_df

# Function to generate the schedule
def generate_schedule(matchups, start_date, end_date, days_of_week, existing_slots):
    schedule = []
    team_daily_play = defaultdict(lambda: defaultdict(int))
    team_weekly_play = defaultdict(lambda: defaultdict(int))
    daily_schedule = defaultdict(lambda: defaultdict(set))

    current_date = start_date

    while current_date <= end_date:
        if current_date.weekday() >= days_of_week:  # Skip weekends
            current_date += timedelta(days=(7 - current_date.weekday()))
            continue
        
        available_matchups = matchups[:]
        random.shuffle(available_matchups)  # Shuffle to add randomness to the scheduling
        
        for matchup in available_matchups:  # Iterate over a copy of the list to allow removal
            home_team, away_team = matchup
            
            # Check if either team has already played 2 times this week
            if team_weekly_play[home_team][current_date.isocalendar()[1]] >= 2 or team_weekly_play[away_team][current_date.isocalendar()[1]] >= 2:
                continue

            # Check if either team has already played on this date
            if team_daily_play[home_team][current_date] > 0 or team_daily_play[away_team][current_date] > 0:
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
                    team_daily_play[home_team][current_date] += 1
                    team_daily_play[away_team][current_date] += 1
                    team_weekly_play[home_team][current_date.isocalendar()[1]] += 1
                    team_weekly_play[away_team][current_date.isocalendar()[1]] += 1

                    # Mark the date and time the teams are playing
                    daily_schedule[current_date][court].add(time)

                    # Add slot to existing slots to avoid future conflicts
                    existing_slots.add(slot)

                    # Remove the matchup from the list
                    matchups.remove(matchup)

                    break

        current_date += timedelta(days=1)
        if current_date.weekday() >= days_of_week:  # Skip to next Monday if weekend
            current_date += timedelta(days=(7 - current_date.weekday()))

    return schedule

# Main function to run the scheduling and conflict resolution
def main():
    all_schedules = []

    # Loop through each matchup file and generate the schedule
    for matchup_file in matchup_files:
        matchups = read_matchups(matchup_file)
        schedule = generate_schedule(matchups, start_date, end_date, days_of_week, existing_slots)

        schedule_df = pd.DataFrame(schedule)
        slot_conflicts, daily_conflicts, weekly_conflicts, weekend_conflicts = check_conflicts(schedule_df)
        iteration = 0
        max_iterations = 10
        while slot_conflicts or daily_conflicts or weekly_conflicts or weekend_conflicts:
            print(f"Iteration {iteration}: Resolving conflicts...")
            schedule_df = resolve_conflicts(schedule_df, slot_conflicts, daily_conflicts, weekly_conflicts, weekend_conflicts)
            slot_conflicts, daily_conflicts, weekly_conflicts, weekend_conflicts = check_conflicts(schedule_df)
            iteration += 1
            if iteration >= max_iterations:
                print(f"Reached maximum iterations ({max_iterations}). Conflicts may still exist.")
                break

        all_schedules.extend(schedule_df.to_dict('records'))

    # Convert the combined schedule to a DataFrame for display
    generated_schedule = pd.DataFrame(all_schedules)

    # Save the DataFrame to a CSV file
    csv_file_path = "schedule.csv"
    generated_schedule.to_csv(csv_file_path, index=False)
    print(f"Schedule saved to {csv_file_path}")

if __name__ == "__main__":
    main()