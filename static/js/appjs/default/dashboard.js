(function($) {
  "use strict";

  var populateCards = function() {
    var cardArguments = [
      {
        "class_name": "StreakCard",
        "init_arguments": [loggedInUserId, "day"]
      },
      {
        "class_name": "StreakCard",
        "init_arguments": [loggedInUserId, "accepted"]
      },
      {
        "class_name": "StreakCard",
        "init_arguments": [loggedInUserId, "accepted"]
      },
      {
        "class_name": "StreakCard",
        "init_arguments": [loggedInUserId, "accepted"]
      },
      {
        "class_name": "StreakCard",
        "init_arguments": [loggedInUserId, "accepted"]
      },
      {
        "class_name": "StreakCard",
        "init_arguments": [loggedInUserId, "accepted"]
      },
      {
        "class_name": "StreakCard",
        "init_arguments": [loggedInUserId, "accepted"]
      }
    ];

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
