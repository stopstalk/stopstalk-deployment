(function($) {
    "use strict";

    var initFieldsWithRecordValues = function() {
        if(!Object.keys(resumeDataRecord).length) return;

        $('#resume_data_opportunity_type').val(resumeDataRecord.fulltime_or_internship);
        $('#resume_data_github_profile').val(resumeDataRecord.github_profile);
        $('#resume_data_linkedin_profile').val(resumeDataRecord.linkedin_profile);
        $('#resume_data_expected_salary').val(resumeDataRecord.expected_salary);
        $('#resume_data_will_relocate').prop('checked', resumeDataRecord.will_relocate);
        $('#resume_data_experience').val(resumeDataRecord.experience);
        $('#resume_data_join_from').val(resumeDataRecord.join_from.split(" ")[0]);
        $('#resume_data_contact_number').val(resumeDataRecord.contact_number);
        $('#resume_data_graduation_year').val(resumeDataRecord.graduation_year);
        $('#resume_data_can_contact').prop('checked', resumeDataRecord.can_contact);
        $('select').material_select();
    };

    $(document).ready(function() {
        $('.datepicker').pickadate({
            selectMonths: true, // Creates a dropdown to control month
            selectYears: 10,
            format: 'yyyy-mm-dd',
            min: new Date(),
            closeOnSelect: true
        });

        $('#resume-data-form').submit(function(e) {
            var MAX_FILE_SIZE = 2 * 1024 * 1024;
            var fileInput = $('#resume_data_file');
            if(fileInput.get(0).files.length){
                var fileSize = fileInput.get(0).files[0].size; // in bytes
                if(fileSize > MAX_FILE_SIZE){
                    $.web2py.flash('Please upload file smaller than 2 MB');
                    return false;
                }
            }

            if ($('#resume_data_opportunity_type').val() === null) {
                $.web2py.flash('Please select Job/Internship');
                return false;
            }

            if ($('#resume_data_join_from').val() === "") {
                $.web2py.flash('Please enter when will you be able to join');
                return false;
            }

            if ($('#resume_data_graduation_year').val() === "") {
                $.web2py.flash('Please enter your graduation year');
                return false;
            }
        });

        initFieldsWithRecordValues();
    });
})(jQuery);
