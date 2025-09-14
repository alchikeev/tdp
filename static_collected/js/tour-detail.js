(function(){
  var bar = document.getElementById('tCtaBar');
  if (!bar) return;

  var header = document.querySelector('.header');
  var headerInner = document.querySelector('.header_content');
  var anchor = document.getElementById('tCtaAnchor');
  var pinTop = 56; // fallback
  function recalcPinTop(){
    var h = 0;
    if (headerInner) { h = headerInner.getBoundingClientRect().height || 0; }
    if (!h && header) { h = header.getBoundingClientRect().height || 0; }
    if (h) pinTop = h; // else keep previous or fallback
  }
  recalcPinTop();

  // initial state: bottom fixed
  bar.classList.add('t-cta-bar--bottom');
  document.body.style.paddingBottom = (bar.offsetHeight + 8) + 'px';
  // reserve space under header when pinned so content doesn't jump
  function updateAnchor(){
    if (!anchor) return;
    if (bar.classList.contains('t-cta-bar--top')) {
      anchor.style.height = (bar.offsetHeight + 6) + 'px';
    } else {
      anchor.style.height = '0px';
    }
  }

  var lastY = window.scrollY || document.documentElement.scrollTop || 0;

  function onScroll(){
    recalcPinTop();
    var y = window.scrollY || document.documentElement.scrollTop;
    var goingUp = y < lastY;
    var threshold = Math.max(80, pinTop);

    // Desired behavior:
    // - Default: bottom fixed
    // - When user scrolls UP and reaches near top (y <= threshold), dock under header
    // - When scrolling DOWN away from top, return to bottom
    if (goingUp && y <= threshold) {
      bar.classList.remove('t-cta-bar--bottom');
      bar.classList.add('t-cta-bar--top');
      bar.style.setProperty('--cta-top', pinTop + 'px');
    } else if (y > threshold) {
      bar.classList.add('t-cta-bar--bottom');
      bar.classList.remove('t-cta-bar--top');
    }
    updateAnchor();
    lastY = y;
  }

  window.addEventListener('scroll', onScroll, {passive:true});
  window.addEventListener('load', function(){ recalcPinTop(); onScroll(); updateAnchor(); });
  window.addEventListener('resize', function(){ recalcPinTop(); onScroll(); });
})();


