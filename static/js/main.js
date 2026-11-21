document.addEventListener('DOMContentLoaded', () => {
  const nav = document.querySelector('.site-navbar');
  const revealItems = document.querySelectorAll('.reveal');
  const megaDropdown = document.querySelector('.visa-mega-dropdown');

  const onScroll = () => {
    if (!nav) return;
    nav.classList.toggle('scrolled', window.scrollY > 12);
  };

  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  if (megaDropdown && window.matchMedia('(min-width: 992px)').matches) {
    const toggle = megaDropdown.querySelector('[data-bs-toggle="dropdown"]');
    if (toggle && window.bootstrap && window.bootstrap.Dropdown) {
      const dropdown = window.bootstrap.Dropdown.getOrCreateInstance(toggle, { autoClose: 'outside' });
      let hideTimer;

      megaDropdown.addEventListener('mouseenter', () => {
        clearTimeout(hideTimer);
        dropdown.show();
      });

      megaDropdown.addEventListener('mouseleave', () => {
        hideTimer = window.setTimeout(() => dropdown.hide(), 180);
      });
    }
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
});
