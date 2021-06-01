(function($) {
    'use strict';
    $(document).ready(function() {
        $('#recommendation-refresh-modal').modal();

        $('.show-recommended-problem-tags').click(function() {
            var problemTags = $(this).data('tags');
            var $tagsSpan = $('<span>');
            if (problemTags.length === 1 && problemTags[0] === '-') {
                $tagsSpan.append('No Tags Available');
            } else {
                var $sampleTag = $('<div>', {
                        'class': 'chip'
                    }),
                    $thisTag,
                    $thisAnchor;
                $sampleTag.append('<a class="recommendation-tags-chip" href="" style="color: white;" target="_blank"></a>');
                $.each(problemTags, function(index, tag) {
                    $thisTag = $sampleTag.clone();
                    $thisAnchor = $($thisTag.children()[0]);
                    $thisAnchor.html(tag);
                    $thisAnchor.attr('href', '/problems/tag/' + '?page=1&q=' + encodeURIComponent(tag));
                    $tagsSpan.append($thisTag);
                    $tagsSpan.append(" ");
                });
            }
            $(this).parent().hide().html($tagsSpan).fadeIn("slow");
        });

        $('#confirm-refresh-recommendations').click(function() {
            var $this = $(this);
            $.ajax({
                url: fetchRecommendationsUrl,
                method: 'GET',
                data: {refresh: canUpdate},
                success: function(response) {
                    $('#recommendations-table-content').html(response['table']);

                    if (response['can_update'] === false) {
                        $('#update-problem-recommendations').addClass("disabled");
                    } else {
                        $('#update-problem-recommendations').removeClass("disabled");
                    }
                },
                error: function(err) {
                  $.web2py.flash('Could not fetch new recommendations.');
                }
            });
        });

        $(document).on('click', '.recommendation-problem-listing, .recommendation-tag-problem-link', function() {
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