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

  if ('IntersectionObserver' in window && revealItems.length) {
    const observer = new IntersectionObserver((entries, observerInstance) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observerInstance.unobserve(entry.target);
        }
      });
    }, { threshold: 0.18, rootMargin: '0px 0px -40px 0px' });

    revealItems.forEach((item) => observer.observe(item));
  } else {
    revealItems.forEach((item) => item.classList.add('is-visible'));
  }

  document.querySelectorAll('form').forEach((form) => {
    form.addEventListener('submit', () => {
      const submitButton = form.querySelector('button[type="submit"]');
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.dataset.originalText = submitButton.textContent;
        submitButton.textContent = 'Please wait...';
      }
    });
  });
});
