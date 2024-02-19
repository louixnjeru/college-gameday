import datetime, requests
from NCAA_Sanitiser import NCAA_Sanitiser
from model import Model

class NCAA_API(BaseException):
    
    def __init__(self, apiKey, modelFilePath, modelFeatures):
        self.apiKey = {'api_key': apiKey}
        self.sanitiser = NCAA_Sanitiser()
        self.model = Model(modelFilePath ,modelFeatures)
        
    def getTodaysGames(self):
        today = datetime.date.today()
        try:
            gameList = self.__getGameSchedule(today.day, today.month, today.year)
            return self.sanitiser.sanitiseGameList(gameList)
        except TypeError:
            pass
        
        
    def getGamesByDate(self, day, month, year):
        currentYear = datetime.date.today().year
        if (1 < day < 31) or (1 < month < 12) or (2013 < year < currentYear):
            gameList = self.__getGameSchedule(day, month, year)
            return self.sanitiser.sanitiseGameList(gameList)
    
    def __getGameSchedule(self, day, month, year):
        try:
            response = requests.get(f'http://api.sportradar.us/ncaamb/trial/v8/en/games/{year}/{month}/{day}/schedule.json', params=self.apiKey).json()
            return response
        except response.status_code != 200:
            return 'ERROR'
        
    def getGameInfo(self, gameId):
        response = requests.get(f'http://api.sportradar.us/ncaamb/trial/v8/en/games/{gameId}/summary.json', params=self.apiKey)
        if response.status_code != 200:
            return []
        
        sanitisedResponse = self.sanitiser.santitiseBoxScore(response.json())
        
        try:
            sanitisedResponse['home']['winner'] = self.model.predict(sanitisedResponse['home']['stats'])
            sanitisedResponse['away']['winner'] = self.model.predict(sanitisedResponse['away']['stats'])
        except AttributeError as e:
            raise
        
        return sanitisedResponse
    
c = NCAA_API('cad4w7zgdw9bx7ee4r8vm389', 'models/vecModel2.joblib', ['FGPD', 'ASTRD', 'TASTRD', 'FTRD', 'FTCRD', '2PPD', '3PPD', 'FTPD', 'FGRRD'])
# gameList = c.getTodaysGames()
# sGameList = [game for game in gameList if game['fullCoverage'] == True]
        
    