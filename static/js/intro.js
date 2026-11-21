document.addEventListener('DOMContentLoaded', () => {
  const root = document.documentElement;
  const intro = document.getElementById('siteIntro');
  if (!intro) return;

  if (!root.classList.contains('show-intro')) {
    intro.remove();
    return;
  }

  try {
    sessionStorage.setItem('kocIntroSeen', '1');
  } catch (error) {
    // Storage blocked (private mode etc.): the intro simply plays again next time.
  }

  const flightMs = 2400;
  let finished = false;

  const finish = () => {
    if (finished) return;
    finished = true;
    intro.classList.add('is-leaving');
    // Let the page's own entrance animations start while the intro fades out.
    document.dispatchEvent(new CustomEvent('intro:done'));
    window.setTimeout(() => {
      intro.remove();
      root.classList.remove('show-intro');
    }, 700);
  };

  // Plane and contrail share one clock so the trail always ends exactly at the plane.
  const flights = Array.from(intro.querySelectorAll('.site-intro__flight'))
    .filter((svg) => svg.getBoundingClientRect().width > 0)
    .map((svg) => ({
      path: svg.querySelector('.site-intro__trail'),
      reveal: svg.querySelector('.site-intro__trail-reveal'),
      plane: svg.querySelector('.site-intro__plane'),
    }))
    .filter(({ path, reveal, plane }) => path && reveal && plane)
    .map((flight) => ({ ...flight, length: flight.path.getTotalLength() }));

  const easeInOutCubic = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  const start = performance.now();

  const fly = (now) => {
    const progress = Math.min((now - start) / flightMs, 1);
    const eased = easeInOutCubic(progress);

    flights.forEach(({ path, reveal, plane, length }) => {
      const distance = eased * length;
      const point = path.getPointAtLength(distance);
      const ahead = path.getPointAtLength(Math.min(distance + 2, length));
      const behind = path.getPointAtLength(Math.max(distance - 2, 0));
      const angle = (Math.atan2(ahead.y - behind.y, ahead.x - behind.x) * 180) / Math.PI;
      plane.setAttribute('transform', `translate(${point.x} ${point.y}) rotate(${angle})`);
      reveal.style.strokeDashoffset = String(1 - eased);
    });

    if (progress < 1 && !finished) window.requestAnimationFrame(fly);
  };

  fly(start);
  intro.classList.add('is-playing');
  window.requestAnimationFrame(fly);

  window.setTimeout(finish, flightMs + 300);
  intro.addEventListener('click', finish);
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' || event.key === 'Enter' || event.key === ' ') finish();
  });
});
