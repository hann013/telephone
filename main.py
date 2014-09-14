import webapp2
import jinja2
import os
import json
import logging

from google.appengine.ext import ndb

class Game(ndb.Model):
    game_creator = ndb.StringProperty(required=True)
    players = ndb.StringProperty(repeated=True)
    game_name = ndb.StringProperty(required=True)
    started = ndb.BooleanProperty(required=True, default=False)
    msg = ndb.StringProperty(repeated=True)
    passcode = ndb.StringProperty(required=False)
    playerLimit = ndb.IntegerProperty( required=False)
    ended = ndb.BooleanProperty(required=True, default=False)

class HomeHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        template = jinja_environment.get_template('home.html')
        self.response.out.write(template.render(template_values))

class AboutUsHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        template = jinja_environment.get_template('aboutus.html')
        self.response.out.write(template.render(template_values))

class InstructionsHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        template = jinja_environment.get_template('instructions.html')
        self.response.out.write(template.render(template_values))

class LoginHandler(webapp2.RequestHandler):
    def get(self):
        choice = self.request.get('choice')
        user = self.request.get('user')
        
        template_values = {
            'choice' : choice,
            'user' : user,
        }

        if choice == "existing-game":
            query = Game.query().fetch()
            template_values['games'] = query

        template = jinja_environment.get_template('login.html')
        self.response.out.write(template.render(template_values)) 

class CheckGamesHandler(webapp2.RequestHandler):
    def post(self):
        choice = self.request.get('choice')
        js_game_count = int(self.request.get('game_count'))  
        query = Game.query()
        list_of_games = query.fetch()   

        if choice == "existing-game":
            if js_game_count < len(list_of_games):
                self.response.headers['Content-Type'] = 'application/json'   
                obj = {
                    'more-games': 'true', 
                  } 
                self.response.out.write(json.dumps(obj))
            else:
                self.response.headers['Content-Type'] = 'application/json'   
                obj = {
                    'more-games': 'false', 
                  } 
                self.response.out.write(json.dumps(obj)) 

class AddGamesHandler(webapp2.RequestHandler):
    def get(self):
        query = Game.query()
        list_of_games = query.filter(Game.started==False)

        self.response.headers['Content-Type'] = 'application/json'   
        obj = {
            'all-games' : [dict(name=game.game_name, creator=game.game_creator) for game in list_of_games], 
          } 
        self.response.out.write(json.dumps(obj))

class WaitHandler(webapp2.RequestHandler):
    def get(self):
        game_name = self.request.get('game_name')
        user = self.request.get('user')
        query = Game.query()
        query = query.filter(Game.game_name==game_name)
        games = query.fetch()
        game = games[0]

        if user not in game.players: 
            game.players.append(user)
            logging.info("WAIT HANDLER:" + str(game.msg))
            game.put()

        template_values = {
            'game' : game,
            'user' : user,
        }       
            
        template = jinja_environment.get_template('wait.html')
        self.response.out.write(template.render(template_values))

class CheckPlayersHandler(webapp2.RequestHandler):
    def post(self):
        js_player_count = int(self.request.get('player_count'))
        game_name = self.request.get('game_name')
        query = Game.query()
        query = query.filter(Game.game_name==game_name)
        games = query.fetch()
        game = games[0]
        
        if js_player_count < len(game.players):
            self.response.headers['Content-Type'] = 'application/json'   
            obj = {
                'more-players': 'true', 
              } 
            self.response.out.write(json.dumps(obj)) 
        else:
            self.response.headers['Content-Type'] = 'application/json'   
            obj = {
                'more-players': 'false', 
              } 
            self.response.out.write(json.dumps(obj))

class AddPlayersHandler(webapp2.RequestHandler):
    def get(self):
        game_name = self.request.get('game_name')
        query = Game.query()
        query = query.filter(Game.game_name==game_name)
        games = query.fetch()
        game = games[0]

        self.response.headers['Content-Type'] = 'application/json'   
        obj = {
            'all-players' : game.players, 
          } 
        self.response.out.write(json.dumps(obj))

class StartHandler(webapp2.RequestHandler):
    def get(self):
        return self.post()

    def post(self):
        logging.info('TRYING TO START')
        game_name = self.request.get('game_name')
        ID = self.request.get('id')
        query = Game.query()
        query = query.filter(Game.game_name==game_name)
        games = query.fetch()
        game = games[0]

        if game.started == False:
            game.started = True
            logging.info("START HANDLER:" + str(game.msg))
            game.put()

        template_values = {
            'game': game,
            'ID' : ID,
        }
        template = jinja_environment.get_template('start.html')
        self.response.out.write(template.render(template_values))


 
class StartedHandler(webapp2.RequestHandler):
    def post(self):
        game_name = self.request.get('game_name')
        query = Game.query()
        query = query.filter(Game.game_name==game_name)
        games = query.fetch()
        game = games[0]

        if game.started == True:
            self.response.headers['Content-Type'] = 'application/json'   
            obj = {
                'ready': 'true', 
              } 
            self.response.out.write(json.dumps(obj))

class GameHandler(webapp2.RequestHandler):
    def get(self):
        game_name = self.request.get('game_name')
        ID = self.request.get('id')
        ID = int(ID)
        print ID

        query = Game.query()
        query = query.filter(Game.game_name==game_name)
        games = query.fetch()
        game = games[0]
        nextID = ID + 1

        template_values = {
            'game': game,
            'ID' : ID,
            'nextID' : nextID,
        }

        template = jinja_environment.get_template('game.html')
        self.response.out.write(template.render(template_values))

class CheckMessageHandler(webapp2.RequestHandler):
    def get(self):
        return self.post()

    def post(self):
        game_name = self.request.get('game_name')
        ID = self.request.get('id')
        ID = int(ID)
        query = Game.query()
        query = query.filter(Game.game_name==game_name)
        games = query.fetch()
       
        if games:
            game = games[0]

            if ID > 0 and len(game.msg) == ID:
                if game.msg[ID-1]:
                    self.response.headers['Content-Type'] = 'application/json'   
                    obj = {
                        'message-received' : 'true',
                        'message' : game.msg[ID-1],
                      } 
                    self.response.out.write(json.dumps(obj))
                else:
                    self.response.headers['Content-Type'] = 'application/json'   
                    obj = {
                        'message-received': 'false', 
                      } 
                    self.response.out.write(json.dumps(obj))

class DisplayMessageHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'   
        obj = {
            'message-received': 'false', 
          } 
        self.response.out.write(json.dumps(obj))

class SendMessageHandler(webapp2.RequestHandler):
    def get(self):
        logging.info('SENDING MESSAGE')
        game_name = self.request.get('game_name')
        ID = self.request.get('id')
        message = self.request.get('message')
        message = message.strip('<>')
        query = Game.query()
        query = query.filter(Game.game_name==game_name)
        games = query.fetch()
        game = games[0]
        game.msg.append(message)
        logging.info("SEND MESSAGE HANDLER:" + str(game.msg))        
        game.put()
        query = Game.query()
        query = query.filter(Game.game_name==game_name)
        games = query.fetch()
        game = games[0]
        logging.info('TESTESTESTESTESTS' + str(game.msg))
        self.redirect("/sent?id="+ID+"&game_name="+game_name)

class CreateHandler(webapp2.RequestHandler):
    def get(self):
        game_name = self.request.get('game_name')
        game_creator = self.request.get('game_creator')
        user = self.request.get('user')
        newGame = Game(game_creator=game_creator, game_name=game_name, started=False, players=[game_creator])
        newGame.put()
        logging.info("CREATE HANDLER:" + str(newGame.msg))
        template_values = {
            'game': newGame,
        }
        template = jinja_environment.get_template('create.html')
        self.response.out.write(template.render(template_values))

class SentHandler(webapp2.RequestHandler):
    def get(self):
        game_name = self.request.get('game_name')
        ID = self.request.get('id')
        ID = int(ID)
        query = Game.query()
        query = query.filter(Game.game_name==game_name)
        games = query.fetch()
        game = games[0]
        print "Sent"
        logging.info('TESTESTESTESTESTS' + str(game.msg))
        
        if ID >= int(len(game.players)):
            logging.info('Ended')
            logging.info('ID: ' + str(ID))
            logging.info('LENGTH OF PLAYERS ARRAY: ' + str(len(game.players)))
            logging.info('TESTESTESTESTESTS' + str(game.msg))

            self.redirect("/endgame?game_name="+game_name)
        
        template_values = {
            "game" : game,
        }
        template = jinja_environment.get_template('sent.html')
        self.response.out.write(template.render(template_values))

class EndedHandler(webapp2.RequestHandler):
    def post(self):
        game_name = self.request.get('game_name')
        query = Game.query()
        query = query.filter(Game.game_name==game_name)
        games = query.fetch()
        game = games[0]

        if game.ended == True:
            self.response.headers['Content-Type'] = 'application/json'   
            obj = {
                'ended': 'true', 
              } 
            self.response.out.write(json.dumps(obj))
        else:
            self.response.headers['Content-Type'] = 'application/json'   
            obj = {
                'ended': 'false', 
              } 
            self.response.out.write(json.dumps(obj))

class EndHandler(webapp2.RequestHandler):
    def get(self):
        game_name = self.request.get('game_name')
        query = Game.query()
        query = query.filter(Game.game_name==game_name)
        games = query.fetch()
        game = games[0]
        game.ended = True
        logging.info("END HANDLER:" + str(game.msg))
        game.put()
        template_values = {
            'game' : game,
            'number_of_msgs' : len(game.msg),
        }

        start_message = game.msg[0].lower()
        start_message = start_message.replace(" ", "")

        end_message = game.msg[len(game.msg)-1].lower()
        end_message = end_message.replace(" ", "")

        if start_message == end_message:
            template_values['game_result'] = "success"
        else:
            template_values['game_result'] = "telephone broken"

        template = jinja_environment.get_template('endgame.html')
        self.response.out.write(template.render(template_values))

jinja_environment = jinja2.Environment(loader=
    jinja2.FileSystemLoader(os.path.dirname(__file__)))

routes = [
    ('/', HomeHandler),
    ('/aboutus', AboutUsHandler),
    ('/instructions', InstructionsHandler),
    ('/login', LoginHandler),
    ('/new-games', CheckGamesHandler),
    ('/add-games', AddGamesHandler),
    ('/wait', WaitHandler),
    ('/new-players', CheckPlayersHandler),
    ('/add-players', AddPlayersHandler),
    ('/start', StartHandler),
    ('/started', StartedHandler),
    ('/game', GameHandler),
    ('/receive-msg', CheckMessageHandler),
    ('/display-msg', DisplayMessageHandler),
    ('/store-msg', SendMessageHandler),
    ('/create', CreateHandler),
    ('/sent', SentHandler),
    ('/ended', EndedHandler),
    ('/endgame', EndHandler),
]

app = webapp2.WSGIApplication(routes, debug=False)