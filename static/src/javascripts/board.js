$().ready(function() {
    function convert2html(str) {
        return "<p>" + str.replace(/^\n+/g, "").replace(/\n+$/g, "").replace(/\n{2,}/g, "</p><p>").replace(/\n/g, "<br>") + "</p>";
    }

    $("#post-content, .comment-content").each(function() {
        $(this).html(convert2html($(this).html()));
    });

    $("#post-lang-func button.post-lang").click(function() {
        var lang = $(this).attr('post-lang');
        $(".post-form-lang").hide();
        $("#post-form-lang-" + lang).show();

        var $btns = $("#post-lang-func button.post-lang");
        $btns.removeClass("btn-primary");
        $btns.removeClass("active");
        $btns.addClass("btn-default");
        $(this).addClass("btn-primary");
        $(this).addClass("active");
        $(this).removeClass("btn-default");
    });

    $(".prev-file-del").click(function() {
        $(this).parent().remove();
    });

    $(document).on('click', ".file-more", function() {
        var attachFileHtml = '<div class="attach-file col-xs-12 nopadding"><input type="file" name="files"><span class="file-more"><i class="fa fa-plus"></i></span></div>'
        $(attachFileHtml).appendTo($("#attach-file-wrap"));
        $(this).html($("#file-del-desc").html());
        $(this).removeClass("file-more");
        $(this).addClass("file-del");
    });
    $(document).on('click', ".file-del", function() {
        var e = $(this).parent();
        if (e.is(":first-child") && !e.next().length)
            e.clone().appendTo("#attach-file-wrap");
        e.remove();
    });

    $("#btn-comment-form").click(function() {
        var $btn = $(this);
        if (!$("#comment-form textarea").val()) {
            alert($("#comment-no-input").html());
            return;
        }
        if ($btn.hasClass("disabled"))
            return;
        $btn.addClass("disabled");
        $.post("./comment/", $("#comment-form").serialize())
            .done(function(data) {
                $("#comment-list").append(data);
                $(".comment-content:last").each(function () {
                    $(this).html(convert2html($(this).html()));
                });
                $("#comment-form textarea").val("");
            }).fail(function() {
                alert("Error");
            }).always(function() {
                $btn.removeClass("disabled");
            });
    });

    $("#comment-list").on('click', ".comment-remove", function() {
        var $comment = $(this).parents(".comment");
        var $form = $(this).parent();
        if (confirm($("#delete-comment-warning").text())) {
            $.post($form.attr('action'), $form.serialize())
                .done(function(data) {
                    $comment.find(".comment-content").html($("#deleted-comment-content").html());
                }).fail(function() {
                    alert("Error");
                });
        }
    });

    $("#post-vote form").click(function() {
        $vote = $(this).find(".vote-status");
        $.post($(this).attr('action'), $(this).serialize())
            .done(function(data) {
                if (data == "True")
                    $vote.html(parseInt($vote.html())+ 1)
                else if (data == "False")
                    alert("이미 평가하셨습니다.");
            }).fail(function(data) {
                alert("권한이 없습니다.");
            });
    });

    $('.tag-item').click(function(e) {
        e.stopPropagation();
    })

    $('#id_board_tab').on('changed.bs.select', function (e) {
        var is_selected = false;
        var options = e.currentTarget.options;
        for (var i = 0; i < options.length; i++) {
            if (options[i].selected) {
                is_selected = true;
            }
        }
        if (!is_selected) {
            val = $('#current_tab')[0].value || e.currentTarget.options[0].value;
            $('#id_board_tab option[value=' + val + ']').prop("selected", true);
        }
        $('#id_board_tab').selectpicker('refresh')
    });

});
