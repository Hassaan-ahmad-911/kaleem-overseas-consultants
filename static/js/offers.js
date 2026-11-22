// Live countdowns for offers with a "valid until" date (home slider and Offers page).
// Each [data-ends-at] element holds the absolute deadline as ISO 8601 with offset, so the countdown is
// right for visitors in any timezone. One interval updates every countdown, including those on hidden
// carousel slides, and only the digit text changes so the slider's animations are not disturbed.
document.addEventListener('DOMContentLoaded', () => {
  const DAY_MS = 24 * 60 * 60 * 1000;
  const UNITS = ['days', 'hours', 'minutes', 'seconds'];

  const countdowns = Array.from(document.querySelectorAll('[data-ends-at]'))
    .map((element) => ({
      element,
      endsAt: Date.parse(element.dataset.endsAt),
      digits: Object.fromEntries(UNITS.map((unit) => [unit, element.querySelector(`[data-unit="${unit}"]`)])),
      ended: false,
    }))
    .filter((countdown) => !Number.isNaN(countdown.endsAt));

  if (!countdowns.length) return;

  let timer = null;

  const update = () => {
    const now = Date.now();
    let anyRunning = false;

    countdowns.forEach((countdown) => {
      if (countdown.ended) return;
      const remaining = countdown.endsAt - now;

      if (remaining <= 0) {
        // Stop at zero; the server hides expired offers on the next page load.
        countdown.ended = true;
        countdown.element.classList.remove('is-urgent');
        countdown.element.classList.add('is-ended');
        return;
      }

      anyRunning = true;
      const totalSeconds = Math.floor(remaining / 1000);
      const values = {
        days: Math.floor(totalSeconds / 86400),
        hours: Math.floor((totalSeconds % 86400) / 3600),
        minutes: Math.floor((totalSeconds % 3600) / 60),
        seconds: totalSeconds % 60,
      };
      UNITS.forEach((unit) => {
        const node = countdown.digits[unit];
        const text = String(values[unit]).padStart(2, '0');
        if (node && node.textContent !== text) node.textContent = text;
      });
      countdown.element.classList.toggle('is-urgent', remaining < DAY_MS);
    });

    if (!anyRunning && timer) {
      clearInterval(timer);
      timer = null;
    }
    return anyRunning;
  };

  const running = update();
  countdowns.forEach(({ element }) => {
    element.hidden = false;
  });
  if (running) timer = setInterval(update, 1000);
});
