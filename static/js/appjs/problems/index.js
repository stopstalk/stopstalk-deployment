(function($) {
    "use strict";

    var refreshSuggestedTags = function() {
        $.ajax({
            method: 'GET',
            url: '/problems/get_suggested_tags.json',
            data: {
                plink: problemLink
            }
        }).done(function(response) {
            var userTags = response["user_tags"],
                tagCounts = response["tag_counts"],
                $inputElement = $('#tag-suggests'),
                $div = $('<div>');

            $inputElement.materialtags('removeAll');

            $.each(userTags, function(index, tag) {
                $inputElement.materialtags('add', tag);
            });

            var i = 0;
            $.each(tagCounts, function(index, row) {
                i += 1;
                $div.append('<div class="chip grey"><span class="red">' + row[1] + '</span>' + row[0]['text'] + '</div> ');
                if (i % 3 == 0) $div.append('<br/><br/>');
            });

            if (tagCounts.length != 0) {
                $('#tags-till-now').html($div);
            } else {
                $('#tags-till-now').html('You are the first to suggest');
            }
        });
    };

    var handleSubmissionTabs = function() {
        var $submissionTabs = $('#submission-tabs');

        $submissionTabs.tabs();
        $submissionTabs.tabs('select_tab', submissionType);

        $('#submission-tabs li').click(function() {
            var value = $(this).attr("value"),
                redirectURL;
            if (value === "global") {
                redirectURL = globalSubmissionURL;
            } else if (value === "my") {
                redirectURL = mySubmissionURL;
            } else {
                redirectURL = friendsSubmissionURL;
            }
            window.location.href = redirectURL;
        });
    };

    $(document).ready(function() {

        $('.tooltipped').tooltip({
            delay: 50
        });

        handleSubmissionTabs();

        setTimeout(function() {
            $('#problem-page-editorial-button').removeClass('pulse');
        }, 10 * 1000);

        var $pieThrobber = $("#view-submission-preloader").clone();
        $pieThrobber.attr('id', 'problemsPagePieThrobber');
        $('#chart_div').html($pieThrobber);

        $('#show-tags').click(function() {
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
                $sampleTag.append('<a class="problem-page-tag" href="" style="color: white;" target="_blank"></a>');
                $.each(problemTags, function(index, tag) {
                    $thisTag = $sampleTag.clone();
                    $thisAnchor = $($thisTag.children()[0]);
                    $thisAnchor.html(tag);
                    $thisAnchor.attr('href', '/problems/tag/' + '?page=1&q=' + encodeURIComponent(tag));
                    $tagsSpan.append($thisTag);
                    $tagsSpan.append(" ");
                });
            }
            $('#tags-span').html($tagsSpan);
        });

        $('.modal').modal();

        if (isLoggedIn) {
            if (openSuggestTagsModal) $('.suggest-tags-plus').trigger('click');
            if (openProblemDifficultyModal) {
                setTimeout(function() {
                    $('#problem-page-difficulty-button').trigger('click')
                }, 10);
            }

            $('#submit-tags').click(function() {
                var submittedTags = $('#tag-suggests').val();
                $('#suggest-tags-modal').modal('close');
                $.ajax({
                    method: 'POST',
                    url: '/problems/add_suggested_tags',
                    data: {
                        problem_id: problemId,
                        tags: submittedTags
                    }
                }).done(function(response) {
                    $.web2py.flash(response);
                    refreshSuggestedTags();
                });
            });
            refreshSuggestedTags();
        }
    });

})(jQuery);
