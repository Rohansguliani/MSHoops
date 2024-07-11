import pandas as pd
from collections import defaultdict
from datetime import datetime, timedelta

# Function to get the start (Monday) and end (Friday) dates of a week given a date
def get_week_start_end(date):
    start_of_week = date - timedelta(days=date.weekday())
    end_of_week = start_of_week + timedelta(days=4)
    return start_of_week.strftime('%m/%d/%Y'), end_of_week.strftime('%m/%d/%Y')

# Function to check for conflicts in the schedule
def check_conflicts(schedule_path):
    # Read the schedule CSV
    schedule_df = pd.read_csv(schedule_path)
    
    # Dictionary to store bookings
    booking_dict = defaultdict(list)
    team_daily_play = defaultdict(lambda: defaultdict(int))
    team_weekly_play = defaultdict(lambda: defaultdict(int))
    team_weekend_play = defaultdict(list)

    # Iterate over each row in the DataFrame
    for index, row in schedule_df.iterrows():
        slot = (row['Date'], row['Court'], row['Time'])
        booking_dict[slot].append(row['Title'])

        date = pd.to_datetime(row['Date'], format='%m/%d/%Y')
        week = date.isocalendar()[1]
        home_team = row['Home']
        away_team = row['Away']

        # Track daily and weekly play counts
        team_daily_play[home_team][date] += 1
        team_daily_play[away_team][date] += 1
        team_weekly_play[home_team][week] += 1
        team_weekly_play[away_team][week] += 1
        
        # Track weekend play
        if date.weekday() >= 5:  # Saturday or Sunday
            team_weekend_play[home_team].append(date)
            team_weekend_play[away_team].append(date)

    # Find slot conflicts
    slot_conflicts = {slot: titles for slot, titles in booking_dict.items() if len(titles) > 1}

    # Find daily double bookings
    daily_conflicts = {team: dates for team, dates in team_daily_play.items() if any(count > 1 for count in dates.values())}

    # Find weekly overbookings (more than 2 games in a week)
    weekly_conflicts = defaultdict(list)
    for team, weeks in team_weekly_play.items():
        for week, count in weeks.items():
            if count > 2:
                # Get the start and end date of the week
                dates_in_week = [date for date in team_daily_play[team].keys() if date.isocalendar()[1] == week]
                start_of_week, end_of_week = get_week_start_end(dates_in_week[0])
                weekly_conflicts[team].append((start_of_week, end_of_week))

    # Find weekend play conflicts
    weekend_conflicts = {team: dates for team, dates in team_weekend_play.items() if dates}

    # Output conflicts
    if slot_conflicts or daily_conflicts or weekly_conflicts or weekend_conflicts:
        if slot_conflicts:
            print("Slot conflicts found:")
            for slot, titles in slot_conflicts.items():
                print(f"Date: {slot[0]}, Court: {slot[1]}, Time: {slot[2]}")
                for title in titles:
                    print(f"  - {title}")
        if daily_conflicts:
            print("\nDaily conflicts found (teams playing more than once a day):")
            for team, dates in daily_conflicts.items():
                for date, count in dates.items():
                    if count > 1:
                        print(f"Team: {team} Date: {date.strftime('%m/%d/%Y')} Count: {count}")
        if weekly_conflicts:
            print("\nWeekly conflicts found (teams playing more than twice a week):")
            for team, weeks in weekly_conflicts.items():
                for week in weeks:
                    print(f"Team: {team} Week: {week[0]} to {week[1]}")
        if weekend_conflicts:
            print("\nWeekend conflicts found (teams playing on weekends):")
            for team, dates in weekend_conflicts.items():
                for date in dates:
                    print(f"Team: {team} Date: {date.strftime('%m/%d/%Y')}")
    else:
        print("No conflicts found.")

    # Save conflicts to a CSV file
    slot_conflicts_df = pd.DataFrame([
        {'Type': 'Slot', 'Date': slot[0], 'Court': slot[1], 'Time': slot[2], 'Details': ", ".join(titles)}
        for slot, titles in slot_conflicts.items()
    ])
    daily_conflicts_df = pd.DataFrame([
        {'Type': 'Daily', 'Team': team, 'Date': date.strftime('%m/%d/%Y'), 'Count': count}
        for team, dates in daily_conflicts.items()
        for date, count in dates.items() if count > 1
    ])
    weekly_conflicts_df = pd.DataFrame([
        {'Type': 'Weekly', 'Team': team, 'Week Start': week[0], 'Week End': week[1]}
        for team, weeks in weekly_conflicts.items()
        for week in weeks
    ])
    weekend_conflicts_df = pd.DataFrame([
        {'Type': 'Weekend', 'Team': team, 'Date': date.strftime('%m/%d/%Y')}
        for team, dates in weekend_conflicts.items()
        for date in dates
    ])

    conflicts_df = pd.concat([slot_conflicts_df, daily_conflicts_df, weekly_conflicts_df, weekend_conflicts_df], ignore_index=True)
    conflicts_df.to_csv('conflicts.csv', index=False)
    print("Conflicts saved to 'conflicts.csv'")

# Check for conflicts in 'schedule.csv'
schedule_path = 'schedule.csv'
check_conflicts(schedule_path)