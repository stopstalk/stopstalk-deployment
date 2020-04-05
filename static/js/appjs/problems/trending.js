(function($) {
    'use strict';
    $(document).ready(function() {
      var $friendsTrendingThrobber, $globalTrendingThrobber = $('#view-submission-preloader').clone();
      $globalTrendingThrobber.attr('id', 'global-trending-throbber');
      $('#global-trending-table').html($globalTrendingThrobber);

      if (userLoggedIn) {
        $friendsTrendingThrobber = $('#view-submission-preloader').clone();
        $friendsTrendingThrobber.attr('id', 'friends-trending-throbber');
        $('#friends-trending-table').html($friendsTrendingThrobber);
        $.ajax({
          url: friendsTableURL,
          method: 'GET',
          success: function(response) {
            $('#friends-trending-table').css('padding', '');
            $('#friends-trending-table').html(response);
            initTooltips();
          },
          error: function(err) {
            console.log(err);
            $.web2py.flash('Something went wrong');
          }
        });
      }

      $.ajax({
        url: globalTableURL,
        method: 'GET',
        success: function(response) {
          $('#global-trending-table').css('padding', '');
          $('#global-trending-table').html(response);
          initTooltips();
        },
        error: function(err) {
          console.log(err);
          $.web2py.flash('Something went wrong');
        }
      });
    });
})(jQuery);
