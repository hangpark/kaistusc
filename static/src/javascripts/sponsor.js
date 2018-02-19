$().ready(function() {
  // this part should work only when board is sponsor
  if (document.getElementById('sponsor-context')) {

    var getListElementTitle = function (post) {
      if (post.is_secret) {
        if (post.is_permitted_to_read) {
          return post.title;
        } else {
          return "_('비밀글입니다.')";
        }
      } else {
        return post.title;
      }
    }

    var getHtmlStrOfImgs = function (fileSet) {
      return fileSet.map(function (elem) {
        return '<img src="' + elem.file +'" alt="사진">'
      }).join();
    }

    var postInfo = function (post) {
      return $.parseHTML(
        '<a \
          class="list-group-item" \
          data-toggle="collapse" \
          href="#collapse-example-'+post.id+'" \
          role="button" aria-expanded="false" \
          aria-controls="collapse-example-'+post.id+'"> \
          '+getListElementTitle(post)+'\
        </a> \
        <div class="collapse" id="collapse-example-'+post.id+'"> \
          <div class="sponsor-content"> \
            <div class="text-center"> \
              '+getHtmlStrOfImgs(post.attachedfile_set)+' \
            </div> \
            <div> \
              <p>'+post.content+'</p> \
            </div> \
          </div> \
        </div>'
      )
    };

    var drawLoadedSponsorPosts = function (sponsorPosts) {
      sponsorPosts.filter(function(post) { return !post.is_deleted })
                  .forEach(function (post) {
                    $('#sponsor-list').append(postInfo(post));
                  });
    };

    var isLoading = false;
    var numSponsorPosts = document.getElementById('sponsor-list').childNodes.length;
    var numSponsorPosts = $("a[href*='#collapse-example-']").length;

    document.addEventListener('scroll', function (event) {
      var scrollHeight = $(document).height();
      var scrollPosition = $(window).height() + $(window).scrollTop();
      if ((scrollHeight - scrollPosition) / scrollHeight === 0 && !isLoading) {
        // when scroll to bottom of the page
        // load more posts
        isLoading = true;
        $.ajax({
            url: '/api/posts?role=SPONSOR&offset=' + String(numSponsorPosts),
            type: 'GET',
        })
        .done(function(data) {
          console.log(data);
          numSponsorPosts += data.results.length;
          drawLoadedSponsorPosts(data.results);
          // draw on html
        }).fail(function(e) {
            alert('데이터 로드에 실패했습니다.');
            console.log(e);
        }).always(function() {
          isLoading = false;
        });
      }
      
    }, true /*Capture event*/);
  }
});