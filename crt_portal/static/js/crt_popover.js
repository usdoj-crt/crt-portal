(() => {
  const close = (trigger) => {
    const content = document.getElementById(trigger.getAttribute('aria-controls'));
    content.hidden = true;
    trigger.setAttribute('aria-expanded', 'false');
    trigger.focus();
  };

  const open = (trigger) => {
    document.querySelectorAll('.crt-popover__trigger[aria-expanded="true"]').forEach(close);
    const content = document.getElementById(trigger.getAttribute('aria-controls'));
    content.hidden = false;
    trigger.setAttribute('aria-expanded', 'true');
    // Make sure the popover is visible if the trigger was near a viewport edge
    content.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  };

  document.addEventListener('click', (e) => {
    const trigger = e.target.closest('.crt-popover__trigger');
    if (trigger) {
      e.preventDefault();
      trigger.getAttribute('aria-expanded') === 'true' ? close(trigger) : open(trigger);
      return;
    }
    if (e.target.closest('.crt-popover__content')) return; // clicked inside, keep open
    document.querySelectorAll('.crt-popover__trigger[aria-expanded="true"]').forEach(close);
  });

  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    document.querySelectorAll('.crt-popover__trigger[aria-expanded="true"]').forEach(close);
  });
})();
