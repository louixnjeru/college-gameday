class NCAA_Sanitiser(BaseException):
    def __init__(self):
        self.gameStatuses = {
            'inprogress': 'Live',
            'scheduled': '',
            'closed': 'F',
            'completed': 'F'
            }
        
        self.gameHalves = {
            1: '1st',
            2: '2nd',
            'OT': 'OT'
            }
        
        self.teams = {'home', 'away'}
    
    def sanitiseGameList(self, gameList):
        if gameList == 'ERROR': return gameList
        
        sanitisedGameList = []
        
        try:
        
            for game in gameList['games']:
                currentGame = {
                    'id': game['id'],
                    'status': self.gameStatuses.get(game['status'],''),
                    'fullCoverage': True if game['coverage'] == 'full' or game.get('track_on_court', None) == True else False,
                    'startTime': game['scheduled'],
                    'timeZone': game['time_zones']['venue'],
                    'broadcasts' : [b['network'] for b in game['broadcasts'] if b['type'] == 'TV' and b.get('locale', None) == 'National'] if 'broadcasts' in game else []
                    }
                
                
                for team in self.teams:
                    currentGame[team] = {
                        'id': game[team]['id'],
                        'teamName': game[team]['name'],
                        'teamCode': game[team]['alias'],
                        }
                    
                    if f'{team}_points' in game:
                        currentGame[team]['teamScore'] = game[f'{team}_points']
                        
                sanitisedGameList.append(currentGame)
                
            return sanitisedGameList
        
        except KeyError() as e:
            raise
    
    def santitiseBoxScore(self, game):  
        try:
            sanitisedGameInfo = {
                'venue': {
                    'name': game['venue']['name'],
                    'city': game['venue']['city'],
                    'state': game['venue']['state'],
                    'coordinates': game['venue']['location'],
                    },
                'id': game['id'],
                'status': self.gameStatuses.get(game['status'],''),
                'startTime': game['scheduled'],
                'timeZone': game['time_zones']['venue'],
                'gameClock': game['clock'],
                'half': self.gameHalves.get(game['half'], None)
                }
            
            for team in self.teams:
                tastrDenominator = (game[team]['statistics']['field_goals_att'] + (0.44 * game[team]['statistics']['free_throws_att']) + game[team]['statistics']['team_turnovers'])
                sanitisedGameInfo[team] = {
                    'id': game[team]['id'],
                    'teamName': f"{game[f'{team}']['market']} {game[f'{team}']['name']}",
                    'teamCode': game[team]['alias'],
                    'points': game[team]['points'],
                    'timeOuts': game[team]['remaining_timeouts'],
                    'halfScores': [h['points'] for h in game[team]['scoring']],
                    'stats': {
                        'FTP': game[team]['statistics']['free_throws_pct'],
                        'ASTR': game[team]['statistics']['assists']/game[team]['statistics']['field_goals_made'] if game[team]['statistics']['field_goals_made'] != 0 else game[team]['statistics']['assists'],
                        'TASTR': game[team]['statistics']['assists']/tastrDenominator if tastrDenominator != 0 else game[team]['statistics']['assists'],
                        'ATR': game[team]['statistics']['assists']/game[team]['statistics']['team_turnovers'] if game[team]['statistics']['team_turnovers'] != 0 else game[team]['statistics']['assists'],
                        'FTR': game[team]['statistics']['free_throws_att']/game[team]['statistics']['field_goals_att'] if game[team]['statistics']['field_goals_att'] != 0 else game[team]['statistics']['free_throws_att'],
                        'FTCR': (game[team]['statistics']['free_throws_att']/game[team]['statistics']['field_goals_att']) * game[team]['statistics']['free_throws_pct'],
                        'FGP': game[team]['statistics']['field_goals_pct'],
                        'FGRR': game[team]['statistics']['offensive_rebounds']/game[team]['statistics']['field_goals_att'] if game[team]['statistics']['field_goals_att'] != 0 else game[team]['statistics']['offensive_rebounds']
                        }
                    }
            
            sanitisedGameInfo['home']['stats']['FGPD'] = sanitisedGameInfo['home']['stats']['FGP'] - sanitisedGameInfo['away']['stats']['FGP']
            sanitisedGameInfo['home']['stats']['ASTRD'] = sanitisedGameInfo['home']['stats']['ASTR'] - sanitisedGameInfo['away']['stats']['ASTR']
            sanitisedGameInfo['home']['stats']['TASTRD'] = sanitisedGameInfo['home']['stats']['TASTR'] - sanitisedGameInfo['away']['stats']['TASTR']
            sanitisedGameInfo['home']['stats']['FTRD'] = sanitisedGameInfo['home']['stats']['FTR'] - sanitisedGameInfo['away']['stats']['FTR']
            sanitisedGameInfo['home']['stats']['FTCRD'] = sanitisedGameInfo['home']['stats']['FTCR'] - sanitisedGameInfo['away']['stats']['FTCR']
            sanitisedGameInfo['home']['stats']['2PPD'] = game['home']['statistics']['two_points_pct'] - game['away']['statistics']['two_points_pct']
            sanitisedGameInfo['home']['stats']['3PPD'] = game['home']['statistics']['three_points_pct'] - game['away']['statistics']['three_points_pct']
            sanitisedGameInfo['home']['stats']['FTPD'] = sanitisedGameInfo['home']['stats']['FTP'] - sanitisedGameInfo['away']['stats']['FTP']
            sanitisedGameInfo['home']['stats']['FGRRD'] = sanitisedGameInfo['home']['stats']['FGRR'] - sanitisedGameInfo['away']['stats']['FGRR']
            
            sanitisedGameInfo['away']['stats']['FGPD'] = -sanitisedGameInfo['home']['stats']['FGPD']
            sanitisedGameInfo['away']['stats']['ASTRD'] = -sanitisedGameInfo['home']['stats']['ASTRD']
            sanitisedGameInfo['away']['stats']['TASTRD'] = -sanitisedGameInfo['home']['stats']['TASTRD']
            sanitisedGameInfo['away']['stats']['FTRD'] = -sanitisedGameInfo['home']['stats']['FTRD']
            sanitisedGameInfo['away']['stats']['FTCRD'] = -sanitisedGameInfo['home']['stats']['FTCRD']
            sanitisedGameInfo['away']['stats']['2PPD'] = -sanitisedGameInfo['home']['stats']['2PPD']
            sanitisedGameInfo['away']['stats']['3PPD'] = -sanitisedGameInfo['home']['stats']['3PPD']
            sanitisedGameInfo['away']['stats']['FTPD'] = -sanitisedGameInfo['home']['stats']['FTPD']
            sanitisedGameInfo['away']['stats']['FGRRD'] = -sanitisedGameInfo['home']['stats']['FGRRD']
            
            return sanitisedGameInfo
        
        except KeyError() as e:
            raise
