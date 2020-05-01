(function($) {
    "use strict";

    function pluralizeIfRequired(number, unit) {
      var returnVal = number + " " + unit;
      if (number != 1) returnVal += "s";
      return returnVal;
    }

    function contestCountDownHandler() {
      var countDownDate = 1554056999000; // March 31st 23:59:59 IST

      var updateCounterInterval = setInterval(function() {

        // Get todays date and time
        var now = new Date().getTime();

        // Find the distance between now and the count down date
        var distance = countDownDate - now;

        // Time calculations for days, hours, minutes and seconds
        var days = Math.floor(distance / (1000 * 60 * 60 * 24));
        var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((distance % (1000 * 60)) / 1000);

        // Output the result in an element with id="demo"
        document.getElementById("march-contest-countdown").innerHTML = pluralizeIfRequired(days, "day") + ", " +
                                                                       pluralizeIfRequired(hours, "hour") + ", " +
                                                                       pluralizeIfRequired(minutes, "minute") + ", " +
                                                                       pluralizeIfRequired(seconds, "second");

        // If the count down is over, write some text
        if (distance < 0) {
          clearInterval(updateCounterInterval);
          document.getElementById("march-contest-countdown").innerHTML = "CONTEST ENDED";
        }
      }, 1000);
    }

    $(document).ready(function() {
      $('.modal').modal();

      setEditorialVoteEventListeners();

      // contestCountDownHandler();
    });
})(jQuery);
