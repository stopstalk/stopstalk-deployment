(function($) {
    "use strict";

    // Load the Visualization API and the piechart package.
    google.load('visualization', '1.1', {'packages': ['corechart', 'calendar']});
    // Set a callback to run when the Google Visualization API is loaded.
    google.setOnLoadCallback(drawChart);
    google.setOnLoadCallback(drawCalendar);

    // ---------------------------------------------------------------------------------
    function goToByScroll(id) {
        $('html, body').animate({scrollTop: $("#" + id).offset().top}, 'slow');
    }

    // ---------------------------------------------------------------------------------
    function createCustomHTML(currDate, currVal) {
        var withoutCount = Object.assign({}, currVal);
        delete withoutCount["count"];
        var customHTML = "<div style='min-width: 180px;'><h6>" +
                         currDate +
                         "</h6><div style='padding-right: 5px; display: inline;'>";
        $.each(withoutCount, function(status, count) {
            customHTML += "<div class='chip'><img src='/static/images/" +
                          status + "-icon.jpg'></img>" +
                          count + "</div> ";
        });
        customHTML += "<div></div></div></div>";
        return customHTML;
    }

    // ---------------------------------------------------------------------------------
    function computeCellValue(val) {
        if(onlyGreen) {
            return val.count;
        }
        var accepted = val.AC, partiallyAccepted = val.PS;
        if(accepted === undefined) accepted = 0;
        if(partiallyAccepted === undefined) partiallyAccepted = 0;
        // Math = Accepted - Not Accepted
        //      = (accepted + partiallyAccepted) - [total - (accepted + partiallyAccepted)]
        return 2 * (accepted + partiallyAccepted) - val.count;
    }

    // ---------------------------------------------------------------------------------
    function selectHandler(calendarChart) {
        var selection = calendarChart.getSelection();
        var milliseconds = selection[0]["date"];
        if (milliseconds) {
            var dateObj = new Date(milliseconds);
            var yyyy = dateObj.getFullYear().toString();
            var mm = (dateObj.getMonth() + 1).toString(); // getMonth() is zero-based
            var dd  = dateObj.getDate().toString();
            var finalDate = yyyy + '-' + (mm[1] ? mm : '0'+ mm[0]) +
                            '-' + (dd[1] ? dd : '0' + dd[0]);
            $.ajax({
                url: getActivityURL,
                data: {date: finalDate, user_id: userRowID, custom: custom},
                method: 'POST'
            }).done(function(response) {
                $("#activity").html(response["table"]);
                $(".tooltipped").tooltip({});
                goToByScroll("activity");
            });
        }
    }

    // ---------------------------------------------------------------------------------
    function drawCalendarFromData(calendarChart, allData) {
        var dataTable = new google.visualization.DataTable(), dateList = [], dt;
        dataTable.addColumn({ type: 'date', id: 'Date' });
        dataTable.addColumn({ type: 'number', id: 'Number' });
        dataTable.addColumn({ type: 'string', role: 'tooltip', 'p': {'html': true} });
        $.each(allData, function(key, val) {
            dt = key.split('-');
            dateList.push([new Date(dt[0], --dt[1], dt[2]),
                           computeCellValue(val),
                           createCustomHTML(key, val)]);
        });
        dataTable.addRows(dateList);
        var colorAxisOption,
            graphTitle,
            onlyGreenAxis = {minValue: 1,
                             colors: ['#dae7ab', '#d6e685', '#8cc665', '#44a340', '#005200', '#001A00'],
                             values: [0, 4, 8, 12, 16, 20]},
            greenRedAxis = {colors: ['#CA1717', '#FFFFFF', '#27CE05'],
                            values: [-5, 0, 5],
                            maxValue: 5,
                            minValue: -5},
            submissionTitle = "Submission Graph",
            acceptanceTitle = "Acceptance Graph";
        if (onlyGreen) {
            graphTitle = submissionTitle;
            colorAxisOption = onlyGreenAxis;
        } else {
            graphTitle = acceptanceTitle;
            colorAxisOption = greenRedAxis;
        }
        var options = {
            legend: 'none',
            tooltip: {isHtml: true},
            title: graphTitle,
            colorAxis: colorAxisOption,
            noDataPattern: {
                backgroundColor: '#eeeeee',
                color: '#eeeeee'
            },
            height: 750,
            calendar: {
                monthOutlineColor: {
                    stroke: '#ffffff',
                    strokeWidth: 2
                },
                unusedMonthOutlineColor: {
                    stroke: '#ffffff',
                    strokeWidth: 2
                },
                focusedCellColor: {
                    stroke: 'grey',
                    strokeOpacity: 0.8,
                    strokeWidth: 1
                }
            }
        };
        calendarChart.draw(dataTable, options);
        $('#toggle-submission-graph').on('click', function() {
            onlyGreen = !onlyGreen;
            if(onlyGreen) {
                graphTitle = submissionTitle;
                colorAxisOption = onlyGreenAxis;
            }
            else {
                graphTitle = acceptanceTitle;
                colorAxisOption = greenRedAxis;
            }
            options["colorAxis"] = colorAxisOption;
            options["title"] = graphTitle;
            var dataTable = new google.visualization.DataTable(), dateList = [], dt;
            dataTable.addColumn({ type: 'date', id: 'Date' });
            dataTable.addColumn({ type: 'number', id: 'Number' });
            dataTable.addColumn({ type: 'string', role: 'tooltip', 'p': {'html': true} });
            $.each(allData, function(key, val) {
                dt = key.split('-');
                dateList.push([new Date(dt[0], --dt[1], dt[2]),
                               computeCellValue(val),
                               createCustomHTML(key, val)]);
            });
            dataTable.addRows(dateList);
            calendarChart.draw(dataTable, options);
        });
    }

    // ---------------------------------------------------------------------------------
    function drawCalendar() {
        var calendarChart = new google.visualization.Calendar(document.getElementById('calendar_submission'));
        google.visualization.events.addListener(calendarChart, 'select', function () {
            selectHandler(calendarChart);
        });
        $.ajax({
            method: 'GET',
            url: getDatesURL,
            data: {user_id: userRowID,
                   custom: custom}
        }).done(function(total) {
            // Update html for the streaks
            $('#max-streak').html(total['max_streak']);
            $('#curr-streak').html(total['curr_streak']);
            $('#max-accepted-streak').html(total['max_accepted_streak']);
            $('#curr-accepted-streak').html(total['curr_accepted_streak']);
            drawCalendarFromData(calendarChart, total['total']);
        });
    }

    // Callback that creates and polates a data table,
    // instantiates the pie chart, passes in the data and
    // draws it.

    // ---------------------------------------------------------------------------------
    function drawChart() {
        var numJSON = {'AC': 0,
                       'WA': 0,
                       'TLE': 0,
                       'MLE': 0,
                       'CE': 0,
                       'RE': 0,
                       'SK': 0,
                       'PS': 0,
                       'HCK': 0,
                       'OTH': 0
                       };
        $.ajax({
            method: 'GET',
            url: getStatsURL,
            data: {user_id: userRowID, custom: custom}
        }).done(function(data) {

            var statuses = data['row'];
            $.each(statuses, function(i) {
                numJSON[statuses[i]['submission']['status']] = statuses[i]['_extra']['COUNT(submission.id)'];
            });
            // Create the data table.
            var data = new google.visualization.DataTable();
            data.addColumn('string', 'resultType');
            data.addColumn('number', 'numberOfSubmissions');
            data.addRows([
                ['Accepted', numJSON['AC']],
                ['Partially Solved', numJSON['PS']],
                ['Wrong Answer', numJSON['WA']],
                ['Time Limit Exceeded', numJSON['TLE']],
                ['Memory Limit Exceeded', numJSON['MLE']],
                ['Runtime Error', numJSON['RE']],
                ['Compile Error', numJSON['CE']],
                ['Hacked', numJSON['HCK']],
                ['Skipped', numJSON['SK']],
                ['Others', numJSON['OTH']]
            ]);
            // Set chart options
            var options = {'title':'Total Submissions',
                           'width':600,
                           'height':500,
                           'pieHole': 0.5,
                           'slices': {0: {color: '#4CAF50'},
                                      1: {color: '#8BC34A'},
                                      2: {color: '#F44336'},
                                      3: {color: '#3F51B5'},
                                      4: {color: '#03A9F4'},
                                      5: {color: '#9C27B0'},
                                      6: {color: '#FF9800'},
                                      7: {color: '#795548'},
                                      8: {color: '#FFEB3B'},
                                      9: {color: '#9E9E9E'}},
                           'pieResidueSliceLabel': '',
                           'pieResidueSliceColor': 'transparent'
                           };
            // Instantiate and draw our chart, passing in some options.
            var chart = new google.visualization.PieChart(document.getElementById('chart_div'));
            chart.draw(data, options);
        });
    }

    $(document).ready(function() {

        /* Get the details about the solved/unsolved problems */
        $.ajax({
            url: getSolvedCountsURL,
            method: "GET",
            data: {user_id: userID,
                   custom: custom},
            success: function(response) {
                $('#solved-problems').html(response['solved_problems']);
                $('#total-problems').html(response['total_problems']);
            },
            error: function(response) {
                $.web2py.flash('Error getting solved problems');
            }
        });

        $('.modal-trigger').leanModal();

        /* Color the handles accordingly */
        $.ajax({
            url: handleDetailsURL,
            data: {handle: handle}
        }).done(function(response) {
            var mapping = {"invalid-handle": "Invalid handle",
                           "pending-retrieval": "Pending retrieval",
                           "not-provided": "Not provided"};

            $.each(response, function(key, val) {
                var $siteChip = $('#' + key + '_chip');
                $siteChip.addClass(val);
                $siteChip.parent().attr("data-tooltip", mapping[val]);
            });
        });

        $('.friends-button').click(function() {
            var thisButton = $(this),
                userID = thisButton.attr('data-user-id'),
                buttonType = thisButton.attr('data-type'),
                child = $(thisButton.children()[0]);

            if (buttonType == 'add-friend') {
                if (isLoggedIn === 'True') {
                    thisButton.removeClass('green');
                    thisButton.addClass('black');
                    thisButton.attr('data-type', 'unfriend');
                    thisButton.attr('data-tooltip', 'Unfriend');
                    child.removeClass('fa-user-plus');
                    child.addClass('fa-user-times');

                    $.ajax({
                        method: 'POST',
                        url: '/default/mark_friend/' + userID
                    }).done(function(response) {
                        $.web2py.flash(response);
                    }).error(function(httpObj, textStatus) {
                        thisButton.removeClass('black');
                        thisButton.addClass('green');
                        thisButton.attr('data-type', 'add-friend');
                        thisButton.attr('data-tooltip', 'Add friend');
                        $.web2py.flash("[" + httpObj.status + "]: Unexpected error occurred");
                    });
                } else {
                    $.web2py.flash("Login to add friend");
                }
            } else if (buttonType == 'unfriend') {
                thisButton.removeClass('black');
                thisButton.addClass('green');
                thisButton.attr('data-type', 'add-friend');
                thisButton.attr('data-tooltip', 'Add friend');
                child.removeClass('fa-user-times');
                child.addClass('fa-user-plus');

                $.ajax({
                    method: 'POST',
                    url: '/default/unfriend/' + userID
                }).done(function(response) {
                    child.removeClass('fa-user-times');
                    child.addClass('fa-user-plus');
                    $.web2py.flash(response);
                }).error(function(httpObj, textStatus) {
                    $.web2py.flash("[" + httpObj.status + "]: Unexpected error occurred");
                    $.web2py.flash("Unexpected error occurred");
                });
            }
        });
    });
})(jQuery);