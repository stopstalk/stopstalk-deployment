var LocalStorageHelper = (function() {
  var defaultNullValue = null;

  var getCardContent = function(cardIdentifier) {
    var value = localStorage.getItem(cardIdentifier);
    if (value === null) return defaultNullValue;
    value = JSON.parse(value);
    if (
        value["version"] === null ||
        parseInt(value["version"]) <= stopstalkReleaseVersion ||
        parseInt(value["user_id"]) !== loggedInUserId) {
      localStorage.removeItem(cardIdentifier);
      return defaultNullValue;
    }

    return value["content"];
  };

  var setCardContent = function(cardIdentifier, content) {
    localStorage.setItem(cardIdentifier, JSON.stringify({
      version: stopstalkReleaseVersion,
      content: content,
      user_id: loggedInUserId
    }));
  };

  return {
    defaultNullValue: defaultNullValue,
    getCardContent: getCardContent,
    setCardContent: setCardContent
  };
})();

(function($) {
  "use strict";

  var shuffleArray = function(array) {
      for (var i = array.length - 1; i > 0; i--) {
          var j = Math.floor(Math.random() * (i + 1));
          var temp = array[i];
          array[i] = array[j];
          array[j] = temp;
      }
  }

  var populateCards = function() {
    var cardArguments = [
      {
        "card_id": "streak_card_day",
        "class_name": "StreakCard",
        "init_arguments": [loggedInUserId, "day"]
      },
      {
        "card_id": "suggest_problem_card",
        "class_name": "SuggestProblemCard",
        "init_arguments": [loggedInUserId],
        "local_cache": true
      },
      {
        "card_id": "streak_card_accepted",
        "class_name": "StreakCard",
        "init_arguments": [loggedInUserId, "accepted"]
      },
      {
        "card_id": "upcoming_content_card",
        "class_name": "UpcomingContestCard",
        "init_arguments": [loggedInUserId]
      },
      {
        "card_id": "add_more_friends_card",
        "class_name": "AddMoreFriendsCard",
        "init_arguments": [loggedInUserId]
      },
      {
        "card_id": "job_profile_card",
        "class_name": "JobProfileCard",
        "init_arguments": [loggedInUserId]
      },
      {
        "card_id": "linked_accounts_card",
        "class_name": "LinkedAccountsCard",
        "init_arguments": [loggedInUserId]
      },
      {
        "card_id": "last_solved_problem_card",
        "class_name": "LastSolvedProblemCard",
        "init_arguments": [loggedInUserId]
      },
      {
        "card_id": "trending_problems_card",
        "class_name": "TrendingProblemsCard",
        "init_arguments": [loggedInUserId]
      },
      {
        "card_id": "search_by_tag_card",
        "class_name": "SearchByTagCard",
        "init_arguments": [loggedInUserId],
        "local_cache": true
      },
      {
        "card_id": "atcoder_handle_card",
        "class_name": "AtCoderHandleCard",
        "init_arguments": [loggedInUserId]
      }
    ];

    shuffleArray(cardArguments);

    cardArguments.unshift({
      "card_id": "recent_submissions_card",
      "class_name": "RecentSubmissionsCard",
      "init_arguments": [loggedInUserId]
    });

    var cardCounter = 0;
    var $currentDiv = "";
    var $containerDiv = $("#dashboard-cards-container");

    cardArguments.forEach(function(cardParams, iter) {
      var promise = new Promise(function(resolve, reject) {
        var cardCacheValue = cardParams["local_cache"] ? LocalStorageHelper.getCardContent(cardParams["card_id"]) : LocalStorageHelper.defaultNullValue;
        if (!cardParams["local_cache"] || cardCacheValue === LocalStorageHelper.defaultNullValue) {
          $.ajax({
            url: getCardURL,
            method: "GET",
            data: cardParams,
            success: function(response) {
              if (response !== "") {
                if(cardParams["local_cache"]) LocalStorageHelper.setCardContent(cardParams["card_id"], response);
                resolve(response);
              } else {
                reject();
              }
            },
            error: function(err) {
              reject(err);
            }
          });
        } else {
          setTimeout(function() {
            resolve(cardCacheValue);
          }, Math.floor(Math.random() * Math.floor(800)));
        }
      }).then(function(response) {
        if (cardCounter % 3 === 0) {
          $containerDiv.append($currentDiv);
          $currentDiv = $("<div class='row'>");
          $containerDiv.append($currentDiv);
        }
        $(response).hide().appendTo($currentDiv).fadeIn();
        cardCounter++;
        if (iter === cardArguments.length - 1 && $currentDiv !== "") $containerDiv.append($currentDiv);
      }).catch(function(err) {
        if (err) {
          console.log(err);
          $.web2py.flash("Something went wrong");
        }
      });

    });
  };

  $(document).ready(function() {
    populateCards();
  });
})(jQuery);
