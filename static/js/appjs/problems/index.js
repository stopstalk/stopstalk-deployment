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
                $div = $('<div>', {
                    'class': 'centered striped'
                });

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
    }

    $(document).ready(function() {

        $('.tooltipped').tooltip({
            delay: 50
        });
        if (globalSubmissions === 'True') {
            $('#submission-switch')[0].checked = true;
        }
        $('#submission-switch').click(function() {
            var redirectURL = null;
            if (globalSubmissions === 'True') {
                redirectURL = friendsSubmissionURL;
            } else {
                redirectURL = globalSubmissionURL;
            }
            window.location.href = redirectURL;
        });

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
                $sampleTag.append('<a href="" style="color: white;" target="_blank"></a>');
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

        if (isLoggedIn == "True") {

            if (openModal)
                $('#suggest-tags-modal').openModal();

            $('#suggest-trigger').leanModal();

            $('#submit-tags').click(function() {
                var submittedTags = $('#tag-suggests').val();
                $('#suggest-tags-modal').closeModal();
                $.ajax({
                    method: 'POST',
                    url: '/problems/add_suggested_tags/',
                    data: {
                        pname: problemName,
                        plink: problemLink,
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