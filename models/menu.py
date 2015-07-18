# -*- coding: utf-8 -*-

response.logo = A(B("StopStalk"), _class="navbar-brand",
                  _href=URL('default', 'index'),
                  _id="web2py-logo")
response.title = request.application.replace('_',' ').title()
response.subtitle = ''

response.meta.author = 'Raj Patel raj454raj@gmail.com'
response.meta.description = 'Stop Stalk'
response.meta.keywords = 'stopstalk, raj454raj'
response.meta.generator = ''

response.google_analytics_id = None

response.menu = [
    (T('Home'), False, URL('default', 'index'), []),
    (T('Notifications'), False, URL('user', 'notifications'), []),
    (T('Friend Requests'), False, URL('user', 'friend_requests'), []),
    (T('Search'), False, URL('default', 'search'), []),
]

if "auth" in locals(): auth.wikimenu() 
