(function($) {
    "use strict";

    // Load the Visualization API and the piechart package.
    google.load('visualization', '1.1', {'packages': ['corechart', 'calendar'],
                                         'callback': drawCharts});

    function drawCharts() {
        // Set a callback to run when the Google Visualization API is loaded.
        drawPieChart();
        drawCalendar();
        if (linechartAvailable === 'True') {
            drawLineChart();
        }
    }

    function drawLineChart() {

        function zeropad(num) {
            return num < 10 ? "0" + num : num.toString();
        }

        function urlToSite(url) {
            if (url.search("codechef.com") !== -1) {
                return "codechef";
            } else if (url.search("codeforces.com") !== -1) {
                return "codeforces";
            } else if (url.search("hackerrank.com") !== -1) {
                return "hackerrank";
            } else {
                $.web2py.flash("Some error occurred");
                return "";
            }
        }

        $.ajax({
            method: 'GET',
            url: getGraphDataURL,
            data: {user_id: userRowID, custom: custom}
        }).done(function(response) {
            var graph_data = response["graphs"];
            if (graph_data == 0) {
                $("#contest_graphs").html("<p>No graph data available at the moment !</p>")
                return;
            }
            var data = new google.visualization.DataTable();
            data.addColumn("date", "Day");
            var reformed_data = {}
            var noOfGraphs = Object.keys(graph_data).length;
            $.each(graph_data, function(k, v) {
                data.addColumn("number", v["title"]);
                $.each(v["data"], function(dateStr, contestData) {
                    dateStr = dateStr.split(" ")[0];
                    if (reformed_data.hasOwnProperty(dateStr)) {
                        reformed_data[dateStr][k] = [parseFloat(contestData["rating"]), contestData];
                    }
                    else {
                        var tmparray = [];
                        for(var i = 0 ; i < noOfGraphs ; i++) {
                            tmparray.push(null);
                        }
                        tmparray[k] = [parseFloat(contestData["rating"]), contestData];
                        reformed_data[dateStr] = tmparray;
                    }
                });
            });
            var completeGraphData = [];
            contestGraphData = jQuery.extend(true, {}, reformed_data);
            $.each(reformed_data, function(k, v) {
                $.each(v, function(i, contestDetails) {
                    if (contestDetails) {
                        v[i] = v[i][0];
                    }
                });
                v.unshift(new Date(k));
                completeGraphData.push(v);
            });
            completeGraphData.sort(function(a, b) {
                return a[0].getTime() - b[0].getTime();
            });
            data.addRows(completeGraphData);
            var options = {
              curveType: 'function',
              width: 900,
              height: 500,
              interpolateNulls: true,
              aggregationTarget: 'multiple',
              focusTarget: 'datum',
              tooltip: {
                  trigger: 'selection',
                  isHtml: true
              },
              pointSize: 4,
              explorer: {
                  keepInBounds: true,
                  maxZoomOut: 1.45,
                  maxZoomIn: 0.45,
              }
            };
            var chart = new google.visualization.LineChart(document.getElementById('cumulative_graph'));
            chart.draw(data, options);
            function lineChartSelectHandler(e) {
                if (typeof ga !== 'undefined') {
                    ga('send', {
                        hitType: 'event',
                        eventCategory: 'button',
                        eventAction: 'click',
                        eventLabel: 'Contest Graph data point'
                    });
                }
                var selection = chart.getSelection();
                if(selection.length === 0 || selection[0].row === null) return;
                var timeStamp = data.getValue(selection[0].row, 0);
                var dateStr = [timeStamp.getFullYear(),
                               zeropad(timeStamp.getMonth() + 1),
                               zeropad(timeStamp.getDate())].join("-");
                $("#contest-activity-date").html(dateStr);
                var tbodyHTML = "";
                $.each(contestGraphData[dateStr], function(ind, val) {
                    if (val) {
                        tbodyHTML += "<tr><td>" + val[1]["name"] + "</td><td><img src='/stopstalk/static/images/" + urlToSite(val[1]["url"]) + "_small.png' style=\"height: 30px; width: 30px;\"></img></td><td><a class='popup-contest-page btn-floating btn-small accent-4 green' href='" + val[1]["url"]+ "' target='_blank'><i class='fa fa-external-link-square fa-lg'></i></a></td><td>" + val[0] + "</td><td>" + val[1]["rank"] + "</td></tr>";
                    }
                });
                $('#participated-contests').html(tbodyHTML);
                $('#contest-activity-modal').modal({
                    complete: function() {
                        $('#participated-contests').html('');
                    }
                });
                $('#contest-activity-modal').modal('open');
            }
            google.visualization.events.addListener(chart, 'select', lineChartSelectHandler);
        });
    }

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
    function drawPieChart() {
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

    var handleRefreshNow = function() {
        if (!canUpdate) return;
        $(document).on('click', '#update-my-submissions', function() {
            var $button = $(this);
            $.ajax({
                url: refreshNowURL,
                method: 'POST',
                data: {stopstalk_handle: stopstalkHandle, custom: custom},
                success: function(response) {
                    canUpdate = false;
                    $button.addClass("disabled");
                    Materialize.toast("Your submissions will be updated in 5 minutes", 10000);
                },
                error: function(err) {
                    $.web2py.flash("Error submitting your request");
                    console.log(err);
                }
            });
        });
    };

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

        $('#stopstalk-handle').modal();
        $('#profile-add-to-my-custom-friend').click(function() {
            $('#stopstalk-handle').modal('open');
        });

        $('#custom-users-modal').modal();

        $('.custom-user-count-profile-page').click(function() {
            var $this = $(this);
            $('#custom-users-modal').modal('open');

            if ($('#custom-users-list').html() === '') {
                // Just one time AJAX call to populate the modal table
                $.ajax({
                    url: getCustomUserURL,
                    method: 'GET',
                    data: {'stopstalk_handle': $this.data('stopstalk-handle')},
                    success: function(response) {
                        $('#custom-users-list').html(response["content"]);
                    },
                    error: function(err) {
                        $.web2py.flash("Something went wrong");
                    }
                })
            }
        });

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

        handleRefreshNow();

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