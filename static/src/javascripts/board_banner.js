$().ready(function() {
  $("#delete-board-banner").click(function() {
    var boardBannerContext = document.getElementById('delete-board-banner-context')
    if (confirm(boardBannerContext.getAttribute('data-confirm-msg'))) {
      $.ajax({
          url: boardBannerContext.getAttribute('data-url'),
          type: 'POST',
          data: { csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val() },
      })
      .done(function(data) {
        var boardBanner = document.getElementById('board-banner');
        boardBanner.removeChild(boardBanner.firstChild);
        var pullRight = boardBanner.firstChild;
        while (pullRight.firstChild) {
          pullRight.removeChild(pullRight.firstChild);
        }
        boardBanner.insertBefore(
          $.parseHTML(
            '<b>' + 
            boardBannerContext.getAttribute('data-no-banner-msg') + 
            '</b>'
          ), 
          pullRight
        )
        pullRight.appendChild($.parseHTML(
          '<a href="' + 
          boardBannerContext.getAttribute('current-url') + 
          '/banner/new/">' + 
          boardBannerContext.getAttribute('data-register-text') + 
          '</a>')
        )
      })
      .fail(function(data) {
        alert(data.message);
      })
    }
  });
})