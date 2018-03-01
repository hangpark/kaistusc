$().ready(function() {
  $("#delete-board-banner").click(function() {
    var boardBannerContext = document.getElementById('delete-board-banner-context')
    if (confirm("게시판 배너를 삭제하시겠습니까?")) {
      $.ajax({
          url: boardBannerContext.getAttribute('data-url'),
          type: 'POST',
          data: { csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val() },
      })
      .done(function(data) {
        location.reload();
      })
      .fail(function(data) {
        alert(data.message);
      })
    }
  });
})