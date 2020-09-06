(function() {
    'use strict';

    var sendToGA = function(eventCategory, eventLabel, eventAction) {
        ga('send', {
            hitType: 'event',
            eventCategory: eventCategory,
            eventAction: eventAction,
            eventLabel: eventLabel
        });
    };

    var problemAuthorsClickHandler = function() {
        $(document).on('click', '#problems-authored-count', function() {
            var problemCount = parseInt($(this).html().split(" ")[0]);
            if (problemCount > 0) {
                sendToGA('button', 'Profile page - Non-zero problems authored link', 'click');
            } else {
                sendToGA('button', 'Profile page - No problems authored link', 'click');
            }
        })
    };

    var addEventListener = function(selector, label, buttonLabel, eventType) {
        if (!eventType) eventType = 'click';
        $(document).on(eventType, selector, function() {
            if (buttonLabel) {
                sendToGA('button', $(this).data('analytics-label'), eventType);
            } else {
                sendToGA('button', label, eventType);
            }
        });
        if (buttonLabel) {
            $(document).on('contextmenu', selector, function() {
                sendToGA('button', $(this).data('analytics-label'), 'contextmenu');
            });
        }
    };

    var addNavItemsToGA = function() {
        addEventListener('.side-nav-item', '', true);
        addEventListener('.nav-dropdown', '', true);
    };

    var addSubmissionPageButtonsToGA = function() {
        addEventListener('.download-submission-button', 'Submission Download', false);
        addEventListener('#final-download-button', 'Download button from Modal', false);
        addEventListener('.view-submission-button', 'View submission button', false);
        addEventListener('#copy-to-clipboard', 'Copy to Clipboard', false);
        addEventListener('#final-view-download-button', 'Download button View Modal', false);
        addEventListener('#link-to-site', 'View submission on Site', false);
        addEventListener('.problem-listing', 'Problem in widget', false);
        addEventListener('.add-to-todo-list', 'Add to todo list', false);
        addEventListener('.submission-user-name', 'User\'s name on submission page', false);
        addEventListener('.submission-site-profile', 'User\'s site profile on submission page', false);
    };

    var addProfilePageButtonsToGA = function() {
        addEventListener('#profile-institute-leaderboard', 'Profile Institute Leaderboard', false);
        addEventListener('#profile-user-submissions', 'Profile User Submissions', false);
        addEventListener('#profile-add-friend', 'Profile Add Friend', false);
        addEventListener('#profile-add-to-my-custom-friend', 'Profile Add to my Custom Friend', false);
        addEventListener('#profile-add-to-my-custom-friend-logged-out', 'Profile Add to my Custom Friend (Logged out)', false);
        addEventListener('#profile-unfriend', 'Profile Unfriend', false);
        addEventListener('#profile-custom-user-of', 'Profile Custom User of', false);
        addEventListener('#friend-list-button', 'View Friend List', false);
        // @ToDo: Generalize this
        addEventListener('#codechef-profile-url', 'Codechef profile URL', false);
        addEventListener('#codeforces-profile-url', 'CodeForces profile URL', false);
        addEventListener('#hackerrank-profile-url', 'HackerRank profile URL', false);
        addEventListener('#hackerearth-profile-url', 'HackerEarth profile URL', false);
        addEventListener('#spoj-profile-url', 'Spoj profile URL', false);
        addEventListener('#uva-profile-url', 'UVa profile URL', false);
        addEventListener('#toggle-submission-graph', 'Toggle Submission Graph', false);
        addEventListener('.popup-contest-page', 'Contest Page button on User Profile', false);
        addEventListener('.custom-user-count-profile-page', 'Custom user count on User Profile', false);
        addEventListener('#update-my-submissions', 'Refresh my submissions', false);
        addEventListener('#disabled-update-my-submissions', 'Disabled refresh my submissions', false);
        addEventListener('.read-editorial-user-profile-page', 'Read editorial - user profile page', false);
        addEventListener('#login-to-view-stopstalk-rating-graph', 'Profile page - login to view StopStalk rating history', false);

        problemAuthorsClickHandler();
    };

    var addMiscellaneousToGA = function() {
        addEventListener('#heart-button', 'Heart Button', false);
        addEventListener('#heart-facebook-group', 'Heart Facebook Group', false);
        addEventListener('#heart-facebook', 'Heart Facebook', false);
        addEventListener('#heart-twitter', 'Heart Twitter', false);
        addEventListener('#heart-google-plus', 'Heart Google Plus', false);
        addEventListener('#heart-github', 'Heart Github', false);
        addEventListener('#explain-problem-difficulty', 'Intro Problem difficulty', false);
        addEventListener('#problem-difficulty-title a', 'Problem page from Problem difficulty modal', false);
        addEventListener('#onboarding-button', 'Onboarding Button', false);
        addEventListener('#footer-media-kit', 'Footer Media Kit', false);
        addEventListener('#footer-privacy-policy', 'Footer Privacy Policy', false);
        addEventListener('#footer-faqs', 'Footer FAQs', false);
        addEventListener('#footer-contact-us', 'Footer Contact Us', false);
        addEventListener('#footer-stopstalk-status', 'Footer StopStalk status', false);
        addEventListener('#footer-contributors', 'Footer Contributors', false);
        addEventListener('#footer-raj454raj', 'Footer raj454raj', false);
        addEventListener('#first-friend-search', 'First friend search', false);
        addEventListener('#first-custom-friend', 'First custom friend', false);
        addEventListener('.remove-from-todo', 'Remove from todo', false);
        addEventListener('#testimonials-page', 'Write a Testimonial', false);
        addEventListener('.custom-user-count', 'Open custom user list', false);
        addEventListener('.custom-user-list-name', 'Custom user name in Modal', false);
        addEventListener('.custom-user-modal-site-profile', 'Custom user Site Profile in Modal', false);
        addEventListener('#open-side-nav', 'Open Side Navbar', false);

        addEventListener('#recent-announcements-update-job-profile-now', 'Onboarding StopStalk Job Profile', false);

        addEventListener('#problem-difficulty-later', 'Problem Difficulty modal - Later', false);
        addEventListener('#skip-this-problem', 'Problem Difficulty modal - Skip problem', false);
        addEventListener('#know-more-dashboard-page', 'Know more - Dashboard page', false);

        addEventListener('#problem-recommendations-cta', 'Find me problems - Problem recommendations', false);
    };

    var addProblemPageButtonsToGA = function() {
        addEventListener('#my-submissions-tab', 'My Submissions Tab', false);
        addEventListener('#friends-submissions-tab', 'Friends Submissions Tab', false);
        addEventListener('#global-submissions-tab', 'Global Submissions Tab', false);
        addEventListener('.problem-page-site-link', 'Problem page problem link', false);
        addEventListener('.problem-page-editorials', 'Problem page editorials link', false);
        addEventListener('.suggest-tags-plus-logged-out', 'Suggest tags plus (Logged out)', false);
        addEventListener('.suggest-tags-plus', 'Suggest tags plus', false);
        addEventListener('#show-tags', 'Show tags', false);
        addEventListener('#problem-page-difficulty-button', 'Problem page difficulty', false);
        addEventListener('.problem-page-tag', 'Problem page tag', false);
        addEventListener('.problem-setter-on-stopstalk', 'Problem author link on StopStalk', false);
        addEventListener('.problem-setter-on-profile-site', 'Problem author link on Profile Site', false);
        addEventListener('.problem-setter-text', 'Problem setter text without a link', false);
        addEventListener('#suggest-trigger', 'Problem page - suggest tag trigger', false)
    };

    var addUserEditorialsButtonsToGA = function() {
        addEventListener('#all-editorials-button', 'Read editorial page All Editorials', false);
        addEventListener('#site-editorial-link', 'Site editorial link', false);
        addEventListener('#show-editor', 'Write Editorial button', false);
        addEventListener('#submit-editorial', 'Submit Editorial button', false);
        addEventListener('#cancel-editorial', 'Cancel Editorial button', false);
    };

    var addFriendsPageButtonsToGA = function() {
        addEventListener('.friends-name', 'Friends name', false);
        addEventListener('.friends-unfriend', 'Friends unfriend', false);
        addEventListener('.friends-add-friend', 'Friends add friend', false);
    };

    var addSearchPageButtonsToGA = function() {
        addEventListener('.search-add-friend', 'Search add friend', false);
        addEventListener('.search-unfriend', 'Search unfriend', false);
        addEventListener('.search-site-profile', 'Search site profile', false);
        addEventListener('.search-user-name', 'Search user name', false);
    };

    var addContestPageButtonsToGA = function() {
        addEventListener('.view-contest', 'View Contest', false);
        addEventListener('.set-reminder', 'Set reminder', false);

    };

    var addLeaderboardPageButtonsToGA = function() {
        addEventListener('.leaderboard-institute', 'Leaderboard Institute', false);
        addEventListener('.leaderboard-country-flag', 'Leaderboard Country', false);
        addEventListener('.leaderboard-stopstalk-handle', 'Leaderboard StopStalk handle', false);
        addEventListener('#leaderboard-switch', 'Leaderboard Switch', false);
    };

    var addProblemSearchPageToGA = function() {
        addEventListener('.problem-search-problem-listing', 'Problem name problem page link');
        addEventListener('.problem-search-tag-problem-link', 'Problem search tags problem link', false);
        addEventListener('.problem-search-tags-chip', 'Problem search tags page chip', false);
        addEventListener('#problem-name', 'Problem Search Problem name field', false);
        addEventListener('#profile-site', 'Problem Search Site field', false, 'change');
        addEventListener('#orderby-problem', 'Problem Search Order By field', false, 'change');
        addEventListener('#search', 'Problem Search Site Tag field', false);
        addEventListener('#generalized-tag-search', 'Problem Search Generalized Tag field', false, 'change');
        addEventListener('#include-editorials', 'Problem Search Include Editorials field', false);
        addEventListener('.problem-search-editorial-link', 'Problem Search Editorials link', false);
    };

    var addOnboardingPageToGA = function() {
        addEventListener('.list-onboarding-things .collapsible-header', '', true);
        addEventListener('#onboarding-page-friend-search', 'Onboarding link - Friend search', false);
        addEventListener('#onboarding-page-custom-friend', 'Onboarding link - Custom friend', false);
        addEventListener('#onboarding-page-friend-trending', 'Onboarding link - Friend trending', false);
        addEventListener('#onboarding-page-friend-leaderboard', 'Onboarding link - Friend leaderboard', false);
        addEventListener('#onboarding-page-todo', 'Onboarding link - Todo page', false);
        addEventListener('#onboarding-page-problem-search', 'Onboarding link - Problem search', false);
        addEventListener('#onboarding-page-contests', 'Onboarding link - Upcoming contests', false);
        addEventListener('#onboarding-page-retrieval-logic', 'Onboarding link - Retrieval logic', false);
        addEventListener('#onboarding-page-user-profile', 'Onboarding link - User profile', false);
    };

    var addUserEditorialsPageToGA = function() {
        addEventListener('.view-user-wise-editorials', 'View userwise editorials - user editorials page', false);
        addEventListener('.read-editorial-user-editorials-page', 'Read editorial - user editorials page', false);
        addEventListener('#show-tc-editorials-contest', 'Show contest T & C - user editorials page', false);
        addEventListener('#show-info-contributions-leaderboard', 'Show contributions info - user editorials page', false);
    };

    var addUserWiseEditorialsPageToGA = function() {
        addEventListener('.read-editorial-user-wise-page', 'Read editorial - user wise editorials page', false);
    };

    var addProblemEditorialsPageToGA = function() {
        addEventListener('.read-editorial-problem-editorials-page', 'Read editorial - problem editorials page', false);
    };

    var addDashboardPageToGA = function() {
        addEventListener('.suggest-problem-card-easy', 'Cards - Suggest Easy Problem', false);
        addEventListener('.suggest-problem-card-medium', 'Cards - Suggest Medium Problem', false);
        addEventListener('.suggest-problem-card-hard', 'Cards - Suggest Hard Problem', false);
        addEventListener('.upcoming-contests-card-view-all', 'Cards - Upcoming contests View All', false);
        addEventListener('.recent-submissions-card-view-all', 'Cards - Recent submissions View All', false);
        addEventListener('.add-more-friends-card-institute-search', 'Cards - Add more friends institute search', false);
        addEventListener('.job-profile-card-update-preferences', 'Cards - Job profile update preferences', false);
        addEventListener('.linked-accounts-card-update-now', 'Cards - Linked accounts update profile', false);
        addEventListener('.linked-accounts-card-update-now', 'Cards - Linked accounts update profile', false);
        addEventListener('.last-solved-problem-write-editorial', 'Cards - Last solved problem write editorial', false);
        addEventListener('.last-solved-problem-suggest-tags', 'Cards - Last solved problem write editorial', false);
        addEventListener('.last-solved-problem-suggest-difficulty', 'Cards - Last solved problem write editorial', false);
        addEventListener('.trending-problems-card-view-all', 'Cards - Trending problems View All', false);
        addEventListener('.accepted-streak-card-pick-problem', 'Cards - Accepted streak pick problem', false);
        addEventListener('.day-streak-card-pick-problem', 'Cards - Day streak pick problem', false);
        addEventListener('.search-by-tag-card-submit', 'Cards - Search by tag Submit', false, 'submit');
        addEventListener('.atcoder-handle-card-update-now', 'Cards - Atcoder handle update now', false);
    };

    var addProblemRecommendationsPageToGA = function() {
        addEventListener('#update-problem-recommendations', 'Refresh problem recommendations', false);
        addEventListener('#close-refresh-recommendations', 'Close refresh problem recommendations modal', false);
        addEventListener('#confirm-refresh-recommendations', 'Confirm refresh problem recommendations modal', false);
        addEventListener('#recommendation-contact-us', 'Recommendation feedback', false);
        addEventListener('.recommendation-problem-listing', 'Recommendations page problem link');
        addEventListener('.recommendation-tag-problem-link', 'Recommendation tags link', false);
        addEventListener('.recommendation-tags-chip', 'Recommendations page tags chip', false);
        addEventListener('.recommendation-editorial-link', 'Recommendations page editorial link', false);
    }


    $(document).ready(function() {
        addNavItemsToGA();
        addSubmissionPageButtonsToGA();
        addProblemPageButtonsToGA();
        addProfilePageButtonsToGA();
        addFriendsPageButtonsToGA();
        addSearchPageButtonsToGA();
        addContestPageButtonsToGA();
        addLeaderboardPageButtonsToGA();
        addProblemSearchPageToGA();
        addOnboardingPageToGA();
        addUserEditorialsPageToGA();
        addUserWiseEditorialsPageToGA();
        addProblemEditorialsPageToGA();
        addDashboardPageToGA();
        addMiscellaneousToGA();
        addProblemRecommendationsPageToGA();
    });
})(jQuery);
