document.addEventListener('DOMContentLoaded', () => {
  const nav = document.querySelector('.site-navbar');
  const revealItems = document.querySelectorAll('.reveal');
  const megaDropdown = document.querySelector('.visa-mega-dropdown');

  // Passive scroll listener that only touches the DOM when the "scrolled" state actually changes.
  let navScrolled = null;
  const onScroll = () => {
    if (!nav) return;
    const scrolled = window.scrollY > 12;
    if (scrolled === navScrolled) return;
    navScrolled = scrolled;
    nav.classList.toggle('scrolled', scrolled);
  };

  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  const desktopNav = window.matchMedia('(min-width: 992px)');
  const megaToggle = megaDropdown && megaDropdown.querySelector('[data-bs-toggle="dropdown"]');

  // Desktop only: open the Visa mega-menu on hover (checked on every hover, so resizing is handled too).
  if (megaToggle && window.bootstrap && window.bootstrap.Dropdown) {
    const dropdown = window.bootstrap.Dropdown.getOrCreateInstance(megaToggle, { autoClose: 'outside' });
    let hideTimer;

    megaDropdown.addEventListener('mouseenter', () => {
      if (!desktopNav.matches) return;
      clearTimeout(hideTimer);
      dropdown.show();
    });

    megaDropdown.addEventListener('mouseleave', () => {
      if (!desktopNav.matches) return;
      hideTimer = window.setTimeout(() => dropdown.hide(), 180);
    });
  }

  // Mobile menu: tapping a link closes the menu, and closing the menu also folds the Visa list.
  const mainNav = document.getElementById('mainNav');
  if (mainNav && window.bootstrap && window.bootstrap.Collapse) {
    mainNav.addEventListener('click', (event) => {
      const link = event.target.closest('a[href]');
      if (!link || link.hasAttribute('data-bs-toggle') || !mainNav.classList.contains('show')) return;
      window.bootstrap.Collapse.getOrCreateInstance(mainNav, { toggle: false }).hide();
    });

    mainNav.addEventListener('hide.bs.collapse', (event) => {
      if (event.target !== mainNav || !megaToggle || !window.bootstrap.Dropdown) return;
      window.bootstrap.Dropdown.getInstance(megaToggle)?.hide();
    });
  }

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Stagger siblings that reveal together (e.g. cards in the same row).
  revealItems.forEach((item) => {
    if (item.style.getPropertyValue('--reveal-delay')) return;
    const siblings = Array.from(item.parentElement.children).filter((el) => el.classList.contains('reveal'));
    const index = Math.min(siblings.indexOf(item), 5);
    if (index > 0) item.style.setProperty('--reveal-delay', `${index * 0.09}s`);
  });

  const countUp = (element) => {
    const target = Number(element.dataset.countTo);
    const suffix = element.dataset.countSuffix || '';
    if (Number.isNaN(target) || prefersReducedMotion) {
      element.textContent = `${element.dataset.countTo}${suffix}`;
      return;
    }
    const duration = 1400;
    const start = performance.now();
    const step = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      element.textContent = `${Math.round(target * eased)}${suffix}`;
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };

  const counters = document.querySelectorAll('[data-count-to]');

  const startReveals = () => {
    if ('IntersectionObserver' in window && !prefersReducedMotion) {
      const observer = new IntersectionObserver((entries, observerInstance) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observerInstance.unobserve(entry.target);
          }
        });
      }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

      revealItems.forEach((item) => observer.observe(item));

      const counterObserver = new IntersectionObserver((entries, observerInstance) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            countUp(entry.target);
            observerInstance.unobserve(entry.target);
          }
        });
      }, { threshold: 0.6 });

      counters.forEach((counter) => counterObserver.observe(counter));
    } else {
      revealItems.forEach((item) => item.classList.add('is-visible'));
      counters.forEach(countUp);
    }
  };

  // While the opening intro is playing, hold the page's entrance animations until it finishes.
  if (document.documentElement.classList.contains('show-intro')) {
    let started = false;
    const startOnce = () => {
      if (started) return;
      started = true;
      startReveals();
    };
    document.addEventListener('intro:done', startOnce, { once: true });
    window.setTimeout(startOnce, 6000);
  } else {
    startReveals();
  }

  document.querySelectorAll('form').forEach((form) => {
    form.addEventListener('submit', () => {
      const submitButton = form.querySelector('button[type="submit"]');
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.dataset.originalHtml = submitButton.innerHTML;
        submitButton.textContent = 'Please wait...';
      }
    });
  });

  // Restore submit buttons when the page comes back from the browser's back/forward cache.
  window.addEventListener('pageshow', (event) => {
    if (!event.persisted) return;
    document.querySelectorAll('button[type="submit"][data-original-html]').forEach((button) => {
      button.disabled = false;
      button.innerHTML = button.dataset.originalHtml;
    });
  });

  // Offers slider. Bootstrap handles the crossfade and the prev/next/dot controls; rotation is driven by the
  // active dot's 5s progress fill (CSS), so pausing on hover/focus freezes the timer and the bar together.
  const offersElement = document.getElementById('offersCarousel');
  if (offersElement && window.bootstrap && window.bootstrap.Carousel) {
    const offersCarousel = window.bootstrap.Carousel.getOrCreateInstance(offersElement, { interval: false, ride: false, pause: false });
    const isMulti = offersElement.classList.contains('offers-carousel--multi');
    const autoRotate = isMulti && !prefersReducedMotion;
    const activeSlide = () => offersElement.querySelector('.carousel-item.active');
    const hold = (on) => offersElement.classList.toggle('is-holding', on);
    let offersInView = false;
    let refocusSelector = null;

    if (autoRotate) offersElement.classList.add('is-auto');

    const pauseSlideMedia = (slide) => {
      if (!slide) return;
      slide.querySelectorAll('video').forEach((video) => video.pause());
      slide.querySelectorAll('iframe').forEach((frame) => {
        frame.contentWindow?.postMessage(JSON.stringify({ event: 'command', func: 'pauseVideo', args: [] }), '*');
      });
    };

    const playSlideVideo = (slide) => {
      const video = slide && slide.querySelector('video[data-offer-autoplay]');
      if (video && offersInView && !prefersReducedMotion) video.play().catch(() => {});
    };

    offersElement.addEventListener('animationend', (event) => {
      if (event.animationName === 'offerProgress' && autoRotate) offersCarousel.next();
    });

    // Uploaded videos hold the slider until they finish.
    offersElement.querySelectorAll('video').forEach((video) => {
      video.addEventListener('play', () => hold(true));
      video.addEventListener('pause', () => {
        if (!video.ended) hold(false);
      });
      video.addEventListener('ended', () => {
        hold(false);
        if (autoRotate) offersCarousel.next();
      });
    });

    offersElement.addEventListener('slide.bs.carousel', (event) => {
      // Each slide has its own copy of the controls; keep keyboard focus on the same control in the new slide.
      const focused = document.activeElement;
      refocusSelector = null;
      if (focused && offersElement.contains(focused)) {
        if (focused.dataset.bsSlide) refocusSelector = `[data-bs-slide="${focused.dataset.bsSlide}"]`;
        else if (focused.dataset.bsSlideTo !== undefined) refocusSelector = `[data-bs-slide-to="${focused.dataset.bsSlideTo}"]`;
      }
      pauseSlideMedia(activeSlide());
      hold(false);
      // Restart the zoom-in / caption stagger on the incoming slide.
      offersElement.querySelectorAll('.offer-slide.is-entering').forEach((slide) => slide.classList.remove('is-entering'));
      void event.relatedTarget.offsetWidth;
      event.relatedTarget.classList.add('is-entering');
    });

    offersElement.addEventListener('slid.bs.carousel', (event) => {
      if (refocusSelector) event.relatedTarget.querySelector(refocusSelector)?.focus({ preventScroll: true });
      refocusSelector = null;
      playSlideVideo(event.relatedTarget);
    });

    // Clicking into a YouTube player moves focus into its iframe, which blurs this window.
    window.addEventListener('blur', () => {
      const focused = document.activeElement;
      if (focused && focused.tagName === 'IFRAME' && offersElement.contains(focused)) hold(true);
    });

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(([entry]) => {
        offersInView = entry.isIntersecting;
        if (offersInView) playSlideVideo(activeSlide());
        else activeSlide()?.querySelectorAll('video').forEach((video) => video.pause());
      }, { threshold: 0.4 }).observe(offersElement);
    } else {
      offersInView = true;
      playSlideVideo(activeSlide());
    }
  }
});
