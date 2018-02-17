$().ready(function() {
    function convert2html(str, withP) {
        return "<p>" + str.replace(/^\n+/g, "").replace(/\n+$/g, "").replace(/\n{2,}/g, "</p><p>").replace(/\n/g, "<br>") + "</p>";
    }

    $(".comment-content").each(function() {
        $(this).html(convert2html($(this).html()));
    });

    $("#btn-comment-form").click(function() {
        var $btn = $(this);
        if (!$("#comment-form textarea").val()) {
            alert($("#comment-no-input").val());
            return;
        }
        if ($btn.hasClass("disabled"))
            return;
        $btn.addClass("disabled");
        $.ajax({
            url: './comment/',
            type: 'POST',
            data: new FormData($("#comment-form")[0]),
            cache: false,
            contentType: false,
            processData: false,
        })
        .done(function(data) {
            $("#comment-list").prepend(data);
            $(".comment-content:last").each(function () {
                $(this).html(convert2html($(this).html()));
            });
            $("#comment-form textarea").val("");
            $("#comment-form-file").val("");
        }).fail(function(e) {
            alert("Request Failed");
        }).always(function() {
            $btn.removeClass("disabled");
        });
    });

    $('#comment-form-content-wrap').on( 'keyup', 'textarea', function (e){
        $(this).css('height', 'auto' );
        $(this).height( this.scrollHeight);
        if($(this).outerHeight() >= parseInt($(this).css('max-height'))) {
            $(this).css('overflow-y', 'auto' );
        } else {
            $(this).css('overflow-y', 'hidden' );
        }
        
    });

    $('#comment-prev-btn span').on('click', function(e) {
        var nextPageNum = $('#comment-next-page-num').val();
        $.getJSON('./comment/?p=' + nextPageNum, function(data){
            var comments = data.comments;
            nextPageNum = data.next_page_num;
            comments.forEach(function(comment_html){
                $(comment_html).insertBefore("#comment-prev-btn");
            });
            if(nextPageNum) {
                $('#comment-next-page-num').val(nextPageNum);
            } else {
                $('#comment-prev-btn').remove();
            }
        })  
    })
});

$(document).on('click', ".comment-remove", function() {
    var $comment = $(this).parents(".comment");
    var $form = $(this).parent();
    if (confirm($("#delete-comment-warning").val())) {
        $.post($form.attr('action'), $form.serialize())
            .done(function(data) {
                $comment.replaceWith(data);
            }).fail(function() {
                alert("Request Failed");
            });
    }
});