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
        "class_name": "StreakCard",
        "init_arguments": [loggedInUserId, "day"]
      },
      {
        "class_name": "SuggestProblemCard",
        "init_arguments": [loggedInUserId]
      },
      {
        "class_name": "StreakCard",
        "init_arguments": [loggedInUserId, "accepted"]
      },
      {
        "class_name": "UpcomingContestCard",
        "init_arguments": [loggedInUserId]
      },
      {
        "class_name": "RecentSubmissionsCard",
        "init_arguments": [loggedInUserId]
      }
    ];

    shuffleArray(cardArguments);

    var cardCounter = 0;
    var $currentDiv = "";
    var $containerDiv = $("#dashboard-cards-container");

    cardArguments.forEach(function(cardParams, iter) {
      var promise = new Promise(function(resolve, reject) {
        $.ajax({
          url: getCardURL,
          method: "GET",
          data: cardParams,
          success: function(response) {
            if (response !== "") resolve(response);
            else reject();
          },
          error: function(err) {
            reject(err);
          }
        });
      }).then(function(response) {
        if (cardCounter % 3 === 0) {
          $containerDiv.append($currentDiv);
          $currentDiv = $("<div class='row'>");
          $containerDiv.append($currentDiv);
        }
        // $currentDiv.append(response);
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
