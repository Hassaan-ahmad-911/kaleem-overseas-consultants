document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('storyModal');
  const video = document.getElementById('storyModalVideo');
  const title = document.getElementById('storyModalTitle');

  if (!modal || !video || !title) return;

  const openModal = (src, clientName) => {
    title.textContent = clientName;
    video.src = src;
    modal.hidden = false;
    document.body.style.overflow = 'hidden';
    video.play().catch(() => {});
  };

  const closeModal = () => {
    video.pause();
    video.removeAttribute('src');
    video.load();
    modal.hidden = true;
    document.body.style.overflow = '';
  };

  document.querySelectorAll('[data-story-open]').forEach((button) => {
    button.addEventListener('click', () => {
      openModal(button.dataset.videoSrc, button.dataset.storyTitle || 'Success Story');
    });
  });

  document.querySelectorAll('[data-story-close]').forEach((element) => {
    element.addEventListener('click', closeModal);
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !modal.hidden) {
      closeModal();
    }
  });
});
