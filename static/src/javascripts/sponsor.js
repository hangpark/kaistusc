$().ready(function() {
  // this part should work only when board is sponsor
  if (document.getElementById('sponsor-context')) {

    var getHtmlStrOfImgs = function (fileSet) {
      return fileSet.map(function (elem) {
        return '<img src="' + elem.file +'" alt="Failed to load photo">'
      }).join();
    }

    var escapeHTML = function(htmlStr) {
      'use strict';

      return htmlStr.replace(/[&<>"\n]/g, function (tag) {
        var charsToReplace = {
          '&': '&amp;',
          '<': '&lt',
          '>': '&gt',
          '\n': '<br>',
          '"': '"'
        };

        return charsToReplace[tag] || tag;
      });
    }

    var postInfo = function (post) {
      return $.parseHTML(
        '<a \
          class="list-group-item" \
          data-toggle="collapse" \
          href="#collapse-example-'+post.id+'" \
          role="button" aria-expanded="false" \
          aria-controls="collapse-example-'+post.id+'"> \
          '+post.title+'\
        </a> \
        <div class="collapse" id="collapse-example-'+post.id+'"> \
          <div class="sponsor-content"> \
            <div class="text-center"> \
              '+getHtmlStrOfImgs(post.attachedfile_set)+' \
            </div> \
            <div> \
              <p>'+escapeHTML(post.content)+'</p> \
            </div>'+postFunc(post)+' \
          </div> \
        </div>'
      )
    };

    var postFunc = function (post) {
      post.csrf = $('input[name*="csrfmiddlewaretoken"]').val();
      return window.format(' \
        <div id="post-func-{id}" class="text-center"> \
          <div> \
            <div class="pull-right"> \
              <a href="{absolute_url}/edit/" class="btn btn-sm btn-default">수정</a> \
              <a href="#" class="btn btn-sm btn-default" data-toggle="modal" data-target="#delete-modal-{id}">삭제</a> \
            </div> \
          </div> \
          <div id="delete-modal-{id}" class="modal fade" tabindex="-1"> \
            <div class="modal-dialog"> \
              <div class="modal-content"> \
                <div class="modal-header"> \
                  <button type="button" class="close" data-dismiss="modal">&times;</button> \
                  <h4 class="modal-title" id="myModalLabel-{id}">삭제</h4> \
                </div> \
                <div class="modal-body"> \
                  <p>게시글을 정말 삭제할까요?</p> \
                </div> \
                <form class="modal-footer" method="post" action="{absolute_url}/delete/"> \
                  <input type="hidden" name="csrfmiddlewaretoken" value="{csrf}"> \
                  <button type="button" class="btn btn-default" data-dismiss="modal">취소</button> \
                  <button type="submit" class="btn btn-danger">삭제</button> \
                </form> \
              </div> \
            </div> \
          </div> \
        </div> \
      ', post);
    };

    var drawLoadedSponsorPosts = function (sponsorPosts) {
      sponsorPosts.forEach(function (post) {
          $('#sponsor-list').append(postInfo(post));
      });
    };

    var getParameterByName = function(name) {
      url = window.location.href;
      name = name.replace(/[\[\]]/g, "\\$&");
      var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
          results = regex.exec(url);
      if (!results) return null;
      if (!results[2]) return '';
      return decodeURIComponent(results[2].replace(/\+/g, " "));
    }

    var isLoading = false;
    var numLoadedSponsorPosts = $("a[href*='#collapse-example-']").length;
    var numTotalSponsorPosts = -1;
    var search = getParameterByName('s');

    document.addEventListener('scroll', function (event) {
      var scrollHeight = $(document).height();
      var scrollPosition = $(window).height() + $(window).scrollTop();

      if ((scrollHeight - scrollPosition) / scrollHeight === 0
          && !isLoading
          && (numLoadedSponsorPosts < numTotalSponsorPosts || numTotalSponsorPosts === -1)) {
        // when scroll to bottom of the page
        // load more posts
        isLoading = true;
        var requestUrl = '/api/posts?role=SPONSOR&offset=' + String(numLoadedSponsorPosts)
        if (search !== null && search !== '') {
          requestUrl += '&search=' + search;
        }
        $.ajax({
            url: requestUrl,
            type: 'GET',
        })
        .done(function(data) {
          numTotalSponsorPosts = data.count;
          drawLoadedSponsorPosts(data.results);
          numLoadedSponsorPosts = $("a[href*='#collapse-example-']").length;
          // draw on html
        }).fail(function(e) {
            alert('데이터 로드에 실패했습니다.');
        }).always(function() {
          isLoading = false;
        });
      }
      
    }, true /*Capture event*/);
  }
});