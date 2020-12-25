(function($) {
    "use strict";

    /* Handle the case of single digit in a time stamp */
    function formatTimeStamp(num) {
        var strnum = num.toString();

        return strnum.length == 1 ? '0' + strnum : strnum;
    }

    /* Add minutes to a js date object */
    function addMinutes(date, minutes) {
        return new Date(date.getTime() + minutes * 60000);
    }

    /* Get time duration in minutes */
    function getMinutes(duration) {
        var minutes = 0;

        duration = duration.split(' ');
        $.each(duration, function(key, val) {
            if (val[val.length - 1] == 'd')
                minutes += parseInt(val.replace('d', '')) * 24 * 60;
            else if (val[val.length - 1] == 'h')
                minutes += parseInt(val.replace('h', '')) * 60;
            else if (val[val.length - 1] == 'm')
                minutes += parseInt(val.replace('m', ''));
        });
        return minutes;
    }

    function dateToTimeStamp(d) {
        return [d.getFullYear(), d.getMonth() + 1, d.getDate()].map(formatTimeStamp).join('-') +
            'T' +
            [d.getHours(), d.getMinutes(), d.getSeconds()].map(formatTimeStamp).join(':') +
            '+05:30';
    }

    /* Authorize Google Calendar user */
    function handleAuthorize(callback, showDialog) {

        var SCOPES = ['https://www.googleapis.com/auth/calendar'];

        /* Check if current user has authorized this application. */
        function checkAuth() {
            if (gapi && gapi.auth) {
                gapi.auth.authorize({
                    'client_id': CLIENT_ID,
                    'scope': SCOPES.join(' '),
                    'immediate': true
                }, handleAuthResult);
            } else {
                /* If gapi library was still loading, try again after 5 sec */
                window.setTimeout(checkAuth, 5000);
            }
        }

        /**
         * Handle response from authorization server.
         *
         * @param {Object} authResult Authorization result.
         */
        function handleAuthResult(authResult) {
            if (authResult && !authResult.error) {
                // Hide auth UI, then load client library.
                loadCalendarApi();
            }
            /* If the failed request was not immediate */
            else if (authResult['error'] != "immediate_failed") {
                $.web2py.flash("Error Authorizing to Google Calendar!");
            }
        }

        /**
         * Initiate auth flow in response to user clicking authorize button.
         *
         * @param {Event} event Button click event.
         */
        function handleAuthClick() {
            gapi.auth.authorize({
                client_id: CLIENT_ID,
                scope: SCOPES,
                immediate: false
            }, handleAuthResult);
            return false;
        }

        /**
         * Load Google Calendar client library. List upcoming events
         * once client library is loaded.
         */
        function loadCalendarApi() {
            gapi.client.load('calendar', 'v3', callback);
        }

        if (showDialog) {
            handleAuthClick();
        } else {
            checkAuth();
        }
    }

    /* Run the decrement counter for a running contest */
    function runCounter(thisElement) {
        var lastDiff = null;

        function updateTime(thisElement) {
            var diff = lastDiff;
            if (lastDiff === null) {
                var now = new Date();
                var kickoff = Date.parse(thisElement.html());
                diff = kickoff - now;
            } else
                diff = diff - 1000;

            lastDiff = diff;

            var days = Math.floor(diff / (1000 * 60 * 60 * 24));
            var hours = Math.floor(diff / (1000 * 60 * 60));
            var mins = Math.floor(diff / (1000 * 60));
            var secs = Math.floor(diff / 1000);

            var dd = days;
            var hh = hours - days * 24;
            var mm = mins - hours * 60;
            var ss = secs - mins * 60;

            if (dd < 0 || hh < 0 || mm < 0 || ss < 0) {
                // One of the contest has ended
                thisElement.html("Contest has Ended!");
                return diff;
            }

            var timeStamp = [dd, hh, mm, ss];
            thisElement.html(timeStamp.map(formatTimeStamp).join(':'));
            return diff;
        }

        // Call it once instead of waiting for 1 second
        updateTime(thisElement);
        setInterval(updateTime, 1000, thisElement);
    }

    /* Log Contest for analytics */
    function logContest(contestName, siteName, contestLink, loggingType) {
        var data = {
            "contest_name": contestName,
            "site_name": siteName,
            "contest_link": contestLink,
            "logging_type": loggingType
        };

        $.ajax({
            url: '/default/log_contest',
            method: 'POST',
            data: data
        });
    }

    /* Check contests using link and data/time */
    function checkMarkedContests() {
        $('#contests-table').find('> tbody > tr')
            /* only ongoing contests*/
            .filter(function(index, element) {
                return this.children.length === 6 && $('.stopstalk-timestamp', this).length === 1;
            })
            /* refer to https://developers.google.com/google-apps/calendar/v3/reference/events/list
             * for more info about constructing listing request
             */
            .each(function() {

                var contestName = this.children[0].textContent;
                var siteName = this.children[1].children[0].title;
                var startTime = this.children[2].textContent;
                // Note this will always be duration and not endtime
                var duration = this.children[3].textContent;
                var contestLink = this.children[4].firstChild.href;
                var calendarButton = $('.set-reminder', this);
                var calendarIcon = $('.set-reminder > i', this);

                var startTimeStamp = new Date(startTime.replace(/-/g, '/'));
                var endTimeStamp = dateToTimeStamp(addMinutes(startTimeStamp, getMinutes(duration)));
                startTimeStamp = dateToTimeStamp(startTimeStamp);

                var request = gapi.client.calendar.events.list({
                    'calendarId': 'primary',
                    'maxResults': 20,
                    'singleEvents': 'true',
                    'orderBy': 'startTime',
                    'q': contestLink,
                    'timeMin': startTimeStamp,
                    'timeMax': endTimeStamp
                });
                /* check contest existence */
                request.execute(function(resp) {
                    var events = resp.items;
                    calendarButton.removeClass('disabled');
                    calendarIcon.removeClass('fa-check').addClass('fa-calendar-plus-o');
                    calendarButton.attr('data-tooltip', 'Set Reminder to Google Calendar');
                    $.each(events, function(index, element) {
                        if (this.summary === 'Contest at ' + siteName && this.location === contestLink) {
                            calendarIcon.removeClass('fa-calendar-plus-o').addClass('fa-check');
                            calendarButton.addClass('disabled');
                            calendarButton.attr('data-tooltip', 'Already set!');
                            return false;
                        }
                    });
                });
            });
    }

    /* Set Reminder in Google Calendar */
    function setReminder(contestName, siteName, startTime, duration, contestLink) {

        var startTimeStamp = new Date(startTime.replace(/-/g, '/'));
        var endTimeStamp = dateToTimeStamp(addMinutes(startTimeStamp, getMinutes(duration)));
        startTimeStamp = dateToTimeStamp(startTimeStamp);

        /**
         * Print the summary and start datetime/date of the next ten events in
         * the authorized user's calendar. If no events are found an
         * appropriate message is printed.
         */
        function addEventToCalendar() {
            // Refer to the JavaScript quickstart on how to setup the environment:
            // https://developers.google.com/google-apps/calendar/quickstart/js
            // Change the scope to 'https://www.googleapis.com/auth/calendar' and delete any
            // stored credentials.
            var event = {
                'summary': 'Contest at ' + siteName,
                'location': contestLink,
                'description': 'Contest name: ' + contestName + ' at ' + siteName + '\nContest Link: ' + contestLink + '\nGet involved more into Competitive programming by registering here: https://www.stopstalk.com/\nFor more contests visit https://www.stopstalk.com/contests/',
                'start': {
                    'dateTime': startTimeStamp,
                    'timeZone': 'Asia/Kolkata'
                },
                'end': {
                    'dateTime': endTimeStamp,
                    'timeZone': 'Asia/Kolkata'
                },
                'reminders': {
                    'useDefault': false,
                    'overrides': [{
                        'method': 'email',
                        'minutes': 30
                    }, ]
                }
            };

            var request = gapi.client.calendar.events.insert({
                'calendarId': 'primary',
                'resource': event
            });

            request.execute(function(event) {
                $.web2py.flash("Reminder added!");
                checkMarkedContests();
            });
        }

        /* Call Auth for Google Calendar */
        handleAuthorize(addEventToCalendar, true);
    }

    $(document).ready(function() {
        /* On document load */

        /* Call runCounter for each contest */
        $('.contest-end-time').each(function() {
            runCounter($(this));
        });

        $(document).on('click', '.set-reminder:not(.disabled)', function() {
            var children = this.parentElement.parentElement.children,
                contestName = children[0].textContent,
                siteName = children[1].children[0].title,
                startTime = children[2].textContent,
                duration = children[3].textContent, // Note this will always be duration and not endtime
                contestLink = children[4].firstChild.href;

            setReminder(contestName, siteName, startTime, duration, contestLink);
            logContest(contestName, siteName, contestLink, "Reminder");
        });

        $('.view-contest').click(function() {
            var children = this.parentElement.parentElement.children,
                contestName = children[0].textContent,
                siteName = children[1].children[0].title,
                contestLink = children[4].firstChild.href;

            logContest(contestName, siteName, contestLink, "View");
        });

        /* Call Auth for Google Calendar to refresh marked contests */
        handleAuthorize(checkMarkedContests, false);
    });
})(jQuery);
