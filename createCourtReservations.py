import csv
from datetime import datetime, timedelta

# Variables
courts = ["Court 43", "Court 93", "Court Redwest"]
start_date = datetime.strptime("2024-07-01", "%Y-%m-%d")
end_date = datetime.strptime("2024-09-01", "%Y-%m-%d")
time_slots = ["4:30", "5:30", "6:30"]

# Function to generate all reservation slots
def generate_reservations(courts, start_date, end_date, time_slots):
    reservations = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:  # Only weekdays
            for court in courts:
                for time in time_slots:
                    reservation = {
                        "Title": court,
                        "Date": current_date.strftime("%m/%d/%Y"),
                        "Time": time,
                        "Status": "Available"
                    }
                    reservations.append(reservation)
        current_date += timedelta(days=1)
    return reservations

# Function to update reservations based on input CSV file
def update_reservations_from_input(input_file, reservations):
    with open(input_file, mode='r', newline='') as infile:
        reader = csv.DictReader(infile)
        existing_reservations = list(reader)
        for res in reservations:
            for existing in existing_reservations:
                if (res["Title"] == "Court " + existing["Court"] and
                    res["Date"] == datetime.strptime(existing["Date"], "%m/%d/%Y").strftime("%d/%m/%Y") and
                    res["Time"] == existing["Time"]):
                    res["Status"] = "Booked"
    return reservations

# Function to write reservations to CSV file
def write_reservations_to_csv(output_file, reservations):
    with open(output_file, mode='w', newline='') as outfile:
        fieldnames = ["Title", "Date", "Time", "Status"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for reservation in reservations:
            writer.writerow(reservation)

# Main script execution
input_file = "schedule.csv"  # Replace with your input file path
output_file = "court_reservations.csv"  # Replace with your desired output file path

reservations = generate_reservations(courts, start_date, end_date, time_slots)
updated_reservations = update_reservations_from_input(input_file, reservations)
write_reservations_to_csv(output_file, updated_reservations)

print("Reservations have been processed and saved to", output_file)
