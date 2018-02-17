
$().ready(function(){
    if($('#project-timeline').length) {
        postProjectTimelineInitialize();

        $('#project-timeline-nav-button-right').on('click', function(e) {
            var sliderLeft = $('#project-timeline-slider').position().left;
            var firstPoint = $('.project-timeline-point').first();
            var lastPoint = $('.project-timeline-point').last();
            var timelineWidth = $('#project-timeline').width();
            var left = sliderLeft + firstPoint.position().left;
            var right = sliderLeft + lastPoint.position().left + lastPoint.width();
            var vector = right - timelineWidth > timelineWidth ? -timelineWidth : -right + timelineWidth;
            _movePostTimelineSlider(vector);
        })

        $('#project-timeline-nav-button-left').on('click', function(e) {
            var sliderLeft = $('#project-timeline-slider').position().left;
            var firstPoint = $('.project-timeline-point').first();
            var timelineWidth = $('#project-timeline').width();
            var left = sliderLeft + firstPoint.position().left;
            var vector = left < -timelineWidth ? timelineWidth : -left;
            _movePostTimelineSlider(vector);
        })
    }
})

function _movePostTimelineSlider(vector) {
    $( "#project-timeline-slider" ).animate({
        left: "+=" + vector,
      }, 500, _renderPostTimelineNvigateButton);
    $( "#project-timeline-current" ).animate({
        left: "+=" + vector,
    }, 500, _renderPostTimelineNvigateButton);
    _renderPostTimelineNvigateButton();
}

function postProjectTimelineInitialize() {
    var date_datas = $('.project-timeline-date-data');
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
    $('#project-timeline-slider').css('left', percentage + '%');
    _renderPostTimelineNvigateButton();
}

function _renderPostTimelineNvigateButton() {
    var sliderLeft = $('#project-timeline-slider').position().left;
    var firstPoint = $('.project-timeline-point').first();
    if(!firstPoint.length) return;
    var lastPoint = $('.project-timeline-point').last();
    var timelineWidth = $('#project-timeline').width();
    var left = sliderLeft + firstPoint.position().left;
    var right = sliderLeft + lastPoint.position().left + lastPoint.width();
    if(left <= -1) {
        $('#project-timeline-nav-button-left').show();
    } else {
        $('#project-timeline-nav-button-left').hide();
    }
    if(right >= timelineWidth+1) {
        $('#project-timeline-nav-button-right').show();
    } else {
        $('#project-timeline-nav-button-right').hide();
    }
}
    
