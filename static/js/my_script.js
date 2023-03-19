function submitAllCheckboxes() {
    var checkboxes = document.querySelectorAll('input[type=checkbox]');
    checkboxes.forEach(function (checkbox) {
        var id = checkbox.id;
        submitCheckbox(id);
    });
}

function submitCheckbox(id) {
    var isChecked = document.getElementById(id).checked;
    $.ajax({
        type: "POST",
        url: "/submit_checkbox",
        data: JSON.stringify({ 'id': id, 'isChecked': isChecked }),
        contentType: 'application/json',
        success: function (response) {
            console.log(response);
            location.reload();
        },
        error: function (error) {
            console.log(error);
        }
    });
}
$(document).ready(function () {
    $('input[type="checkbox"]').on('change', function () {
        var id = $(this).attr('id');
        submitCheckbox(id);
    });
});




