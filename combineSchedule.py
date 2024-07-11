import pandas as pd

# List of CSV files to combine
csv_files = [
    'a_matchups.txtSchedule.csv',
    'b_matchups.txtSchedule.csv',
    'c_matchups.txtSchedule.csv',
    '2024 Schedule_intern.csv'
]

# Columns required for the final schedule
columns = ['Title', 'Home', 'Away', 'Court', 'Date', 'Time', 'Score', 'Winner', 'HomeScore', 'AwayScore']

# Create an empty DataFrame with the required columns
combined_schedule = pd.DataFrame(columns=columns)

# Read and append each CSV file
for file in csv_files:
    df = pd.read_csv(file)
    # Ensure all required columns are present
    for col in columns:
        if col not in df.columns:
            df[col] = ''
    # Append to the combined schedule
    combined_schedule = pd.concat([combined_schedule, df], ignore_index=True)


# Save the combined schedule to a CSV file
combined_schedule.to_csv('schedule.csv', index=False)

print("Combined schedule saved to 'schedule.csv'")