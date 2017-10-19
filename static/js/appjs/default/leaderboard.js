(function($) {
    "use strict";

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
        return path + "?" + $.param(params);
    };

    var createLeaderBoardTable = function(userList, requestParams) {

        var getCountryTD = function(countryDetails) {
            var td = $("<td></td>");
            if(!countryDetails) { return td.html(); }
            var countryCode = countryDetails[0],
                countryName = countryDetails[1];
            td.append("<a href='" + buildCompleteURL(leaderboardURL,
                                                     Object.assign({},
                                                                   requestParams,
                                                                   {country: countryCode})) +
                      "'><span class='flag-icon flag-icon-" + countryCode.toLowerCase() +
                      "' title='" + countryName + "'></span></a>");
            return td.html();
        };

        var getNameTD = function(name, stopstalkHandle, cfCount) {
            var td = $("<td></td>");
            td.append("<div class='left'>" + name +"</div>")

            if(cfCount > 0) {
                td.append("<div class='right'><button class='custom-user-count btn-floating btn-very-small tooltipped' data-position='right' data-delay='50' data-tooltip='Number of custom users' data-stopstalk-handle='" + stopstalkHandle + "'>" + cfCount + "</button></div>");
            }
            return td.html();
        };

        var getStopStalkHandleTD = function(stopstalkHandle) {
            return "<a target='_blank' class='leaderboard-stopstalk-handle' href='" + userProfileURL + "/" + stopstalkHandle + "'>" + stopstalkHandle + "</a>";
        };

        var getInstituteTD = function(institute) {
            return "<a class='leaderboard-institute' href='" +
                   buildCompleteURL(leaderboardURL,
                                    Object.assign({},
                                    requestParams,
                                    {q: institute})) +
                   "'>" + institute + "</a>";
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

        var rank = 1;
        var $tbody = $($("#leaderboard-table tbody")[0]);
        $.each(userList, function(_, row) {
            $tbody.append("<tr><td class='center-align'>" + rank.toString() +
                          ".</td><td class='center-align'>" + getCountryTD(row[6]) +
                          "</td><td>" + getNameTD(row[0], row[1], row[7]) +
                          "</td><td>" + getStopStalkHandleTD(row[1]) +
                          "</td><td>" + getInstituteTD(row[2]) +
                          "</td><td class='center-align'>" + row[3] +
                          "</td><td class='center-align'>" + getRatingChangesTD(row[5]) +
                          "</td><td class='center-align'>" + getPerDayChangesTD(row[4]) +
                          "</td></tr>");
            ++rank;
        });
    };

    var populateLeaderboard = function(params) {
        $.ajax({
            url: leaderboardJSONURL,
            data: params,
            success: function(response) {
                createLeaderBoardTable(response["users"], params);
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

    $(document).ready(function() {

        if (globalLeaderboard === 'True') {
            $('#leaderboard-switch')[0].checked = true;
        }

        var params = getVars();

        $('#custom-users-modal').modal({
            complete: function() {
                $('#custom-users-list').html('');
                $('#custom-users-modal-header').html(headerPlaceHolder);
            }
        });

        populateLeaderboard(params);

        $('#leaderboard-switch').click(function() {
            var global = this.checked;
            var redirectURL = null;
            var currentURL = window.location.href;
            if (global) {
                params['global'] = 'True';
            } else {
                params['global'] = 'False';
            }
            window.location.href = buildCompleteURL(leaderboardURL, params);
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