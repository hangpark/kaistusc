$(document).ready(function() {
  $(".rule-article p.rule-clause").each(function() {
    $para = $(this);
    var lines = $para.html().replace(/\s(제(\d+)조)/g, " <a href='javascript:void(0);' class='rule-article-popup' data-article-num='$2'>$1</a>").split("\n");
    if (lines.length == 1) {
      $para.html(lines[0]);
      return;
    }
    var new_para = "<p class='rule-clause'>" + lines.join("</p><p class='rule-clause'>") + "</p>";
    $para.after(new_para);
    $para.remove();
  });
  $(".rule-viewer").on('click', ".rule-article-popup", function() {
    $("#rule-modal-article").html($("#article-" + $(this).attr('data-article-num')).html());
    $("#rule-modal").modal('show');
  });
});
