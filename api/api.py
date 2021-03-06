#!/usr/bin/env python
import jinja2
import logging
import os
import webapp2

from google.appengine.ext import db
from models import Level, GameAccount, Character, Machine

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
JINJA_ENV = jinja2.Environment(loader = jinja2.FileSystemLoader(TEMPLATE_DIR), autoescape = True)


class MainHand(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = JINJA_ENV.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class FrontHand(MainHand):
    def get(self):
        self.write('<html><head><title>ARTF API</title></head><body>ARTF API 0.0.5</body></html>')


class LevelsHand(MainHand):
    def post(self):
        live_level_data = self.request.get('live_level_data')
        draft_level_data = self.request.get('draft_level_data')
        game_acct_id_str = self.request.get('game_acct_id')
        mach_id_str = self.request.get('mach_id')

        if game_acct_id_str.isdigit() and mach_id_str.isdigit():
            game_acct_id = int(game_acct_id_str)
            mach_id = int(mach_id_str)

            if game_acct_id and mach_id:
                new_level = Level(live_level_data=live_level_data, draft_level_data=draft_level_data, game_acct_id=game_acct_id, mach_id=mach_id)
                new_level.put()

                new_level_id = str(new_level.key().id())
                self.write(new_level_id)
                logging.info('Level ' + new_level_id + ' created')
            else:
                self.write('')
                logging.error('Level upload failed. game_acct_id or mach_id cannot be 0.')
        else:
            self.write('')
            logging.error('Level upload failed. game_acct_id and mach_id must be numbers.')


class LevelsIdHand(MainHand):
    def get(self, level_id):
        entity = Level.get_by_id(int(level_id))

        if entity is None:
            self.write('')
            logging.error('Level download failed. Level ' + level_id + ' does not exist in Datastore.')
        else:
            self.write(entity.live_level_data)
            logging.info('Level ' + level_id  + ' downloaded')

    def post(self, level_id):
        flag = self.request.get('flag')
        game_acct_id_str = self.request.get('game_acct_id')
        live_level_data = self.request.get('live_level_data')
        draft_level_data = self.request.get('draft_level_data')

        entity = Level.get_by_id(int(level_id))

        if entity is None:
            self.write('')
            logging.error('Level manipulation failed. Level does not exist in Datastore.')
        else:
            if flag == 'update':
                if game_acct_id_str != '':
                    entity.game_acct_id = int(game_acct_id_str)
                if live_level_data != '':
                    entity.live_level_data = live_level_data
                if draft_level_data != '':
                    entity.draft_level_data = draft_level_data
                entity.put()
                self.write(level_id)
                logging.info('Level ' + level_id + ' updated')
            elif flag == 'delete':
                entity.delete()
                self.write(level_id)
                logging.info('Level ' + level_id + ' deleted')
            else:
                self.write('')
                logging.error('Level manipulation failed. No manipulation flag set.')


class GameLoginHand(MainHand):
    def post(self):
        input_game_acct_name = self.request.get('game_acct_name')
        input_game_acct_password = self.request.get('game_acct_password')

        entity = db.GqlQuery('SELECT * FROM GameAccount WHERE game_acct_name = :1', input_game_acct_name).get()

        if entity is not None:
            game_acct_id = str(entity.key().id())

            if input_game_acct_password == entity.game_acct_password:
                entity = db.GqlQuery('SELECT * FROM Character WHERE game_acct_id = :1', int(game_acct_id)).get()

                if entity is None:
                    logging.error('Character download for game account ' + game_acct_id +' failed. Character doesn\'t exist for game account.')
                    self.write('')
                else:
                    char_id = str(entity.key().id())
                    self.write(char_id)
                    logging.info('Character ' + char_id + ' logged in') #post location and maybe account name later
            else:
                self.write('')
                logging.info('Login failed for game account ' + game_acct_id + '. Password incorrect.')
        else:
            self.write('')
            logging.info('Login failed for game account ' + input_game_acct_name + '. game_acct_name doesn\'t exist.')


class GameRegisterHand(MainHand):
    def post(self):
        input_game_acct_name = self.request.get('game_acct_name')
        input_game_acct_password = self.request.get('game_acct_password')
        input_char_data = self.request.get('char_data')

        query = db.GqlQuery('SELECT * FROM GameAccount WHERE game_acct_name = :1', input_game_acct_name)

        if query.count() == 0:
            new_game_acct = GameAccount(game_acct_name=input_game_acct_name, game_acct_password=input_game_acct_password)
            new_game_acct.put()

            game_acct_id = new_game_acct.key().id()

            new_char = Character(char_data=input_char_data, game_acct_id=game_acct_id)
            new_char.put()

            game_acct_id = str(game_acct_id)  # must be cast to str for logging
            self.write(game_acct_id)
            logging.info('Game account ' + game_acct_id + ' created')
        else:
            logging.error('Registration failed for ' + input_game_acct_name + '. game_acct_name already exists.')
            self.write('')


class CharactersHand(MainHand):
    def get(self, character_id):
        entity = Character.get_by_id(int(character_id))

        if entity is None:
            self.write('')
            logging.error('Character download failed. Character ' + character_id + ' does not exist in Datastore.')
        else:
            self.write(entity.char_data)
            logging.info('Character ' + character_id + ' downloaded')

    def post(self, character_id):
        char_data = self.request.get('char_data')

        entity = Character.get_by_id(int(character_id))

        if entity is None:
            self.write('')
            logging.error('Character update failed. Character does not exist in Datastore.')
        else:
            if char_data != '':
                entity.char_data = char_data
                entity.put()
                self.write(character_id)
                logging.info('Character ' + character_id + ' updated')
            else:
                self.write('')
                logging.error('Character update failed. Character ' + character_id + ' cannot have empty character data.')


class MachineHand(MainHand):
    def post(self):
        input_mach_name = self.request.get('mach_name')
        input_venue_name = self.request.get('venue_name')

        new_mach = Machine(mach_name=input_mach_name, venue_name=input_venue_name)
        new_mach.put()

        mach_id = str(new_mach.key().id())

        self.write(mach_id)
        logging.info('Machine ' + mach_id + ' created')


class DSConnHand(MainHand):
    def get(self):
        query = Level.all()
        levels = list(query)
        self.render('dsconn.html', levels = levels)


class UploadTestHand(MainHand):
    def get(self):
        self.render('uploadtest.html')

from google.appengine.ext import blobstore
upload_url = blobstore.create_upload_url('/upload')
from google.appengine.ext.webapp import blobstore_handlers
import urllib

class BlobstoreTest(MainHand):
    def get(self):
        self.write('<html><body>')
        self.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
        self.write("""Upload File: <input type="file" name="file"><br> <input type="submit"
        name="submit" value="Submit"> </form></body></html>""")

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        self.redirect('/serve/%s' % blob_info.key())

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)

app = webapp2.WSGIApplication([
    ('/?', FrontHand),
    ('/levels/?', LevelsHand),
    ('/levels/([^/]+)?', LevelsIdHand),
    ('/gameaccounts/login/?', GameLoginHand),
    ('/gameaccounts/register/?', GameRegisterHand),
    ('/characters/([^/]+)?', CharactersHand),
    ('/machines/?', MachineHand),
    ('/dsconn', DSConnHand),
    ('/uploadtest', UploadTestHand),
    ('/blobstore', BlobstoreTest),
    ('/upload', UploadHandler),
    ('/serve/([^/]+)?', ServeHandler)
], debug=True)
