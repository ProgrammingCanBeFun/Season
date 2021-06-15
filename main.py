import os
import sys
import json


class Game:

    def __init__(self, vs: str, points: int, vs_points: int):
        """Set up basic game data."""
        self.vs = vs.title()
        self.points = points
        self.vs_points = vs_points
        if self.points > vs_points:
            self.result = 'w'
        elif self.points == vs_points:
            self.result = 't'
        elif self.points < vs_points:
            self.result = 'l'

    def convert_dict(self):
        """Convert game data into a dictionary."""
        return {'vs': self.vs, 'points': self.points, 'vs_points': self.vs_points, 'result': self.result}


class Season:

    def __init__(self, season_name, team, filename=None):
        """Initialize the season."""
        self.team = team
        self.season_name = season_name
        self.season = []
        if filename:
            self.filename = filename
        else:
            self.filename = f'{self.season_name}_{self.team}.json'
        # Set up season variables.
        self.wins = 0
        self.ties = 0
        self.losses = 0
        self.season_len = 0
        self.points = 0
        self.vs_points = 0
        self.win_percentage = 0.0
        self.point_difference = 0
        self.wins_vs_teams = []
        self.losses_vs_teams = []
        self.ties_vs_teams = []
        self.vs_teams = [self.wins_vs_teams, self.losses_vs_teams, self.ties_vs_teams]
        self.record_vs_teams = []

    def add_to_season(self, *games):
        """Append games to the season list."""
        for item in games:
            item = item.convert_dict()
            self.season.append(item)
            self._gather_stats()

    def load_file(self):
        """Load the current season."""
        with open(self.filename, 'r') as f:
            self.season = json.load(f)
            self._gather_stats()

    def save_to_file(self):
        """Save games to the season file."""
        season_dict = self.season
        with open(self.filename, 'w') as f:
            json.dump(season_dict, f, indent=4)

    def statistics(self):
        """Return the season statistics as a string."""
        self._gather_stats()
        return f'''
        Wins: {self.wins}
        Losses: {self.losses}
        Ties: {self.ties}
        Games Played: {self.season_len}
        Runs Scored: {self.points}
        Runs Against: {self.vs_points}
        Win Percentage: {str(self.win_percentage)[:5]}
        Point Difference: {self.point_difference}
        Record vs Teams: {str(self.f_record_vs_teams).lstrip('[').rstrip(']')}
        '''

    def _gather_stats(self):
        """Gather the basic season statistics (wins, runs, runs against)."""
        # Set all values to zero
        self.wins = 0
        self.ties = 0
        self.losses = 0
        self.season_len = 0
        self.points = 0
        self.vs_points = 0
        self.win_percentage = 0.0
        self.point_difference = 0
        self.wins_vs_teams = []
        self.losses_vs_teams = []
        self.ties_vs_teams = []
        self.record_vs_teams = []
        self.f_record_vs_teams = []
        wins_list = []
        losses_list = []
        ties_list = []
        opponents = []
        # Gather statistics
        for g in self.season:
            # Gather the number of games won, lost, and tied
            g_result = g['result']
            opponent = g['vs']
            if opponent not in opponents:
                opponents.append(opponent)
            if g_result == 'w':
                self.wins += 1
                wins_list.append(g)
            elif g_result == 'l':
                self.losses += 1
                losses_list.append(g)
            elif g_result == 't':
                self.ties += 1
                ties_list.append(g)
            self.season_len += 1
            # Gather the number of runs scored
            g_points = g['points']
            self.points += g_points
            # Gather the number of runs scored by opponents
            g_vs_points = g['vs_points']
            self.vs_points += g_vs_points

        for opponent in opponents:
            self.wins_vs_teams.append(self._records_vs(wins_list, opponent))
            self.losses_vs_teams.append(self._records_vs(losses_list, opponent))
            self.ties_vs_teams.append(self._records_vs(ties_list, opponent))
        # Calculate win percentage
        try:
            self.win_percentage = self.wins / self.season_len
        except ZeroDivisionError:
            self.win_percentage = None

        # Calculate difference in points
        self.point_difference = self.points - self.vs_points

        # Calculate record against opponents
        for x in range(len(opponents)):
            self.record_vs_teams.append({opponents[x]: {'w': self.wins_vs_teams[x][opponents[x]],
                                                        'l': self.losses_vs_teams[x][opponents[x]],
                                                        't': self.ties_vs_teams[x][opponents[x]]}})
            self.f_record_vs_teams.append(
                f"""{opponents[x]}: {self.wins_vs_teams[x][opponents[x]]}-{self.losses_vs_teams[x][opponents[x]]}-{self.ties_vs_teams[x][opponents[x]]}""")

    def _records_vs(self, stat, opponent):
        record_against_team = {opponent: 0}
        for record in stat:
            # f_record = self._convert_dict_to_str(record, 'keys')
            # if f_record == opponent:
            if record['vs'] == opponent:
                record_against_team[opponent] += 1
        return record_against_team

    def _convert_dict_to_str(self, item, dict_type):
        item = str(item).lstrip(f'dict_{dict_type}([\'').rstrip('\'])')
        return item

    def _convert_dict_to_int(self, item, dict_type):
        self._convert_dict_to_str(item, dict_type)
        item = int(item)
        return item

    def create_game(self):
        vs = str(input("Please enter the opponent team."))
        points = int(input("Please enter your team\'s points."))
        vs_points = int(input("Please enter the opponent\'s team\'s points."))
        return Game(vs, points, vs_points)


class CommandPrompt(Season):

    def __init__(self, season_name=input('Season Name: '), team=input('Team Name: ')):
        """Set up season and run the code."""
        Season.__init__(self, season_name, team)
        self.run()

    def run(self):
        """Run the code."""
        """try:"""
        self._access_season()
        self._use_season()
        """except KeyError:
            action = input("File being accessed is corrupt. Would you like to delete it? (y/n)")
            if action == 'y':
                self._delete_file()
            else:
                print("File has not been deleted.")"""

    def _access_season(self):
        """Set up season being used."""
        try:
            self.load_file()
        except FileNotFoundError:
            self._set_up_file()

    def _set_up_file(self):
        """Make file ready for editing."""
        self.save_to_file()
        print("New season created.")

    def _use_season(self):
        action2 = str(input("""Press c + enter to create a game. Press s + enter to view season statistics.
    Press q + enter to quit. Press d + enter to delete the season. Press f + enter to save your season to the file.
    Press p + enter to print out your current season. Press e + enter to remove a game from the season.
    If your season is not saved to the file, your progress will be lost."""))
        if action2 == 'c':
            self._game_creation(self.create_game())
        elif action2 == 's':
            print(self.statistics())
            self._use_season()
        elif action2 == 'q':
            sys.exit()
        elif action2 == 'd':
            self._delete_file()
        elif action2 == 'f':
            self.save_to_file()
            print("Your season has been saved.")
            self._use_season()
        elif action2 == 'p':
            print(self.season)
            self._use_season()
        elif action2 == 'e':
            self._edit_season()
            self._use_season()
        else:
            print("The action you entered is not valid. Try again.")
            self._use_season()

    def _game_creation(self, new_game=None):
        action3 = str(input("""Press a + enter to add the game to the season. Press c + enter to recreate the game. 
    Press s + enter to add the game to the season and create another game. Press q + enter to exit game creation. 
    Press p + enter to print out your current season.
    (Note: If you do not add the game to the season, you will lose your progress)."""))
        if action3 == 'c':
            self._game_creation(self.create_game())
        elif action3 == 'a':
            if new_game:
                self.add_to_season(new_game)
                print("Your game is saved.")
            else:
                print("No game has been created yet.")
            self._use_season()
        elif action3 == 's':
            if new_game:
                self.add_to_season(new_game)
                print("Your game is saved.")
            else:
                print("No game has been created yet.")
            self._game_creation(self.create_game())
        elif action3 == 'q':
            self._use_season()
        elif action3 == 'p':
            print(self.season)
            self._game_creation()
        else:
            print("The action you entered is not valid. Try again.")
            self._game_creation()

    def _delete_file(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)
            print("File has been deleted.")
        else:
            print("File cannot be deleted.")
            sys.exit()

    def _edit_season(self):
        print(self.season)
        game = input("""Please choose the season game you want to remove by stating which position it is in. 
    e.g. 1, 2, 3. Press a to delete entire season.""")
        try:
            del self.season[int(game) - 1]
        except ValueError:
            if game == 'a':
                del self.season
                self.season = []
            else:
                print("The command you just answered is not valid.")


if __name__ == '__main__':
    command_prompt = CommandPrompt()
