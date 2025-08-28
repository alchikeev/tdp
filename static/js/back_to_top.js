(() => {
  'use strict';
  const ID = 'backToTop';
  const btn = document.getElementById(ID);
  if (!btn) return;

  const THRESHOLD_DESKTOP = 300;
  const THRESHOLD_MOBILE = 200;
  const GAP = 0; // gap between chat FAB and this button

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
    // Mirror chat FAB: detect chat element and place this button on the opposite side
    const chat = document.querySelector('#chatFab, .cw-btn, .contact-widget, [data-role="chat-fab"], .chat-fab');
    let bottom = 88; // default
    let right = 16;
    let sizeW = 48, sizeH = 48;
    if (window.innerWidth <= 375) bottom = 80;
    if (chat) {
      const rect = chat.getBoundingClientRect();
      const chatBottom = window.innerHeight - rect.bottom; // distance from viewport bottom to chat bottom
      // prefer using chat's bottom offset if available
      bottom = chatBottom + GAP;
      // mirror side: if chat is on left half, place this on right; otherwise place on left
      const isLeft = rect.left < (window.innerWidth / 2);
      if (isLeft) {
        right = 16; // keep default right margin
      } else {
        // if chat is on right, position this button on left so they don't overlap
        right = (window.innerWidth - rect.right) + GAP; // use right offset
      }
      // match size to chat
      sizeW = Math.round(rect.width) || sizeW;
      sizeH = Math.round(rect.height) || sizeH;
    }

    btn.style.bottom = `${bottom}px`;
    btn.style.right = `${right}px`;
    btn.style.width = `${sizeW}px`;
    btn.style.height = `${sizeH}px`;
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
  };

  window.addEventListener('scroll', onScrollOrResize, { passive: true });
  window.addEventListener('resize', onScrollOrResize);

  // initial
  setTimeout(onScrollOrResize, 50);
})();
