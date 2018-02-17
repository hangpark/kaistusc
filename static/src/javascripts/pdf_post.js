$(document).ready(function() {

  var pdfContext = document.getElementById('pdf-context');
  var url = pdfContext === null ? null : pdfContext.getAttribute('data-url');

  var currentPdf;

  function renderPage(pageIndex) {
    if (pageIndex > currentPdf.numPages || pageIndex < 1) {
      return;
    }
    currentPdf.getPage(pageIndex)
      .then(function(page) {

        var canvas = pageIndex % 2 === 1 ? document.getElementById('the-canvas') : document.getElementById('the-canvas-2');

        var canvasContainer = document.getElementById('pdf-canvas-container')
        var canvasWidth = canvasContainer.offsetWidth / 2;
        
        var viewport = page.getViewport(canvasWidth / page.getViewport(1.0).width);

        var context = canvas.getContext('2d');

        canvas.height = viewport.height;
        canvas.width = viewport.width;
        
        var renderContext = {
          canvasContext: context,
          viewport: viewport
        };
      
        page.render(renderContext);
      })
      .catch(function (e) {
        // render error page.
        $("#pdf-success").hide();
        $("#pdf-fail").show();
      });
  }

  function goToPage(pageIndex) {
    pageIndex = pageIndex % 2 === 0 ? pageIndex-1 : pageIndex;
    document.getElementById('pdf-page-num').value = pageIndex;
    renderPage(pageIndex)
    renderPage(pageIndex+1)
  }

  function goToInputPage() {
    var currentPageIndex = Number(document.getElementById('pdf-page-num').value);
    goToPage(currentPageIndex);
  }

  function goToPrevPage() {
    var currentPageIndex = Number(document.getElementById('pdf-page-num').value);
    if (currentPageIndex > 1) {
      goToPage(--currentPageIndex);
    }
  }

  function goToNextPage() {
    var currentPageIndex = Number(document.getElementById('pdf-page-num').value);
    if (currentPageIndex % 2 === 1) {
      currentPageIndex++;
    }
    if (currentPageIndex < currentPdf.numPages) {
      currentPageIndex++;
      goToPage(currentPageIndex);
    }
  }

  // Asynchronous download PDF
  if (url) {
    PDFJS.getDocument(url)
    .then(function(pdf) {
      currentPdf = pdf;
      goToPage(1);
    })
    $('#pdf-prev').on('click', goToPrevPage);
    $('#pdf-next').on('click', goToNextPage);
    $('#pdf-go-to-page').on('click', goToInputPage);
  }

});