import random

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

# Generate all possible matchups
all_possible_matchups = [create_matchup(team1, team2) for i, team1 in enumerate(teams) for team2 in teams[i+1:]]
random.shuffle(all_possible_matchups)

# Select matchups ensuring each team plays exactly 8 games
for matchup in all_possible_matchups:
    team1, team2 = matchup
    if games_played[team1] < num_games_per_team and games_played[team2] < num_games_per_team:
        selected_matchups.append((team1, team2))
        games_played[team1] += 1
        games_played[team2] += 1
    if all(games_played[team] == num_games_per_team for team in teams):
        break

# Save the matchups to a text file
with open('c_matchups.txt', 'w') as file:
    for matchup in selected_matchups:
        file.write(f"{matchup[0]} vs {matchup[1]}\n")