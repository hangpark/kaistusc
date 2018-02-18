$().ready(function() {
  // this part should work only when board is sponsor
  if (document.getElementById('sponsor-context')) {
    var numSponsors = document.getElementsByClassName('list-group-item').length;
    $(window).on("scroll", function() {
      var scrollHeight = $(document).height();
      var scrollPosition = $(window).height() + $(window).scrollTop();
      if ((scrollHeight - scrollPosition) / scrollHeight === 0) {
          // when scroll to bottom of the page
          // load more posts
      }
    });
  }
});