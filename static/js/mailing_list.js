$(document).ready(function () {
    $('#add-email').click(function () {
        let formIdx = $('#id_form-TOTAL_FORMS').val();
        $('#email-container').append(
            $('<div class="email-entry">' +
                '<i class="remove-email fa-solid fa-trash"></i>' +
                '<input type="text" name="form-' + formIdx + '-address" class="email-option" placeholder="Email Address">' +
                '<select name="form-' + formIdx + '-tags" class="tag-option" multiple>' +
                '   <option value="any">Any</option>' +
                '   <option value="poly_pipe">Poly Pipe</option>' +
                '   <option value="line_pipe">Line Pipe</option>' +
                '   <option value="composite_pipe">Composite Pipe</option>' +
                '   <option value="flex_pipe">Flexpipe</option>' +
                '   <option value="tubing_sand_screens">Tubing - Sand Screens</option>' +
                '   <option value="tubing">Tubing</option>' +
                '   <option value="casing">Casing</option>' +
                '   <option value="other">Other</option>' +
                '</select>' +
                '<input type="checkbox" name="form-' + formIdx + '-DELETE" class="delete-checkbox" style="display: none">' +
                '<input type="hidden" id="id_form-' + formIdx + '-id" name="form-' + formIdx + '-id">' +
                '</div>'
            )
        );
        $('#id_form-TOTAL_FORMS').val(parseInt(formIdx) + 1);
    });

    $(document).on('click', '.remove-email', function () {
        $(this).siblings().prop('checked', true);
        $(this).closest('.email-entry').hide();
    });
});