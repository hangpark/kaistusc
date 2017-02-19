$().ready(function() {
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
        $("#attach-file-wrap").children(":last").clone().appendTo($("#attach-file-wrap"));
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
});
