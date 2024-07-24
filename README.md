# MSHoops schedule generator

The following description was generated by the GitHub Copilot command @workspace /explain

## Files and Their Purposes

* **CSV and Text Files:**
These files (`2024 Schedule_intern.csv`, `a_matchups.txt`, `b_matchups.txt`, `c_matchups.txt`, `conflicts.csv`, etc.) store data related to game schedules, team matchups, and identified scheduling conflicts.
* `conflictChecker.py` and `conflictCheckerOld.py`: These scripts are responsible for checking the generated schedules for any conflicts. Conflicts can include slot conflicts (two games scheduled at the same time and place), daily conflicts (teams playing more than once a day), weekly conflicts (teams playing more than twice a week), and weekend conflicts (teams playing on weekends). The `conflictCheckerOld.py` script also includes functionality to save identified conflicts to a CSV file (`conflicts.csv`).
* `gameScheduler.py`: This script appears to be the main driver for generating the game schedule. It reads existing schedules to avoid conflicts, reads matchups from text files, and generates a new schedule considering available courts, times, and days of the week. It likely uses the `conflictChecker.py` module to check for and resolve any conflicts in the generated schedule.
* `resolve_conflicts.py`: While not explicitly detailed, this script is presumably used to resolve conflicts identified by the conflict checker, possibly by rescheduling games to different times or locations.
* **Analysis Files (`scheduleAnalyzer.py`, `team_schedule_analysis.csv`, `intern_team_schedule_analysis.csv`)**: These files are likely used for analyzing the generated schedules, possibly evaluating metrics like the distribution of games across teams, time slots, and locations.

## Key Functionalities

* **Schedule Generation**: The `gameScheduler.py` script generates a schedule based on matchups, available courts and times, and an existing schedule to avoid conflicts.
* **Conflict Checking**: The `conflictCheckerOld.py` script checks the generated schedule for various types of conflicts and saves any identified conflicts to a CSV file.
* **Conflict Resolution**: Although not explicitly shown, the project includes mechanisms for resolving scheduling conflicts, possibly through the `resolve_conflicts.py` script or functionality within `gameScheduler.p`y`.
* **Schedule Analysis**: The project includes tools for analyzing the generated schedules, assessing the fairness and balance of the game distribution among teams.

This project combines data handling (reading from and writing to CSV and text files), date and time manipulation, and algorithmic scheduling to manage and optimize game schedules for a sports league or tournament.