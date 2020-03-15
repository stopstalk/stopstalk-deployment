(function($) {
    "use strict";

    $(document).ready(function() {

        $(document).on('mouseenter', '#problem-setter-page-table tr', function() {
            var todoIcon = $(this).find('.add-to-todo-list');
            todoIcon.show();
        });

        $(document).on('mouseleave', '#problem-setter-page-table tr', function() {
            var todoIcon = $(this).find('.add-to-todo-list');
            todoIcon.hide();
        });

    });
})(jQuery);
