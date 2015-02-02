#!/usr/bin/env python
import datetime
import webapp2

from google.appengine.ext import db
from google.appengine.api import users

class Level(db.Model):
	uid = db.IntegerProperty(required = True)
	level_name = db.StringProperty(required = True)
	live_level_data = db.TextProperty()
	draft_level_data = db.TextProperty()
	created = db.DateTimeProperty(auto_now_add = True)
	modified = db.DateTimeProperty(auto_now_add = True)

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
		self.write('<html><head><title>ARTF API</title></head><body>ARTF API 0.0.2</body></html>')

class LevelULHand(MainHand):
	def post(self):
		uid_str = self.request.get('user_id')
		level_name = self.request.get('level_name')
		live_level_data = self.request.get('live_level_data')
		draft_level_data = self.request.get('draft_level_data')
		
		uid = int(uid_str) #need to check if non-int is input later
		
		if uid and level_name:
			new_level = Level(uid = uid, level_name = level_name, live_level_data = live_level_data, draft_level_data = draft_level_data)
			new_level.put()
			self.write(new_level.key().id())
		else:
			self.write('ERROR: Missing required properties: uid or level_name');

class LevelDLHand(MainHand):
	def get(self, resource):
		beginning_path_len = 12 #the length of the string '/api/levels/'
		total_path_len = len(self.request.path)
		lid = int(self.request.path[beginning_path_len:total_path_len])
		query = Level.get_by_id(lid)
		if(query == None):
			self.abort(404)
		else:
			self.write(query.live_level_data)

app = webapp2.WSGIApplication([
    ('/?', FrontHand),
    ('/api/levels/?', LevelULHand),
    ('/api/levels/([^/]+)?', LevelDLHand)
], debug=True)
