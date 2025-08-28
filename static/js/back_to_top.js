(() => {
  'use strict';
  const ID = 'backToTop';
  const btn = document.getElementById(ID);
  if (!btn) return;

  const THRESHOLD_DESKTOP = 300;
  const THRESHOLD_MOBILE = 200;
  const GAP = 16; // gap between chat FAB and this button

  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function isMobileWidth() {
    return window.innerWidth <= 768;
  }

  function getThreshold() {
    return (window.innerWidth <= 768) ? THRESHOLD_MOBILE : THRESHOLD_DESKTOP;
  }

  function updateVisibility() {
    const scrollY = window.scrollY || window.pageYOffset;
    const thr = getThreshold();
    if (scrollY > thr) {
      btn.classList.add('is-visible');
    } else {
      btn.classList.remove('is-visible');
    }
  }

  function adjustPositionForChat() {
    // try known chat selectors
    const chat = document.querySelector('#chatFab, .cw-btn, .contact-widget, [data-role="chat-fab"], .chat-fab');
    let bottom = 88; // default
    if (window.innerWidth <= 375) bottom = 80;
    if (chat) {
      const rect = chat.getBoundingClientRect();
      // chat is fixed relative to viewport; compute its height
      const chatHeight = rect.height || 56;
      bottom = (window.innerHeight - rect.top) + GAP; // distance from bottom
      // clamp minimal
      if (bottom < 64) bottom = 64;
    }
    btn.style.bottom = `${bottom}px`;
  }

  function avoidFooterOverlap() {
    // if footer exists, and button would overlap it, lift it up by overlap + 16px
    const footer = document.querySelector('footer, .site-footer, #footer');
    if (!footer) return;
    const footerRect = footer.getBoundingClientRect();
    const btnRect = btn.getBoundingClientRect();
    const overlap = (btnRect.bottom) - footerRect.top;
    if (overlap > -16) {
      // lift by overlap + 16
      const currentBottom = parseInt(getComputedStyle(btn).bottom, 10) || 88;
      btn.style.bottom = `${currentBottom + overlap + 16}px`;
    }
  }

  function onClick() {
    if (prefersReduced) window.scrollTo(0, 0);
    else window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  btn.addEventListener('click', onClick);
  btn.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ' || e.key === 'Spacebar') {
      e.preventDefault();
      onClick();
    }
  });

  const onScrollOrResize = () => {
    updateVisibility();
    adjustPositionForChat();
    avoidFooterOverlap();
  };

  window.addEventListener('scroll', onScrollOrResize, { passive: true });
  window.addEventListener('resize', onScrollOrResize);

  // initial
  setTimeout(onScrollOrResize, 50);
})();
