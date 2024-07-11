import pandas as pd
from collections import defaultdict
from datetime import datetime, timedelta
import random

def resolve_conflicts(schedule_path, conflicts_path, output_path, max_iterations=10):
    schedule_df = pd.read_csv(schedule_path)
    conflicts_df = pd.read_csv(conflicts_path)
    
    # Convert date columns to datetime
    schedule_df['Date'] = pd.to_datetime(schedule_df['Date'], format='%m/%d/%Y')
    if 'Date' in conflicts_df.columns:
        conflicts_df['Date'] = pd.to_datetime(conflicts_df['Date'], format='%m/%d/%Y')
    if 'Week Start' in conflicts_df.columns:
        conflicts_df['Week Start'] = pd.to_datetime(conflicts_df['Week Start'], format='%m/%d/%Y')
    if 'Week End' in conflicts_df.columns:
        conflicts_df['Week End'] = pd.to_datetime(conflicts_df['Week End'], format='%m/%d/%Y')
    
    # Load existing slots into a set for fast lookup
    existing_slots = set(zip(schedule_df['Date'], schedule_df['Court'], schedule_df['Time']))
    
    # Available courts and times
    courts = ["43", "92", "redwest"]
    times = ["4:30", "5:30", "6:30"]
    
    def move_conflict_one_week_later(row):
        team = row['Team']
        date = row['Date']
        if pd.notna(date):
            new_date = date + timedelta(weeks=1)
            while new_date > schedule_df['Date'].max() + timedelta(weeks=1):
                new_date -= timedelta(weeks=1)
            print(f"Moving {team} from {date.strftime('%m/%d/%Y')} to {new_date.strftime('%m/%d/%Y')}")
            affected_rows = schedule_df[(schedule_df['Date'] == date) & 
                                        ((schedule_df['Home'] == team) | (schedule_df['Away'] == team))]
            for index, affected_row in affected_rows.iterrows():
                schedule_df.at[index, 'Date'] = new_date
                existing_slots.add((new_date, affected_row['Court'], affected_row['Time']))
                if (affected_row['Date'], affected_row['Court'], affected_row['Time']) in existing_slots:
                    existing_slots.remove((affected_row['Date'], affected_row['Court'], affected_row['Time']))
                else:
                    print(f"Slot to be removed not found: {(affected_row['Date'], affected_row['Court'], affected_row['Time'])}")

    def randomize_court_and_time(row):
        date = row['Date']
        court = row['Court']
        time = row['Time']
        attempts = 0
        while attempts < 5:
            new_court = random.choice(courts)
            new_time = random.choice(times)
            if (date, new_court, new_time) not in existing_slots:
                print(f"Randomizing {date.strftime('%m/%d/%Y')}: Moving from {court}, {time} to {new_court}, {new_time}")
                schedule_df.loc[(schedule_df['Date'] == date) & 
                                (schedule_df['Court'] == court) & 
                                (schedule_df['Time'] == time), ['Court', 'Time']] = [new_court, new_time]
                existing_slots.add((date, new_court, new_time))
                if (date, court, time) in existing_slots:
                    existing_slots.remove((date, court, time))
                else:
                    print(f"Slot to be removed not found: {(date, court, time)}")
                return
            attempts += 1
    
    def resolve_conflict(row):
        conflict_type = row['Type']
        if conflict_type in ['Daily', 'Weekly']:
            move_conflict_one_week_later(row)
        elif conflict_type == 'Slot':
            randomize_court_and_time(row)
    
    iteration = 0
    while not conflicts_df.empty and iteration < max_iterations:
        print(f"Iteration {iteration}: Resolving conflicts...")
        conflicts_df.apply(resolve_conflict, axis=1)
        
        # Recheck for conflicts
        booking_dict = defaultdict(list)
        team_daily_play = defaultdict(lambda: defaultdict(int))
        team_weekly_play = defaultdict(lambda: defaultdict(int))
        team_weekend_play = defaultdict(list)
        
        for index, row in schedule_df.iterrows():
            slot = (row['Date'], row['Court'], row['Time'])
            booking_dict[slot].append(row['Title'])

            date = row['Date']
            week = date.isocalendar()[1]
            home_team = row['Home']
            away_team = row['Away']

            # Track daily and weekly play counts
            team_daily_play[home_team][date] += 1
            team_daily_play[away_team][date] += 1
            team_weekly_play[home_team][week] += 1
            team_weekly_play[away_team][week] += 1
            
            # Track weekend play
            if date.weekday() >= 5:  # Weekend
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
        
        # Collect all conflicts
        conflicts = []
        
        for slot, titles in slot_conflicts.items():
            conflicts.append({
                'Type': 'Slot',
                'Date': slot[0],
                'Court': slot[1],
                'Time': slot[2],
                'Details': ", ".join(titles)
            })
        
        for team, dates in daily_conflicts.items():
            for date, count in dates.items():
                if count > 1:
                    conflicts.append({
                        'Type': 'Daily',
                        'Team': team,
                        'Date': date,
                        'Count': count
                    })
        
        for team, weeks in weekly_conflicts.items():
            for week in weeks:
                conflicts.append({
                    'Type': 'Weekly',
                    'Team': team,
                    'Week Start': week[0],
                    'Week End': week[1]
                })
        
        for team, dates in weekend_conflicts.items():
            for date in dates:
                conflicts.append({
                    'Type': 'Weekend',
                    'Team': team,
                    'Date': date
                })
        
        conflicts_df = pd.DataFrame(conflicts)
        iteration += 1
    
    if iteration >= max_iterations:
        print(f"Maximum iterations ({max_iterations}) reached. Conflicts may still exist.")
    
    # Save the updated schedule
    schedule_df['Date'] = schedule_df['Date'].dt.strftime('%m/%d/%Y')
    schedule_df.to_csv(output_path, index=False)
    print(f"Conflicts resolved. Updated schedule saved to '{output_path}'")

# Helper function to get the start and end of a week
def get_week_start_end(date):
    start_of_week = date - timedelta(days=date.weekday())
    end_of_week = start_of_week + timedelta(days=4)
    return start_of_week.strftime('%m/%d/%Y'), end_of_week.strftime('%m/%d/%Y')

# Run the conflict resolution
schedule_path = 'schedule.csv'
conflicts_path = 'conflicts.csv'
output_path = 'updated_schedule.csv'
resolve_conflicts(schedule_path, conflicts_path, output_path)
