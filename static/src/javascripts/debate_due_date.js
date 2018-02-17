$().ready(function() {
    var today = new Date();
    $("#debate_due_date_datetimepicker").datetimepicker({
        defaultDate: today,
        minDate: today,
        format: 'MM/DD/YYYY',
    });
    $('#id_due_date').val(today.toISOString());
    $('#debate_due_date_datetimepicker').on('dp.change', function(e) {
        var datetimepicker = $(this).data("DateTimePicker")
        if (datetimepicker.date()) {
            var date = new Date(datetimepicker.date()._d)
            $('#id_due_date').val(date.toISOString());
        } else {
            datetimepicker.date(today);
            $('#id_due_date').val(today.toISOString());
        }
    })
})
