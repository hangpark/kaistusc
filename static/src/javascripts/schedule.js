
$().ready(function(){
    $('#schedule_add_input_ko').attr('placeholder', $('#schedule_add_input_placeholder_ko').val());
    $('#schedule_add_input_en').attr('placeholder', $('#schedule_add_input_placeholder_en').val());

    // 한/영 변환
    $("#post-lang-func button.post-lang").click(function() {
        var lang = $(this).attr('post-lang');
        $(".schedule_title").hide();
        $(".schedule_title_" + lang).show();
        $(".selected_schedule_title").hide();
        $("#selected_schedule_title_" + lang).show();
    });

    // datetimepicker 초기화
    $('#schedule_datetimepicker').datetimepicker({
        defaultDate: $('input[name*="schedules"]').val() ? JSON.parse($('input[name*="schedules"]').val()).date : "",
        collapse: false,
        format: 'MM/DD/YYYY',
    });

    // datetimepicker 날짜선택
    $('#schedule_datetimepicker').on('dp.change', function(e) {
        var datetimepicker = $(this).data("DateTimePicker")
        if (datetimepicker.date()) {
            var date = new Date(datetimepicker.date()._d)
            var targetIndex = $('#selected_schedule_index').val();
            var targetScheduleData = $('#schedule_titles li:nth-child('+(parseInt(targetIndex)+1)+') input[name*="schedules"]')
            var newData = Object.assign(JSON.parse(targetScheduleData.val()), {date: date})
            targetScheduleData.val(JSON.stringify(newData));
        }
    })

    // 일정 타이틀 키업
    $('#schedule_add_input_ko').on('keyup', function(e) {
        validateScheduleAddInput();
        if(e.which == 13) {
            $('#schedule_add_input_en').focus();
        }
    });
    $('#schedule_add_input_en').on('keyup', function(e) {
        if(e.which == 13) {
            addSchedule();
        }
    });

    // 일정 타이틀 엔터, 서브밋 막아줌
    $('#schedule_add_input_ko, #schedule_add_input_en').on('keydown', function(e) {
        if(e.which == 13) {
            e.preventDefault();
        }
    });
    
    // 일정 추가버튼 클릭
    $('#schedule_add_submit').on('click', function(e) {
        e.stopPropagation();
        addSchedule();
    });
    $('#schedule_add_submit i').on('click', function(e) {
        if($('#schedule_add_submit').prop("disabled")){
            e.stopPropagation();
        }
    });

    // 일정 인풋창 show
    $('#schedule_add_button').on('click', function (e) {
        e.stopPropagation();
        $('#schedule_add_button_li').hide();
        $('#schedule_add_input_li').show();
        $('#schedule_add_input_ko').focus();
    });
})

// 일정 삭제
$(document).on('click', '.schedule_delete', function (e) {
    e.stopPropagation();
    var selectedIndex = parseInt($('#selected_schedule_index').val());
    var targetIndex = $(this).closest('li').index();
    $(this).closest('li').remove();
    if(selectedIndex === targetIndex) {
        $('#schedule_datetimepicker').data("DateTimePicker").date(null);
        $('#selected_schedule_title_ko, #selected_schedule_title_en').html($('#schedule_dropdown_placeholder').val());
    } else if(targetIndex < selectedIndex) {
        $('#selected_schedule_index').val(selectedIndex - 1);
    }
});

// 일정 선택
$(document).on('click', '.schedule_title_container', function(e) {
    var currentLink = $(this).closest('li')
    var schedule = JSON.parse(currentLink.find('input[name*="schedules"]').val());
    $('#selected_schedule_index').val(currentLink.index());
    window.d = $('#schedule_datetimepicker');
    $('#schedule_datetimepicker').data("DateTimePicker").date(new Date(schedule.date));
    $('#selected_schedule_title_ko').html(schedule.title_ko);
    $('#selected_schedule_title_en').html(schedule.title_en);
    $('#schedule_titles > li').removeClass('selected');
    $(this).closest('li').addClass('selected');
})

// 일정 정보 input
function addSchedule() {
    $('#schedule_add_button_li').show();
    $('#schedule_add_input_li').hide();

    var scheduleTitleKo = $("#schedule_add_input_ko").val()
    var scheduleTitleEn = $("#schedule_add_input_en").val()
    var scheduleJsonStr = JSON.stringify({
        title_ko: scheduleTitleKo,
        title_en: scheduleTitleEn,
        date: new Date(),
    })
    var data = '<input type="hidden" name="schedules" value=\''+scheduleJsonStr+'\'>'
    var currentIndex = $('#schedule_add_input_li').index();
    var scheduleDropdownListItem = '<li class="selected">'+data+'<a class="schedule_title_container"><span class="schedule_title_ko schedule_title">'+scheduleTitleKo+'</span><span class="schedule_title_en schedule_title">'+scheduleTitleEn+'</span><i class="schedule_delete fa fa-times"></i></a></li>'
    $('#selected_schedule_index').val(currentIndex);
    $('#schedule_titles > li').removeClass('selected');
    $(scheduleDropdownListItem).insertBefore("#schedule_add_input_li");
    $('#schedule_datetimepicker').data("DateTimePicker").date(new Date());
    $("#schedule_add_input_ko").val("");
    $("#schedule_add_input_en").val("");
    $('#selected_schedule_title_ko').html(scheduleTitleKo);
    $('#selected_schedule_title_en').html(scheduleTitleEn);
    validateScheduleAddInput();
}

// 일정타이틀 validate
function validateScheduleAddInput() {
    var inputValue = $('#schedule_add_input_ko').val();
    if (!inputValue) {
        $('#schedule_add_submit').prop("disabled",true);
    }
    else {
        $('#schedule_add_submit').prop("disabled",false);
    }
}