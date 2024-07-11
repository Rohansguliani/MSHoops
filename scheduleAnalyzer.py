import pandas as pd
from collections import defaultdict

# Function to analyze the schedule
def analyze_schedule(schedule_path):
    # Read the schedule CSV
    schedule_df = pd.read_csv(schedule_path)
    
    # Initialize a dictionary to store the results
    team_schedule = defaultdict(lambda: {'count': 0, 'dates': []})
    
    # Iterate over each row in the DataFrame
    for index, row in schedule_df.iterrows():
        date = row['Date']
        home_team = row['Home']
        away_team = row['Away']
        
        # Update the home team schedule
        team_schedule[home_team]['count'] += 1
        team_schedule[home_team]['dates'].append(date)
        
        # Update the away team schedule
        team_schedule[away_team]['count'] += 1
        team_schedule[away_team]['dates'].append(date)
    
    # Convert the results to a DataFrame for better visualization
    results = []
    for team, data in team_schedule.items():
        # Sort dates in chronological order
        sorted_dates = sorted(data['dates'], key=lambda date: pd.to_datetime(date, format='%m/%d/%Y'))
        results.append({
            'Team': team,
            'Games Played': data['count'],
            'Dates': sorted_dates
        })
    
    # Create a DataFrame
    results_df = pd.DataFrame(results)

    # Split dates into separate columns
    max_dates = max(results_df['Dates'].apply(len))
    dates_columns = pd.DataFrame(results_df['Dates'].tolist(), columns=[f'Date {i+1}' for i in range(max_dates)])
    results_df = pd.concat([results_df.drop(columns=['Dates']), dates_columns], axis=1)
    
    return results_df

# Analyze the schedule and save the results
schedule_path = 'schedule.csv'
results_df = analyze_schedule(schedule_path)
results_df.to_csv('team_schedule_analysis.csv', index=False)
