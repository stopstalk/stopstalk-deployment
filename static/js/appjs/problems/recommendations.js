(function($) {
    'use strict';
    $(document).ready(function() {
        $('#recommendation-refresh-modal').modal();

        $('#confirm-refresh-recommendations').click(function() {
            var $this = $(this);
            $.ajax({
                url: fetchRecommendationsUrl,
                method: 'GET',
                data: {refresh: canUpdate},
                success: function(response) {
                    $('#recommendation-table').html(response['table']);

                    if (response['can_update'] === false) {
                        $this.addClass("disabled");
                    } else {
                        $this.removeClass("disabled");
                    }
                },
                error: function(err) {
                  $.web2py.flash('Could not fetch new recommendations.');
                }
            });
        });

        $(document).on('click', '.problem-listing, .tag-problem-link', function() {
            var $this = $(this);
            var pid = $this.data('pid');

            $.ajax({
                url: '/problems/update_recommendation_status/' + pid,
                method: 'POST',
                success: function(response) {
                },
                error: function(err) {
                }
            })
        });
    });
})(jQuery);