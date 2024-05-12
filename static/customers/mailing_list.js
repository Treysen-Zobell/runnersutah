$(document).ready(function () {
    $('#add-email').click(function () {
        $('<div>' +
            '<i class="remove-email fa-solid fa-trash"></i>' +
            '<input type="email" name="email_list" placeholder="Email Address">' +
            '<input type="text" name="tag_list" placeholder="Product Type 1, Product Type 2">' +
            '</div>').appendTo('#email-container');
    });

    $(document).on('click', '.remove-email', function () {
        $(this).parent().remove();
    });
});