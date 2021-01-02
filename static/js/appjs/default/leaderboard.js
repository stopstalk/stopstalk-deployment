(function($) {
    "use strict";
    var SCROLL_BATCH_SIZE = 50;
    var currentOffset = 0;
    var userList = [];
    var requestParams;

    var getVars = function() {
        // @Todo: Better and generalised way to do this?
        var url = window.location.href,
            params = url.split('?'),
            finalObject = {},
            param;

        if (params.length == 1) {
            return {};
        }

        params = params.splice(-1)[0];
        params = params.split('&');
        $.each(params, function(key, value) {
            param = value.split('=');
            finalObject[param[0]] = param[1].replace(/\+/g, ' ')
                                            .replace(/\%2C/g, ',')
                                            .replace(/\%26/g, '&');
        });

        return finalObject;
    };

    var buildCompleteURL = function(path, params) {
        return path + "?" + decodeURI($.param(params));
    };

    var getCountryTD = function(countryDetails) {
        var td = $("<td></td>");
        if(!countryDetails) { return td.html(); }
        var countryCode = countryDetails[0],
            countryName = countryDetails[1];
        td.append("<a class='flag-icon flag-icon-" + countryCode.toLowerCase() +
                  "' href='" + buildCompleteURL(leaderboardURL,
                                                 Object.assign({},
                                                               requestParams,
                                                               {country: countryCode})) +
                  "' title='" + countryName + "'></a>");
        return td.html();
    };

    var getNameTD = function(name, stopstalkHandle, cfCount) {
        var td = $("<td></td>");

        if(cfCount > 0) {
            td.append("<div class='left'>" + name +"</div>");
            td.append("<div class='right'><button class='custom-user-count btn-floating btn-very-small' data-stopstalk-handle='" + stopstalkHandle + "'>" + cfCount + "</button></div>");
        } else {
            td.html(name);
        }
        return td.html();
    };

    var getStopStalkHandleTD = function(stopstalkHandle) {
        return "<a href='" + userProfileURL + "/" + unescapeHtml(stopstalkHandle)  + "' target='_blank'>" + stopstalkHandle + "</a>";
    };

    var getInstituteTD = function(institute) {
        return "<a href='" + buildCompleteURL(leaderboardURL,
                                              Object.assign(
                                                  {},
                                                  requestParams,
                                                  {q: unescapeHtml(institute)}
                                              )) + "'>" + institute + "</a>";
    };

    var getRatingChangesTD = function(ratingChanges) {
        if (ratingChanges > 0) {
            return "<b class='green-text text-darken-2'>+" + ratingChanges + "</b>";
        } else if (ratingChanges < 0) {
            return "<b class='red-text text-darken-2'>" + ratingChanges + "</b>";
        } else {
            return "<b class='blue-text'>" + ratingChanges + "</b>";
        }
    };

    var getPerDayChangesTD = function(perdayChanges) {
        if(perdayChanges === 0.0) {
            return "+" + perdayChanges.toFixed(5) + " <i class='fa fa-minus'></i>";
        } else if (perdayChanges > 0) {
            return "+" + perdayChanges.toFixed(5) + " <i class='fa fa-chevron-circle-up per-day-increase'></i>";
        } else {
            return perdayChanges.toFixed(5) + " <i class='fa fa-chevron-circle-down per-day-decrease'></i>";
        }
    };

    var getLeaderboardRowHTML = function(row, loggedInUser) {
        var trTag = loggedInUser ? "<tr style='background-color: #e8f7e9;'>" : "<tr>";
        return trTag + "<td>" + row[7] +
               ".</td><td>" + getCountryTD(row[5]) +
               "</td><td>" + getNameTD(row[0], row[1], row[6]) +
               "</td><td>" + getStopStalkHandleTD(row[1]) +
               "</td><td>" + getInstituteTD(row[2]) +
               "</td><td>" + row[3] +
               "</td><td>" + getPerDayChangesTD(row[4]) +
               "</td></tr>";
    };

    var processNextLeaderboardBatch = function() {
        var $tbody = $($("#leaderboard-table tbody")[0]);
        $.each(userList.slice(currentOffset, currentOffset + SCROLL_BATCH_SIZE), function(_, row) {
            $tbody.append(getLeaderboardRowHTML(row));
        });
        currentOffset += SCROLL_BATCH_SIZE;
    };

    var setupInfiniteScrolling = function() {
        $(window).scroll(function() {
            if ($(window).scrollTop() >= $(document).height() - $(window).height() - 2000) {
                processNextLeaderboardBatch();
            }
        });
    };

    var setLoggedInUserRow = function(loggedInRow) {
        var $tbody = $($("#leaderboard-table tbody")[0]);
        $tbody.append(getLeaderboardRowHTML(loggedInRow, true));
    };

    var populateLeaderboard = function() {
        $.ajax({
            url: leaderboardJSONURL,
            data: requestParams,
            success: function(response) {
                userList = response["users"];
                if(response["logged_in_row"] !== null) setLoggedInUserRow(response["logged_in_row"]);
                setupInfiniteScrolling();
                processNextLeaderboardBatch();
                // Re-initialize tooltips
                $('.tooltipped').tooltip();
            },
            error: function(err) {
                $.web2py.flash("Error loading leaderboard");
            },
            complete: function() {
                $('#leaderboard-preloader').hide();
            }
        })
    };

    var unescapeHtml = function(unsafe) {
        return unsafe
             .replace("&amp;", "&")
             .replace("&lt;", "<")
             .replace("&gt;", ">")
             .replace("&quot;", "\"")
             .replace("&#039;", "'");
     };

    $(document).ready(function() {

        if (globalLeaderboard === 'True') {
            $('#leaderboard-switch')[0].checked = true;
        }

        requestParams = getVars();

        $('#custom-users-modal').modal({
            complete: function() {
                $('#custom-users-list').html('');
                $('#custom-users-modal-header').html(headerPlaceHolder);
            }
        });

        populateLeaderboard(requestParams);

        $('#leaderboard-switch').click(function() {
            var global = this.checked;
            if (global) {
                requestParams['global'] = 'True';
            } else {
                requestParams['global'] = 'False';
            }
            window.location.href = buildCompleteURL(leaderboardURL, requestParams);
        });

        $(document).on('click', '.custom-user-count', function() {
            var placeholder = $('#custom-users-modal-header').html(),
                $this = $(this);
            $('#custom-users-modal-header').html(headerPlaceHolder + $this.data("stopstalk-handle"));
            $('#custom-users-modal').modal('open');

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
        });
    });
})(jQuery);
