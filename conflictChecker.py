import pandas as pd
from collections import defaultdict

# List of CSV files to check
csv_files = [
    '2024 Schedule_intern.csv',
    'a_matchups.txtSchedule.csv',
    'b_matchups.txtSchedule.csv',
    'c_matchups.txtSchedule.csv'
    # Add more CSV file paths as needed
]

# Dictionary to store bookings
booking_dict = defaultdict(list)

# Read each CSV and store bookings in the dictionary
for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    for index, row in df.iterrows():
        slot = (row['Date'], row['Court'], row['Time'])
        booking_dict[slot].append(row['Title'])

# Find conflicts
conflicts = {slot: titles for slot, titles in booking_dict.items() if len(titles) > 1}

# Output conflicts
if conflicts:
    print("Conflicts found:")
    for slot, titles in conflicts.items():
        print(f"Date: {slot[0]}, Court: {slot[1]}, Time: {slot[2]}")
        for title in titles:
            print(f"  - {title}")
else:
    print("No conflicts found.")

# Optional: Save conflicts to a CSV file
conflicts_df = pd.DataFrame([
    {'Date': slot[0], 'Court': slot[1], 'Time': slot[2], 'Titles': ", ".join(titles)}
    for slot, titles in conflicts.items()
])

conflicts_df.to_csv('conflicts.csv', index=False)