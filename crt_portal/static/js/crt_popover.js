/**
 * crt-popover — minimal, accessible click-to-open popover (USWDS-style).
 *
 * Markup contract (each popover instance):
 *
 *   <span class="crt-popover">
 *     <button class="crt-popover__trigger"
 *             type="button"
 *             id="UNIQUE-TRIGGER-ID"
 *             aria-controls="UNIQUE-CONTENT-ID"
 *             aria-expanded="false">
 *       …trigger text or icon…
 *     </button>
 *     <span class="crt-popover__content" id="UNIQUE-CONTENT-ID" hidden>
 *       …popover body…
 *     </span>
 *   </span>
 *
 * Requirements / gotchas:
 *
 *  1. IDs MUST be unique per instance. The trigger finds its content via
 *     document.getElementById(aria-controls), and HTML forbids duplicate IDs
 *     on a page. If you have two popovers, use e.g. "obs-trigger" / "obs-pop"
 *     and "obs-trigger-2" / "obs-pop-2". Do NOT reuse an ID.
 *
 *  2. The trigger MUST be type="button". A bare <button> defaults to
 *     type="submit", which can submit an ancestor <form> and cause a page
 *     jump/reload instead of opening the popover.
 *
 *  3. Both the trigger and the content span MUST live inside the
 *     .crt-popover wrapper. The content is position:absolute relative to
 *     that wrapper, so it anchors over the trigger only if they share a
 *     common positioning parent.
 *
 *  4. The content MUST start with the `hidden` attribute. The JS toggles
 *     .hidden, not a class.
 *
 * Behaviour:
 *  - Opens on click of the trigger (NOT hover — accessibility requirement).
 *  - One popover open at a time: opening one closes any other open instance.
 *  - Dismisses on: Escape, click outside the popover, or re-clicking the
 *    same trigger.
 *  - Clicking inside an open popover does NOT dismiss it.
 *  - Scrolls into view only if the opened popover overflows the viewport.
 *  - On close, focus returns to the trigger.
 */
(() => {
  const close = trigger => {
    const content = document.getElementById(trigger.getAttribute('aria-controls'));
    if (!content) return;
    content.hidden = true;
    trigger.setAttribute('aria-expanded', 'false');
    trigger.focus();
  };

  const open = trigger => {
    // Close any other open popover first (single-open invariant).
    document.querySelectorAll('.crt-popover__trigger[aria-expanded="true"]').forEach(close);
    const content = document.getElementById(trigger.getAttribute('aria-controls'));
    if (!content) return;
    content.hidden = false;
    trigger.setAttribute('aria-expanded', 'true');

    // Only scroll if the popover actually overflows the viewport.
    // (block:'nearest' is relative to the nearest scrollable ancestor, which
    // can be far up the tree — so we gate it on a real overflow instead.)
    const rect = content.getBoundingClientRect();
    const margin = 8;
    if (rect.top < margin || rect.bottom > window.innerHeight - margin) {
      content.scrollIntoView({ block: 'nearest' });
    }
  };

  document.addEventListener('click', e => {
    const trigger = e.target.closest('.crt-popover__trigger');
    if (trigger) {
      e.preventDefault();
      trigger.getAttribute('aria-expanded') === 'true' ? close(trigger) : open(trigger);
      return;
    }
    if (e.target.closest('.crt-popover__content')) return; // clicked inside, keep open
    document.querySelectorAll('.crt-popover__trigger[aria-expanded="true"]').forEach(close);
  });

  document.addEventListener('keydown', e => {
    if (e.key !== 'Escape') return;
    document.querySelectorAll('.crt-popover__trigger[aria-expanded="true"]').forEach(close);
  });
})();
