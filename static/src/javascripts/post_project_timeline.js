
$().ready(function(){
    if($('#project_timeline').length) {
        postProjectTimelineInitialize();

        $('#project_timeline_nav_button_right').on('click', function(e) {
            var sliderLeft = $('#project_timeline_slider').position().left;
            var firstPoint = $('.project_timeline_point').first();
            var lastPoint = $('.project_timeline_point').last();
            var timelineWidth = $('#project_timeline').width();
            var left = sliderLeft + firstPoint.position().left;
            var right = sliderLeft + lastPoint.position().left + lastPoint.width();
            var vector = right - timelineWidth > timelineWidth ? -timelineWidth : -right + timelineWidth;
            _movePostTimelineSlider(vector);
        })

        $('#project_timeline_nav_button_left').on('click', function(e) {
            var sliderLeft = $('#project_timeline_slider').position().left;
            var firstPoint = $('.project_timeline_point').first();
            var timelineWidth = $('#project_timeline').width();
            var left = sliderLeft + firstPoint.position().left;
            var vector = left < -timelineWidth ? timelineWidth : -left;
            _movePostTimelineSlider(vector);
        })
    }
})

function _movePostTimelineSlider(vector) {
    $( "#project_timeline_slider" ).animate({
        left: "+=" + vector,
      }, 500, _renderPostTimelineNvigateButton);
    $( "#project_timeline_current" ).animate({
        left: "+=" + vector,
    }, 500, _renderPostTimelineNvigateButton);
    _renderPostTimelineNvigateButton();
}

function postProjectTimelineInitialize() {
    var date_datas = $('.project_timeline_date_date');
    var dates = date_datas.map(function(e){
        return new Date($(this).val());
    });
    var now = new Date();
    window.d = dates;

    if(dates.length && dates[0] > now) {
        _slidePostTimeline(60);
        return;
    }
    for(var i=0; i<dates.length - 1; i++) {
        var prev = dates[i]
        var next = dates[i+1]
        if(now < next) {
            var shiftingRatio = (now - prev) / (next - prev);
            _slidePostTimeline(-(20 * (i - 2 + shiftingRatio)));
            return;
        }
    }
    _slidePostTimeline(-(20 * (dates.length - 2)));
}

function _slidePostTimeline(percentage) {
    $('#project_timeline_slider').css('left', percentage + '%');
    _renderPostTimelineNvigateButton();
}

function _renderPostTimelineNvigateButton() {
    var sliderLeft = $('#project_timeline_slider').position().left;
    var firstPoint = $('.project_timeline_point').first();
    if(!firstPoint.length) return;
    var lastPoint = $('.project_timeline_point').last();
    var timelineWidth = $('#project_timeline').width();
    var left = sliderLeft + firstPoint.position().left;
    var right = sliderLeft + lastPoint.position().left + lastPoint.width();
    if(left <= -1) {
        $('#project_timeline_nav_button_left').show();
    } else {
        $('#project_timeline_nav_button_left').hide();
    }
    if(right >= timelineWidth+1) {
        $('#project_timeline_nav_button_right').show();
    } else {
        $('#project_timeline_nav_button_right').hide();
    }
}
    
