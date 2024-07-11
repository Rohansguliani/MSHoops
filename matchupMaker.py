import random
import time

# Read teams from a text file
with open('cTeams.txt', 'r') as file:
    teams = [line.strip() for line in file.readlines()]

# Ensure each team plays 8 games with unique opponents
num_games_per_team = 8

# Track games played by each team
games_played = {team: 0 for team in teams}

# Store matchups to ensure no repetitions
matchup_history = set()

# Selected matchups
selected_matchups = []

# Function to create a matchup string that is order-independent
def create_matchup(team1, team2):
    return tuple(sorted([team1, team2]))

# Function to reset the matchups and tracking structures
def reset_matchups():
    global games_played, matchup_history, selected_matchups
    games_played = {team: 0 for team in teams}
    matchup_history = set()
    selected_matchups = []

# Start timing the computation
start_time = time.time()
timeout = 10  # 1 minute timeout

# Continuously generate matchups until all teams have played 8 games
while any(games_played[team] < num_games_per_team for team in teams):
    iteration_start_time = time.time()
    while any(games_played[team] < num_games_per_team for team in teams):
        current_time = time.time()
        if current_time - iteration_start_time > timeout:
            print(f"Timeout reached. Starting over. Matchups generated in this iteration: {len(selected_matchups)}")
            reset_matchups()
            iteration_start_time = time.time()
            continue

        team1, team2 = random.sample(teams, 2)
        matchup = create_matchup(team1, team2)
        if matchup not in matchup_history and games_played[team1] < num_games_per_team and games_played[team2] < num_games_per_team:
            selected_matchups.append((team1, team2))
            games_played[team1] += 1
            games_played[team2] += 1
            matchup_history.add(matchup)
            if all(games_played[team] == num_games_per_team for team in teams):
                break

# Check for any teams that didn't get enough games and try to balance
for team in teams:
    while games_played[team] < num_games_per_team:
        possible_opponents = [t for t in teams if t != team and games_played[t] < num_games_per_team]
        if not possible_opponents:
            raise ValueError(f"Cannot find enough opponents for {team}.")
        opponent = random.choice(possible_opponents)
        matchup = create_matchup(team, opponent)
        if matchup not in matchup_history:
            selected_matchups.append(matchup)
            games_played[team] += 1
            games_played[opponent] += 1
            matchup_history.add(matchup)

# End timing the computation
end_time = time.time()
elapsed_time = end_time - start_time

# Save the matchups to a text file
with open('c_matchups.txt', 'w') as file:
    for matchup in selected_matchups:
        file.write(f"{matchup[0]} vs {matchup[1]}\n")

print("Matchups generated successfully:")
for matchup in selected_matchups:
    print(f"{matchup[0]} vs {matchup[1]}")

print(f"Time taken to generate matchups: {elapsed_time:.2f} seconds")