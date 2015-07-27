# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

## app configuration made easy. Look inside private/appconfig.ini
from gluon.contrib.appconfig import AppConfig
## once in production, remove reload=True to gain full speed
myconf = AppConfig(reload=True)

import custom_layout as custom

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
#    db = DAL('mysql://' + current.mysql_user + \
#             ':' + current.mysql_password + \
#             '@' + current.mysql_server + \
#             '/' + current.mysql_dbname)
    db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*']
## choose a style for forms
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')


## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

## create all tables needed by auth if not custom tables
auth.settings.extra_fields['auth_user']= [Field('institute', requires=IS_NOT_EMPTY()),
                                          Field('codechef_handle'),
                                          Field('codeforces_handle'),
                                          Field('spoj_handle'),
                                          Field('stopstalk_handle',
                                                requires=[IS_NOT_IN_DB(db,
                                                                      'auth_user.stopstalk_handle',
                                                                      error_message=T("Handle taken")),
                                                          IS_NOT_IN_DB(db,
                                                                       'custom_friend.stopstalk_handle',
                                                                       error_message=T("Handle taken"))]
                                                ),
                                          Field('rating',
                                                default=0)
                                          ]

auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = current.smtp_server
mail.settings.sender = current.sender_mail
mail.settings.login = current.sender_mail + ":" + current.sender_password

## configure auth policy
auth.settings.registration_requires_verification = True
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

db.define_table("custom_friend",
                Field("user_id", "reference auth_user"),
                Field("first_name", requires=IS_NOT_EMPTY()),
                Field("last_name", requires=IS_NOT_EMPTY()),
                Field("institute", requires=IS_NOT_EMPTY()),
                Field("stopstalk_handle", requires = [IS_NOT_IN_DB(db,
                                                                   'auth_user.stopstalk_handle',
                                                                   error_message=T("Handle already exists")),
                                                      IS_NOT_IN_DB(db,
                                                                   'custom_friend.stopstalk_handle',
                                                                   error_message=T("Handle already exists"))]),
                Field("codechef_handle"),
                Field("spoj_handle"),
                Field("codeforces_handle"),
                Field('rating',
                      default=0)
                )

db.define_table("submission",
                Field("user_id", "reference auth_user"),
                Field("custom_user_id", "reference custom_friend"),
                Field("stopstalk_handle"),
                Field("site_handle"),
                Field("site"),
                Field("time_stamp", "datetime"),
                Field("problem_name"),
                Field("problem_link"),
                Field("lang"),
                Field("status"),
                Field("points"),
                )

db.define_table("friend_requests",
                Field("from_h", "reference auth_user"),
                Field("to_h", "reference auth_user"),
                )

db.define_table("friends",
                Field("user_id", "reference auth_user"),
                Field("friends_list", "text"))

current.db = db
