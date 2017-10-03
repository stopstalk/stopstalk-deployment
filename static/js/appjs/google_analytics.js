(function() {
    'use strict';

    var sendToGA = function(eventCategory, eventLabel) {
        ga('send', {
            hitType: 'event',
            eventCategory: eventCategory,
            eventAction: 'click',
            eventLabel: eventLabel
        });
    };

    var addEventListener = function(selector, label, buttonLabel) {
        $(document).on('click', selector, function() {
            if (buttonLabel) {
                sendToGA('button', $(this).data("button-label"));
            } else {
                sendToGA('button', label);
            }
        });
    };

    var addNavItemsToGA = function() {
        addEventListener('.stopstalk-nav', '', true);
        addEventListener('.nav-dropdown', '', true);
    };

    var addSubmissionPageButtonsToGA = function() {
        addEventListener('.download-submission-button', 'Submission Download');
        addEventListener('#final-download-button', 'Download button from Modal');
        addEventListener('.view-submission-button', 'View submission button');
        addEventListener('#copy-to-clipboard', 'Copy to Clipboard');
        addEventListener('#final-view-download-button', 'Download button View Modal');
        addEventListener('#link-to-site', 'View submission on Site');
        addEventListener('.problem-listing', 'Problem in widget');
        addEventListener('.add-to-todo-list', 'Add to todo list');
        addEventListener('.submission-user-name', 'User\'s name on submission page');
        addEventListener('.submission-site-profile', 'User\'s site profile on submission page');
    };

    var addProfilePageButtonsToGA = function() {
        addEventListener('#profile-institute-leaderboard', 'Profile Institute Leaderboard')
        addEventListener('#profile-user-submissions', 'Profile User Submissions');
        addEventListener('#profile-add-friend', 'Profile Add Friend');
        addEventListener('#profile-add-to-my-custom-friend', 'Profile Add to my Custom Friend');
        addEventListener('#profile-add-to-my-custom-friend-logged-out', 'Profile Add to my Custom Friend (Logged out)');
        addEventListener('#profile-unfriend', 'Profile Unfriend');
        addEventListener('#profile-custom-user-of', 'Profile Custom User of');
        // @ToDo: Generalize this
        addEventListener('#codechef-profile-url', 'Codechef profile URL');
        addEventListener('#codeforces-profile-url', 'CodeForces profile URL');
        addEventListener('#hackerrank-profile-url', 'HackerRank profile URL');
        addEventListener('#hackerearth-profile-url', 'HackerEarth profile URL');
        addEventListener('#spoj-profile-url', 'Spoj profile URL');
        addEventListener('#uva-profile-url', 'UVa profile URL');
        addEventListener('#toggle-submission-graph', 'Toggle Submission Graph');
        addEventListener('.popup-contest-page', 'Contest Page button on User Profile');
    };

    var addMiscellaneousToGA = function() {
        addEventListener('#heart-button', 'Heart Button');
        addEventListener('#footer-faqs', 'Footer FAQs');
        addEventListener('#footer-contact-us', 'Footer Contact Us');
        addEventListener('#footer-license', 'Footer MIT License');
        addEventListener('#footer-contributors', 'Footer Contributors');
        addEventListener('#footer-raj454raj', 'Footer raj454raj');
        addEventListener('#first-friend-search', 'First friend search');
        addEventListener('#first-custom-friend', 'First custom friend');
        addEventListener('.remove-from-todo', 'Remove from todo');
        addEventListener('#testimonials-page', 'Write a Testimonial');
    };

    var addProblemPageButtonsToGA = function() {
        addEventListener('#my-submissions-tab', 'My Submissions Tab');
        addEventListener('#friends-submissions-tab', 'Friends Submissions Tab');
        addEventListener('#global-submissions-tab', 'Global Submissions Tab');
        addEventListener('.problem-page-site-link', 'Problem page problem link');
        addEventListener('.problem-page-editorial-link', 'Problem page editorial link');
        addEventListener('.suggest-tags-plus-logged-out', 'Suggest tags plus (Logged out)');
        addEventListener('.suggest-tags-plus', 'Suggest tags plus');
        addEventListener('#show-tags', 'Show tags');
        addEventListener('.problem-page-tag', 'Problem page tag');
    };

    var addFriendsPageButtonsToGA = function() {
        addEventListener('.friends-name', 'Friends name');
        addEventListener('.friends-unfriend', 'Friends unfriend');
        addEventListener('.friends-add-friend', 'Friends add friend');
    };

    var addSearchPageButtonsToGA = function() {
        addEventListener('.search-add-friend', 'Search add friend');
        addEventListener('.search-unfriend', 'Search unfriend');
        addEventListener('.search-site-profile', 'Search site profile');
        addEventListener('.search-user-name', 'Search user name');
    };

    var addContestPageButtonsToGA = function() {
        addEventListener('.view-contest', 'View Contest');
        addEventListener('.set-reminder', 'Set reminder');

    };

    var addLeaderboardPageButtonsToGA = function() {
        addEventListener('.leaderboard-institute', 'Leaderboard Institute');
        addEventListener('.leaderboard-country-flag', 'Leaderboard Country');
        addEventListener('.leaderboard-stopstalk-handle', 'Leaderboard StopStalk handle');
        addEventListener('#leaderboard-switch', 'Leaderboard Switch');
    };

    var addTagsPageButtonsToGA = function() {
        addEventListener('.tag-problem-link', 'Tags problem link');
        addEventListener('.tags-chip', 'Tags page chip');
    };

    $(document).ready(function() {
        addNavItemsToGA();
        addSubmissionPageButtonsToGA();
        addProblemPageButtonsToGA();
        addProfilePageButtonsToGA();
        addFriendsPageButtonsToGA();
        addSearchPageButtonsToGA();
        addContestPageButtonsToGA();
        addLeaderboardPageButtonsToGA();
        addTagsPageButtonsToGA();
        addMiscellaneousToGA();
    });
})(jQuery);
