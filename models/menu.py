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
        (I(_class="fa fa-inbox fa-2x",
           _title="Notifications"),
         False,
         URL('default', 'notifications'), []),
        (I(_class="fa fa-users fa-2x",
           _title="Friend requests"),
         False,
         URL('user', 'friend_requests'), []),
        (I(_class="fa fa-tag fa-2x",
           _title="Search by tags"),
         False,
         URL('problems', 'tag'), []),
        (I(_class="fa fa-search fa-2x",
           _title="Search friends"),
         False,
         URL('default', 'search'), []),
        (I(_class="fa fa-filter fa-2x",
           _title="Filters"),
         False,
         URL('default', 'filters'), []),
        (I(_class="fa fa-plus-circle fa-2x",
           _title="Add Custom Friend"),
         False,
         URL('user', 'custom_friend'), []),
        (I(_class="fa fa-edit fa-2x",
           _title="Edit Custom Friend Details"),
         False,
         URL('user', 'edit_custom_friend_details'), []),
    ]

response.menu += [(I(_class="fa fa-bar-chart fa-2x",
                     _title="Leaderboard"),
                   False,
                   URL('default', 'leaderboard'), [])]

if "auth" in locals(): auth.wikimenu()
