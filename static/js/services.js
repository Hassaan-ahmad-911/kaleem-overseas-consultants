document.addEventListener('DOMContentLoaded', () => {
  const revealItems = document.querySelectorAll('.services-reveal');
  const heroSection = document.querySelector('.services-hero');
  const heroGlow = document.querySelector('.services-hero-bg');

  if ('IntersectionObserver' in window && revealItems.length) {
    const observer = new IntersectionObserver((entries, observerInstance) => {
      entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
          const delay = index * 80;
          entry.target.style.transitionDelay = `${delay}ms`;
          entry.target.classList.add('is-visible');
          observerInstance.unobserve(entry.target);
        }
      });
    }, { threshold: 0.16, rootMargin: '0px 0px -20px 0px' });

    revealItems.forEach((item) => observer.observe(item));
  } else {
    revealItems.forEach((item) => item.classList.add('is-visible'));
  }

  if (heroSection && heroGlow) {
    heroSection.addEventListener('mousemove', (event) => {
      const rect = heroSection.getBoundingClientRect();
      const x = ((event.clientX - rect.left) / rect.width - 0.5) * 18;
      const y = ((event.clientY - rect.top) / rect.height - 0.5) * 18;
      heroGlow.style.transform = `translate3d(${x}px, ${y}px, 0)`;
    });

    heroSection.addEventListener('mouseleave', () => {
      heroGlow.style.transform = 'translate3d(0, 0, 0)';
    });
  }
});