(function($) {
    "use strict";

    var StopStalk = {userStats: {}};

    // ---------------------------------------------------------------------------------
    var getStopStalkUserStats = function() {
        return new Promise(function(resolve, reject) {
            $.ajax({
                method: 'GET',
                url: stopStalkStatsUrl,
                data: {user_id: userRowID, custom: custom}
            }).done(function(data) {
                resolve(data);
            });
        });
    };

    var populateSolvedCounts = function(data) {
        $.each(data, function(key, val) {
            $('#' + key.toLowerCase() + '-solved-count').html(val);
        });
    };

    var populateSiteAccuracy = function(data) {
        $.each(data, function(key, val) {
            $('#site-accuracy-' + key.toLowerCase()).html(val);
        });
    };

    function drawCharts() {
        // Set a callback to run when the Google Visualization API is loaded.
        if (linechartAvailable === 'True') {
            drawLineChart();
        }
        drawPieChart(StopStalk.userStats['status_percentages']);
        drawCalendar(StopStalk.userStats['calendar_data']);
        if (totalSubmissions !== '0' && isLoggedIn) {
            drawStopStalkRatingChart(StopStalk.userStats['rating_history']);
        }
    }

    function drawStopStalkRatingChart(ratingHistoryData) {
        var dataTable = new google.visualization.DataTable();
        var dataValues = [['Date', 'Current Streak', 'Maximum Streak', 'Solved', 'Accuracy', 'Attempted', 'Per-Day']];
        $.each(ratingHistoryData, function(key, val) {
            dataValues.push([
                new Date(val[0]),
                val[1][0],
                val[1][1],
                val[1][2],
                val[1][3],
                val[1][4],
                val[1][5]
            ]);
        });

        var options = {
            width: 1000,
            height: 500,
            legend: { position: 'right', maxLines: 3 },
            bar: { groupWidth: '100%' },
            isStacked: true,
            focusTarget: 'category',
            explorer: {
                keepInBounds: true,
                maxZoomOut: 1.0,
                maxZoomIn: 0.1,
            }
        };
        var data = google.visualization.arrayToDataTable(dataValues);
        var view = new google.visualization.DataView(data);
        var chart = new google.visualization.ColumnChart(document.getElementById("stopstalk-rating-graph"));
        chart.draw(view, options);
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
            } else if (url.search("hackerearth.com") !== -1) {
                return "hackerearth";
            } else if (url.search("atcoder.jp") !== -1) {
                return "atcoder";
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
        var accepted = val.AC, partiallyAccepted = val.PS, editorials = val.EAC;
        if(accepted === undefined) accepted = 0;
        if(partiallyAccepted === undefined) partiallyAccepted = 0;
        if(editorials === undefined) editorials = 0;
        // Math = Accepted - Not Accepted
        //      = (accepted + partiallyAccepted) - [total - (accepted + partiallyAccepted)]
        return 2 * (accepted + partiallyAccepted + editorials) - val.count;
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
        var dataTable = new google.visualization.DataTable(),
            dateList = [],
            years = new Set(),
            dt;

        dataTable.addColumn({ type: 'date', id: 'Date' });
        dataTable.addColumn({ type: 'number', id: 'Number' });
        dataTable.addColumn({ type: 'string', role: 'tooltip', 'p': {'html': true} });
        $.each(allData, function(key, val) {
            dt = key.split('-');
            years.add(dt[0]);
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
            submissionTitle = "Contribution Graph",
            acceptanceTitle = "Acceptance Graph";
        if (onlyGreen) {
            graphTitle = submissionTitle;
            colorAxisOption = onlyGreenAxis;
        } else {
            graphTitle = acceptanceTitle;
            colorAxisOption = greenRedAxis;
        }
        years = Array.from(years).map(function(el) { return parseInt(el); });
        var options = {
            legend: 'none',
            tooltip: {isHtml: true},
            title: graphTitle,
            colorAxis: colorAxisOption,
            noDataPattern: {
                backgroundColor: '#eeeeee',
                color: '#eeeeee'
            },
            height: 36 + (Math.max.apply(null, years) - Math.min.apply(null, years) + 1) * 144,
            width: 920,
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
    function drawCalendar(calendarData) {
        var calendarChart = new google.visualization.Calendar(document.getElementById('calendar_submission'));
        google.visualization.events.addListener(calendarChart, 'select', function () {
            selectHandler(calendarChart);
        });
        drawCalendarFromData(calendarChart, calendarData);
    }

    // Callback that creates and polates a data table,
    // instantiates the pie chart, passes in the data and
    // draws it.

    // ---------------------------------------------------------------------------------
    function drawPieChart(statuses) {
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
        $.each(statuses, function(i) {
            numJSON[statuses[i][1]] = statuses[i][0];
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
                    if (response === "FAILURE") {
                        $.web2py.flash("Something went wrong");
                        return;
                    }
                    canUpdate = false;
                    $button.addClass("disabled");
                    if (custom === 'True') {
                        Materialize.toast("Custom user submissions will be updated in 20 minutes", 8000);
                    } else {
                        Materialize.toast("Your submissions will be updated in 5 minutes", 8000);
                    }
                },
                error: function(err) {
                    $.web2py.flash("Something went wrong");
                    console.log(err);
                }
            });
        });
    };

    var getSolvedUnsolvedProblems = function() {

        if (totalSubmissions === '0') {
            return;
        }

        var getStopStalkProblemPageURL = function(problemLink, problemName, problemId) {
            return problemIndexURL + "?" + $.param({problem_id: problemId});
        };

        var getSpanElement = function(element, problemLink, problemName, problemId) {
            var newSpanElement = element.clone(),
                newSpanChildren = newSpanElement.children();
            newSpanChildren[0]["href"] = getStopStalkProblemPageURL(problemLink, problemName, problemId);
            newSpanChildren[0].innerHTML = problemName;
            if (isLoggedIn) {
                $(newSpanChildren[1]).attr("data-pid", problemId);
                return "<div class='todo-list-icon' style='display: inline-flex;'>" +
                       newSpanChildren[0].outerHTML +
                       newSpanChildren[1].outerHTML +
                       "</div>";
            } else {
                return newSpanChildren[0].outerHTML;
            }
        };

        var getProblemListingTable = function(response, tableType) {
            var tableData = response[tableType + "_problems"],
                tableContent = "<table class='bordered col offset-s1 s10' id='solved-unsolved-table'>",
                widgets = [$($.parseHTML(response["solved_html_widget"])),
                           $($.parseHTML(response["unsolved_html_widget"])),
                           $($.parseHTML(response["unattempted_html_widget"]))];

            var orderedCategories = ["Dynamic Programming",
                                     "Greedy",
                                     "Strings",
                                     "Hashing",
                                     "Bit Manipulation",
                                     "Trees",
                                     "Graphs",
                                     "Algorithms",
                                     "Data Structures",
                                     "Math",
                                     "Implementation",
                                     "Miscellaneous"];
            $.each(orderedCategories, function(i, category) {
                var problems = tableData[category];
                if (problems.length === 0) return;
                tableContent += "<tr>";
                tableContent += "<td class='categories'><strong>" + category + "</strong> <strong class='purple-text text-darken-3 category-pcount'>" + problems.length + "</strong></td><td> | ";
                $.each(problems, function(i, problemData) {
                    tableContent += getSpanElement(widgets[problemData[2]],
                                                   problemData[0],
                                                   problemData[1],
                                                   problemData[3]);
                    tableContent += " | ";
                });
                tableContent += "</td></tr>";
            });
            tableContent += "</table>";
            return tableContent;
        };

        $.ajax({
            url: getSolvedUnsolvedURL,
            method: "GET",
            data: {user_id: userID, custom: custom},
            success: function(response) {
                $("#solved-problems-list").html(getProblemListingTable(response, "solved"));
                $("#unsolved-problems-list").html(getProblemListingTable(response, "unsolved"));
            },
            error: function(err) {
                console.log(err);
                $.web2py.flash("Something went wrong");
            }
        });
    };

    // ---------------------------------------------------------------------------------
    var initCardSlider = function() {
        var currentActive = 0;
        $(document).keydown(function(e) {
            switch (e.which) {
                case 37: // left
                    currentActive = ((currentActive - 1) + 4) % 4;
                    break;
                case 39: // right
                    currentActive = ((currentActive + 1) + 4) % 4;
                    break;
                default:
                    return; // exit this handler for other keys
            }
            e.preventDefault(); // prevent the default action (scroll / move caret)
        });
    };

    // ---------------------------------------------------------------------------------
    var friendListModalHandler = function() {
        $('#friend-list-modal').modal();
        var $throbber = $("#view-submission-preloader").clone();
        $throbber.attr('id', 'friendsListThrobber');
        $('#friend-list').html($throbber);

        $(document).on('click', '#friend-list-button', function() {
            var $this = $(this);
            if (isLoggedIn) {
                $('#friend-list-modal').modal('open');
                $.ajax({
                    url: getFriendListUrl,
                    method: 'GET',
                    data: {'user_id': $this.data('user-id')},
                    success: function(response) {
                        $('#friend-list').html(response['table']);
                    },
                    error: function(err) {
                        $.web2py.flash('Something went wrong');
                        $('#friend-list').html("Something went wrong!");
                    }
                });
            } else {
                $.web2py.flash('Log in to see friend list.');
            }
        });
    };

    var populateProblemsAuthoredCount = function(count) {
        if(custom === 'True') return;
        var problemString = count === 1 ? 'problem' : 'problems';
        $('#problems-authored-count').html(count.toString() + " " + problemString + " authored by " + handle);
    };

    $(document).ready(function() {

        if (totalSubmissions !== "0") {
            // Load the Visualization API and the piechart package.
            getStopStalkUserStats().then(function(data) {
                populateProblemsAuthoredCount(data['problems_authored_count']);
                populateSolvedCounts(data['solved_counts']);
                $('#solved-problems').html(data['solved_problems_count']);
                $('#total-problems').html(data['total_problems_count']);
                $('#curr-streak').html(data['curr_day_streak']);
                $('#max-streak').html(data['max_day_streak']);
                $('#curr-accepted-streak').html(data['curr_accepted_streak']);
                $('#max-accepted-streak').html(data['max_accepted_streak']);
                populateSiteAccuracy(data['site_accuracies']);
                StopStalk.userStats.rating_history = data['rating_history'];
                StopStalk.userStats.calendar_data = data['calendar_data'];
                StopStalk.userStats.status_percentages = data['status_percentages'];
                google.load('visualization', '1.1', {'packages': ['corechart', 'calendar', 'bar'],
                                                     'callback': drawCharts});
            });
        } else {
            $('#user-details').css('margin-left', '32%');
        }

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

        friendListModalHandler();

        getSolvedUnsolvedProblems();

        setEditorialVoteEventListeners();

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
            $('.tooltipped').tooltip({delay: 50});
        });

        handleRefreshNow();

        $(document).on('click', '.profile-page-site-profile-url', function(e) {
            var $this = $(this),
                profileURL = $this[0]["href"];
            window.open(profileURL, '_blank');
            e.preventDefault();
        });

        $(document).on('click', '.friends-button', function() {
            var thisButton = $(this),
                userID = thisButton.attr('data-user-id'),
                buttonType = thisButton.attr('data-type'),
                child = $(thisButton.children()[0]);

            if (buttonType == 'add-friend') {
                if (isLoggedIn) {
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
                        $('.tooltipped').tooltip();
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
                    $('.tooltipped').tooltip();
                    $.web2py.flash(response);
                }).error(function(httpObj, textStatus) {
                    $.web2py.flash("[" + httpObj.status + "]: Unexpected error occurred");
                    $.web2py.flash("Unexpected error occurred");
                });
            }
        });
    });
})(jQuery);
