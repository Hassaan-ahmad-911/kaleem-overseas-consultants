document.addEventListener('DOMContentLoaded', () => {
  if (typeof AOS !== 'undefined') {
    AOS.init({
      duration: 700,
      once: true,
      offset: 50,
      easing: 'ease-out-cubic',
    });
  }

  const modalElement = document.getElementById('galleryLightbox');
  if (!modalElement) {
    return;
  }

  const modalImage = modalElement.querySelector('[data-gallery-modal-image]');
  const modalTitle = modalElement.querySelector('[data-gallery-modal-title]');
  const modalCountry = modalElement.querySelector('[data-gallery-modal-country]');
  const modalVisa = modalElement.querySelector('[data-gallery-modal-visa]');
  const modalCaption = modalElement.querySelector('[data-gallery-modal-caption]');

  modalElement.addEventListener('show.bs.modal', (event) => {
    const trigger = event.relatedTarget;
    if (!trigger) {
      return;
    }

    const image = trigger.getAttribute('data-image');
    const title = trigger.getAttribute('data-title');
    const country = trigger.getAttribute('data-country');
    const visa = trigger.getAttribute('data-visa');
    const caption = trigger.getAttribute('data-caption');

    if (modalImage) {
      modalImage.src = image || '';
      modalImage.alt = title ? `${title} approval image` : 'Gallery image';
    }
    if (modalTitle) modalTitle.textContent = title || '';
    if (modalCountry) modalCountry.textContent = country || '';
    if (modalVisa) modalVisa.textContent = visa || '';
    if (modalCaption) modalCaption.textContent = caption || '';
  });

  modalElement.addEventListener('hidden.bs.modal', () => {
    if (modalImage) {
      modalImage.src = '';
      modalImage.alt = '';
    }
    if (modalTitle) modalTitle.textContent = '';
    if (modalCountry) modalCountry.textContent = '';
    if (modalVisa) modalVisa.textContent = '';
    if (modalCaption) modalCaption.textContent = '';
  });
});