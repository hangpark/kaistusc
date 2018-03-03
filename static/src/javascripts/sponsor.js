$().ready(function() {
  // this part should work only when board is sponsor
  if (document.getElementById('sponsor-context')) {

    var getHtmlStrOfImgs = function (fileSet) {
      return fileSet.map(function (elem) {
        return '<img src="' + elem.file +'" alt="Failed to load photo">'
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
          '+post.title+'\
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