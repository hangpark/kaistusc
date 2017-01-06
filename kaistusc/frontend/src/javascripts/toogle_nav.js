/* 모바일 환경에서 네비게이션 토글기능 구현 */
$().ready(function() {
    var wrapper = $('#wrapper');
    var trigger = $('#side-nav-toggle');
    var overlay = $('#overlay');

    function toggle_side_nav() {
        overlay.toggle();
        wrapper.toggleClass('toggled');
    }

    function open_side_nav(e) {
        toggle_side_nav();
        e.stopPropagation();
        $('#side-nav .current-menu').addClass('open');
    }

    trigger.click(open_side_nav);
    overlay.click(toggle_side_nav);
});
