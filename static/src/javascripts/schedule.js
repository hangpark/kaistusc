$().ready(function(){
    $('#schedule-add-input-ko').attr('placeholder', $('#schedule-add-input-placeholder-ko').val());
    $('#schedule-add-input-en').attr('placeholder', $('#schedule-add-input-placeholder-en').val());

    // 한/영 변환
    $("#post-lang-func button.post-lang").click(function() {
        var lang = $(this).attr('post-lang');
        $(".schedule-title").hide();
        $(".schedule-title-" + lang).show();
        $(".selected-schedule-title").hide();
        $("#selected-schedule-title-" + lang).show();
    });

    // datetimepicker 초기화
    $('#schedule-datetimepicker').datetimepicker({
        defaultDate: $('input[name*="schedules"]').val() ? JSON.parse($('input[name*="schedules"]').val()).date : "",
        collapse: false,
        format: 'MM/DD/YYYY',
    });
    validateCurrentSchedule();

    // datetimepicker 날짜선택
    $('#schedule-datetimepicker').on('dp.change', function(e) {
        var datetimepicker = $(this).data("DateTimePicker")
        if (datetimepicker.date()) {
            var date = new Date(datetimepicker.date()._d)
            var targetIndex = $('#selected-schedule-index').val();
            var targetScheduleData = $('#schedule-titles li:nth-child('+(parseInt(targetIndex)+1)+') input[name*="schedules"]')
            var newData = Object.assign(JSON.parse(targetScheduleData.val()), {date: date})
            targetScheduleData.val(JSON.stringify(newData));
        }
    })

    // 일정 타이틀 키업
    $('#schedule-add-input-ko').on('keyup', function(e) {
        validateScheduleAddInput();
        if(e.which == 13) {
            $('#schedule-add-input-en').focus();
        }
    });
    $('#schedule-add-input-en').on('keyup', function(e) {
        if(e.which == 13) {
            addSchedule();
        }
    });

    // 일정 타이틀 엔터, 서브밋 막아줌
    $('#schedule-add-input-ko, #schedule-add-input-en').on('keydown', function(e) {
        if(e.which == 13) {
            e.preventDefault();
        }
    });
    
    // 일정 추가버튼 클릭
    $('#schedule-add-submit').on('click', function(e) {
        e.stopPropagation();
        addSchedule();
    });
    $('#schedule-add-submit i').on('click', function(e) {
        if($('#schedule-add-submit').prop("disabled")){
            e.stopPropagation();
        }
    });

    // 일정 인풋창 show
    $('#schedule-add-button').on('click', function (e) {
        e.stopPropagation();
        $('#schedule-add-button-li').hide();
        $('#schedule-add-input-li').show();
        $('#schedule-add-input-ko').focus();
    });
})

// 일정 삭제
$(document).on('click', '.schedule-delete', function (e) {
    e.stopPropagation();
    var selectedIndex = parseInt($('#selected-schedule-index').val());
    var targetIndex = $(this).closest('li').index();
    $(this).closest('li').remove();
    if(selectedIndex === targetIndex) {
        $('#schedule-datetimepicker').data("DateTimePicker").date(null);
        $('#selected-schedule-title-ko, #selected-schedule-title-en').html($('#schedule-dropdown-placeholder').val());
        $('#selected-schedule-index').val(-1);
    } else if(targetIndex < selectedIndex) {
        $('#selected-schedule-index').val(selectedIndex - 1);
    }
    validateCurrentSchedule();
});

// 일정 선택
$(document).on('click', '.schedule-title-container', function(e) {
    var currentLink = $(this).closest('li')
    var schedule = JSON.parse(currentLink.find('input[name*="schedules"]').val());
    $('#selected-schedule-index').val(currentLink.index());
    window.d = $('#schedule-datetimepicker');
    $('#schedule-datetimepicker').data("DateTimePicker").date(new Date(schedule.date));
    $('#selected-schedule-title-ko').html(schedule.title_ko);
    $('#selected-schedule-title-en').html(schedule.title_en);
    $('#schedule-titles > li').removeClass('dropdown-item-selected');
    $(this).closest('li').addClass('dropdown-item-selected');
    validateCurrentSchedule();
})

// 일정 정보 input
function addSchedule() {
    $('#schedule-add-button-li').show();
    $('#schedule-add-input-li').hide();

    var scheduleTitleKo = $("#schedule-add-input-ko").val()
    var scheduleTitleEn = $("#schedule-add-input-en").val()
    var scheduleJsonStr = JSON.stringify({
        title_ko: scheduleTitleKo,
        title_en: scheduleTitleEn,
        date: new Date(),
    })
    var data = '<input type="hidden" name="schedules" value=\''+scheduleJsonStr+'\'>'
    var currentIndex = $('#schedule-add-input-li').index();
    var scheduleDropdownListItem = '<li class="dropdown-item-selected">'+data+'<a class="schedule-title-container"><span class="schedule-title-ko schedule-title">'+scheduleTitleKo+'</span><span class="schedule-title-en schedule-title">'+scheduleTitleEn+'</span><i class="schedule-delete fa fa-times"></i></a></li>'
    $('#selected-schedule-index').val(currentIndex);
    $('#schedule-titles > li').removeClass('dropdown-item-selected');
    $(scheduleDropdownListItem).insertBefore("#schedule-add-input-li");
    $('#schedule-datetimepicker').data("DateTimePicker").date(new Date());
    $("#schedule-add-input-ko").val("");
    $("#schedule-add-input-en").val("");
    $('#selected-schedule-title-ko').html(scheduleTitleKo);
    $('#selected-schedule-title-en').html(scheduleTitleEn);
    validateScheduleAddInput();
    validateCurrentSchedule();
}

// 일정타이틀 validate
function validateScheduleAddInput() {
    var inputValue = $('#schedule-add-input-ko').val();
    if (!inputValue) {
        $('#schedule-add-submit').prop("disabled",true);
    }
    else {
        $('#schedule-add-submit').prop("disabled",false);
    }
}

function validateCurrentSchedule() {
    if(!$('#selected-schedule-index').length) return;
    
    if($('#selected-schedule-index').val() > -1) {
        $('#schedule-datetimepicker').data("DateTimePicker").enable();
    } else {
        $('#schedule-datetimepicker').data("DateTimePicker").disable();
    }
}