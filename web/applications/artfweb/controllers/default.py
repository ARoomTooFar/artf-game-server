# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################

#from google.appengine.ext import db
#from google.appengine.ext.db import GqlQuery
#db = GQLDB()
import logging
import random

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Welcome to web2py!")

    if auth.user:
        msg = A('Workshop', _class='btn', _href=URL('default', 'workshop'))
    else:
        msg = "Please login or register to edit your level!";

    return dict(inWorkshop=False)

def media():
    return dict(display_title= 'Media')

def locations():
    return dict(display_title= 'Locations')

def blog():
    #form = SQLFORM(db.blog)
    #form.add_button('Add', URL('add'))
    posts = db().select(db.blog.ALL, orderby = ~db.blog.date_posted)

    #return  dict(form=form)
    return dict(posts=posts)

@auth.requires_login()
def add():
    #form = SQLFORM(db.blog)
    form = SQLFORM.factory(
        Field('post_title', 'string', requires=IS_NOT_EMPTY(error_message='Field is empty !'), label='Title'),
        Field('authour', 'string', requires=IS_NOT_EMPTY(error_message='Field is empty !'), label='Authour'),
        Field('date_posted', 'datetime', label='Date Posted'),
        Field('postbody', 'text', requires=IS_NOT_EMPTY(error_message='Field is empty !'), label='Body')
    )

    if form.process().accepted:
        db.blog.insert(**form.vars)
        response.flash = T('Announcement posted')
        redirect(URL('default','blog'))

    return dict(form=form)

def view():
    p = db.blog(request.args(0)) or redirect(URL('default', 'index'))
    form = SQLFORM(db.blog,readonly=True)
    return dict(form=form)


def dbtest():
    q = db().select(db.Level.ALL)
    #levels = db.GqlQuery("SELECT * FROM Level ORDER BY created DESC")
    #personresults = db(Level).select(db.Level.level_name)

    return dict(display_title='DB Test', q=q)

def dbinput():
    form = SQLFORM(db.Level)

    if form.process().accepted:
        session.flash = T('Level added')
        redirect(URL('default', 'dbinput'))

    return dict(display_title='DB Input', form=form)

@auth.requires_login()
def workshop():
    # returns parsed data from level data. index 0 is level name, index 1 is difficulty.
    def parseLevelData(levelData):
        parsedData = []

        if levelData == 'farts':
            parsedData.append('Untitled Zone')
            parsedData.append('0')
        else:
            firstLine = levelData.split('\n')[0]
            parsedData = firstLine.split('\t')
            parsedData[0] = parsedData[0][5:]
            if parsedData[0] == '':
                parsedData[0] = 'Untitled Zone'

        return parsedData

    btnLevels = None
    btnAddLevel = None
    levelsList = None
    form = None
    ids = '0'
    levelData = None

    # /workshop
    if request.args(0) is None:
        redirect(URL('default', 'workshop', args=['zones']))
    
    elif request.args(0) == 'zones':

        # /workshop/zones/[LEVELID]/webgl
        if str(request.args(1)).isdigit() and request.args(2) == 'webgl':
            ids = str(auth.user.game_acct_id) + ',' + request.args(1)

            # get level data for debugging purposes
            entity = db(db.Level.id == request.args(1)).select().first()
            levelData = entity.live_level_data

            response.view = request.controller + '/zoneeditor-webgl.html'
            return dict(ids=ids, levelData=levelData)

        # /workshop/zones/[LEVELID]/del
        if str(request.args(1)).isdigit() and request.args(2) == 'del':
            page_title = 'Delete Zone'

            btnLevels = A('Your Zones', _class='btn', _href=URL('default', 'workshop', args=['zones']))
            form = FORM.confirm('Are you sure you want to delete your level?')

            if form.accepted:
                db(db.Level.id == request.args(1)).delete()
                session.flash = T('Level ' + str(request.args(1)) + ' deleted')
                redirect(URL('default', 'workshop', args=['zones']))

        # /workshop/zones/[LEVELID]
        # need to add in security here later so people can't edit other people's levels
        elif str(request.args(1)).isdigit():
            ids = str(auth.user.game_acct_id) + ',' + request.args(1)

            # get level data for debugging purposes
            entity = db(db.Level.id == request.args(1)).select().first()
            levelData = entity.live_level_data
            parsedData = parseLevelData(entity.live_level_data)

            response.view = request.controller + '/zoneeditor.html'
            return dict(ids=ids, levelData=levelData, levelName = parsedData[0], difficulty = parsedData[1])

        # /workshop/zones/add
        elif request.args(1) == 'add':
            response.view = request.controller + '/zoneadd.html'
            page_title = 'Create Zone'

            form = FORM.confirm('Do you want to create a new level?')

            if form.accepted:
                levelId = db.Level.insert(live_level_data='farts', draft_level_data='farts', difficulty='0', game_acct_id=auth.user.game_acct_id, mach_id=123)
                session.flash = T('New level ' + str(levelId) + ' created!')
                redirect(URL('default', 'workshop', args=['zones']))

            return dict(form=form)

        # /workshop/zones
        else:
            response.view = request.controller + '/zonelist.html'
            page_title = 'Your Zones'

            query = db(db.Level.game_acct_id == auth.user.game_acct_id).select()

            levelsList = []

            for entity in query:
                parsedData = parseLevelData(entity.live_level_data)
                levelsList.append({'id': entity.id, 'live_level_data': entity.live_level_data, 'level_name': parsedData[0], 'difficulty': parsedData[1]})

            return dict(levelsList=levelsList)

    return dict()

def test():
    return dict()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """

    if 'register' in request.args:
        field_game_acct_id = db.auth_user['game_acct_id']
        field_game_acct_id.readable = False
        field_game_acct_id.writable = False

    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

def api():
    # returns parsed data from level data. index 0 is level name, index 1 is difficulty.
    def parseLevelData(levelData):
        parsedData = []

        if levelData == 'farts':
            parsedData.append('Untitled Zone')
            parsedData.append('0')
        else:
            firstLine = levelData.split('\n')[0]
            parsedData = firstLine.split('\t')
            parsedData[0] = parsedData[0][5:]
            if parsedData[0] == '':
                parsedData[0] = 'Untitled Zone'

        return parsedData

    data = 'error'

    # /api/levels
    if request.args(0) == 'levels':
        if request.args(1) != None and request.args(1).isdigit():
            level_id = request.args(1)

            # download level (/api/levels/[LEVELID])
            if(request.env.request_method == 'GET'):
                entity = db(db.Level.id == level_id).select().first()

                # if the level exists in the data store, print its data
                if entity is not None:
                    data = XML(entity.live_level_data)
                    logging.info('Level ' + level_id  + ' downloaded')
                else:
                    logging.error('Level download failed. Level ' + level_id + ' does not exist in Datastore.')

            # update level (/api/levels/[LEVELID])
            elif(request.env.request_method == 'POST'):
                entity = db(db.Level.id == level_id).select().first()

                # if the level exists in the data store, update its data
                if entity is not None:
                    entity.update_record(draft_level_data = request.post_vars['draft_level_data'], game_acct_id = request.post_vars['game_acct_id'], live_level_data = request.post_vars['live_level_data'], modified = datetime.utcnow())
                    data = request.post_vars['live_level_data']
                    logging.info('Level ' + level_id + ' updated')
                else:
                    logging.error('Level manipulation failed. No manipulation flag set.')

    # /api/gameaccounts
    elif request.args(0) == 'gameaccts':
        if (request.env.request_method == 'POST'):
            
            # register (/api/gameaccts/register)
            if request.args(1) == 'register':
                # register handling goes here
                input_game_acct_name = request.post_vars['game_acct_name']
                input_game_acct_password = request.post_vars['game_acct_password']

                entity = db(db.GameAccount.game_acct_name == input_game_acct_name).select().first()

                # if game_acct_name doesn't exist already
                if entity is None:
                    # create game_acct
                    new_game_acct_id = db.GameAccount.insert(game_acct_name = input_game_acct_name, game_acct_password = input_game_acct_password)

                    # create character linked to game_acct
                    new_char_id = db.Character.insert(char_data = str(new_game_acct_id) + ",123,0,0,9001,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1", game_acct_id = new_game_acct_id)

                    #game_acct_id = str(game_acct_id)  # must be cast to str for logging
                    data = new_game_acct_id
                    logging.info('Game account ' + str(new_game_acct_id) + ' created')
                else:
                    logging.info('Registration failed for ' + input_game_acct_name + '. game_acct_name already exists.')

            # login (/api/gameaccts/login)
            elif request.args(1) == 'login':
                input_game_acct_name = request.post_vars['game_acct_name']
                input_game_acct_pass = request.post_vars['game_acct_password']

                entity = db(db.GameAccount.game_acct_name == input_game_acct_name).select().first()
                
                # continue if game_acct_name exists
                if entity is not None:
                    game_acct_id = entity.id

                    # send char_data if game_acct_name and game_acct_pass are correct
                    if entity.game_acct_password == input_game_acct_pass:
                        entity = db(db.Character.game_acct_id == game_acct_id).select().first()
                        data = entity.char_data
                        logging.info('Game account ' + input_game_acct_name + ' logged in')
                    # send error if game_acct_name or game_acct_pass are incorrect
                    else:
                        logging.info('Login failed for game account ' + input_game_acct_name + '. Password incorrect.')
                
                # send error if game_acct_name doesn't exist
                else:
                    logging.info('Login failed for game account ' + input_game_acct_name + '. game_acct_name doesn\'t exist.')

    # /api/matchmake
    elif request.args(0) == 'matchmake':
        levelListLen = 10

        # get levels for difficulty (/api/matchmake/[DIFFICULTYVAL])
        if request.args(1) != None and request.args(1).isdigit():
            difficulty = int(request.args(1))
            difficultyCeil = difficulty + 1
            query = (db.Level.difficulty >= difficulty) & (db.Level.difficulty < difficultyCeil)
            entities = db(query).select().sort(lambda row: random.random())[0:levelListLen]

            if entities is not None:
                data = ''

                for entity in entities:
                    level_id = entity.id

                    data += str(level_id) # append level id

                    if entity != entities[-1]:
                        data += ','

                if data == '':
                    data = 'error'
                    logging.info('Matchmaking for difficulty ' + str(difficulty)  + ' executed, but no levels exist in this difficulty range')
                else:
                    logging.info('Matchmaking for difficulty ' + str(difficulty)  + ' successfully executed')

        # get levels at random (/api/matchmake/rand)
        elif request.args(1) == 'rand':
            entities = db().select(db.Level.ALL).sort(lambda row: random.random())[0:levelListLen]

            if entities is not None:
                data = ''

                for entity in entities:
                    level_id = str(entity.id)
                    levelEntity = db(db.Level.id == level_id).select().first()
                    level_data = levelEntity.live_level_data
                    parsed_level_data = parseLevelData(level_data)
                    level_name = parsed_level_data[0]
                    level_difficulty = parsed_level_data[1]
                    if levelEntity.game_acct_id is None:
                        level_owner_name = 'Nosmik'
                    else:
                        level_owner_id = levelEntity.game_acct_id
                        gameAcctEntity = db(db.GameAccount.id == level_owner_id).select().first()
                        if gameAcctEntity is None:
                            level_owner_name = 'Nosmik'
                        else:
                            level_owner_name = gameAcctEntity.game_acct_name

                    data = data + level_id + '|' + level_name + '|' + level_owner_name + '|' + level_difficulty

                    if entity != entities[-1]:
                        data += ','

                    if data == '':
                        data = 'error'
                        logging.info('Matchmaking for random executed, but no levels exist in this difficulty range')
                    else:
                        logging.info('Matchmaking for random successfully executed')

    return dict(data=data)

"""@auth.requires_login() 
def api():

    #this is example of API with access control
    #WEB2PY provides Hypermedia API (Collection+JSON) Experimental

    from gluon.contrib.hypermedia import Collection
    rules = {
        'blog': {
        'GET':{'query':None,'fields':['id', 'authour']},
        'POST':{},'PUT':{},'DELETE':{}},
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}}
        }
    return Collection(db).process(request,response,rules)"""
