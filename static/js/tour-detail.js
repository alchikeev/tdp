(function(){
  var bar = document.getElementById('tCtaBar');
  if (!bar) return;

  var header = document.querySelector('.header');
  var anchor = document.getElementById('tCtaAnchor');
  var contentStart = document.getElementById('contentStart');
  
  // Синхронизируем с логикой прокрутки из common.js
  var SCROLL_THRESHOLD = 127; // точно как в common.js
  var HEADER_HEIGHT_NORMAL = 148; // из CSS
  var HEADER_HEIGHT_SCROLLED = 90; // из CSS
  
  var barHeight = 0;
  var isFixed = false;
  
  function getCurrentHeaderHeight() {
    var scrollY = window.scrollY || document.documentElement.scrollTop;
    return scrollY > SCROLL_THRESHOLD ? HEADER_HEIGHT_SCROLLED : HEADER_HEIGHT_NORMAL;
  }
  
  function calculatePositions() {
    barHeight = bar.offsetHeight;
    console.log('Bar height:', barHeight);
  }

  function updateAnchor(){
    if (!anchor) return;
    if (isFixed && bar.classList.contains('t-cta-bar--top')) {
      anchor.style.height = (barHeight + 6) + 'px';
    } else {
      anchor.style.height = '0px';
    }
  }

  function onScroll(){
    var scrollY = window.scrollY || document.documentElement.scrollTop;
    var currentHeaderHeight = getCurrentHeaderHeight();
    
    // Рассчитываем, когда блок должен прилипнуть к шапке
    // Это происходит когда верх блока достигает нижней части шапки
    var barRect = bar.getBoundingClientRect();
    var shouldStick = barRect.top <= currentHeaderHeight;
    
    if (shouldStick && scrollY > 0) {
      // Блок достиг шапки - прилипает к ней
      if (!isFixed) {
        isFixed = true;
        bar.classList.add('t-cta-bar--top');
        bar.style.setProperty('--cta-top', currentHeaderHeight + 'px');
        updateAnchor();
        console.log('Блок прилип к шапке');
      } else {
        // Обновляем позицию при изменении высоты шапки
        bar.style.setProperty('--cta-top', currentHeaderHeight + 'px');
      }
    } else {
      // Блок в нормальном потоке документа
      if (isFixed) {
        isFixed = false;
        bar.classList.remove('t-cta-bar--top');
        bar.style.removeProperty('--cta-top');
        updateAnchor();
        console.log('Блок вернулся в нормальный поток');
      }
    }
  }

  // Дебаунсинг для resize события
  var resizeTimeout;
  function onResize() {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(function() {
      calculatePositions();
      onScroll();
    }, 100);
  }

  // Event listeners
  window.addEventListener('scroll', onScroll, {passive:true});
  window.addEventListener('load', function() {
    calculatePositions();
    onScroll();
  });
  window.addEventListener('resize', onResize);
  
  // Инициализация
  calculatePositions();
  onScroll();
})();