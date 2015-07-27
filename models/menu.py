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

if session.user_id:
    response.menu = [
        (T('Notifications'), False, URL('user', 'notifications'), []),
        (T('Friend Requests'), False, URL('user', 'friend_requests'), []),
        (T('Find friends'), False, URL('default', 'search'), []),
        (T('Make custom friend'), False, URL('user', 'custom_friend'), []),
    ]

response.menu += [(T('Leaderboard'), False, URL('default', 'leaderboard'), [])]

if "auth" in locals(): auth.wikimenu() 
