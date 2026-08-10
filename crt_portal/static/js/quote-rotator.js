// Quote rotator widget
//
// Rotates through a list of quotes inside a `[data-quote-rotator]` element,
// showing one at a time with a fade. Quotes are read from a JSON `<script>`
// referenced by the widget's `data-quotes-id` attribute, in the form:
//   [{ "text": "...", "cite": "..." }, ...]
//
// Controls (optional, matched by data-attribute within the widget):
//   [data-quote-prev]    previous quote
//   [data-quote-next]    next quote
//   [data-quote-toggle]  play/pause auto-rotation
//   [data-quote-status]  visually-hidden live region for screen readers
//
// Accessibility notes:
//   - The rotating text is NOT a live region; announcing every automatic
//     rotation would constantly interrupt screen readers. Instead, a separate
//     `[data-quote-status]` live region is updated only when the *user*
//     navigates (prev/next), announcing e.g. "Quote 2 of 4: ...".
//   - Users who prefer reduced motion get no auto-rotation and no fade; they
//     step through manually with the arrows.

const QUOTE_FADE_MS = 300;
const DEFAULT_INTERVAL_MS = 8000;

// Read the users' OS level preference for reduced motion.
// If true, we don't use fade animation, and we start paused.
const prefersReducedMotion =
  window.matchMedia &&
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function readQuotes(quotesId) {
  const dataEl = document.getElementById(quotesId);
  if (!dataEl) return [];
  try {
    const quotes = JSON.parse(dataEl.textContent);
    return Array.isArray(quotes) ? quotes : [];
  } catch (error) {
    console.error(`QuoteRotator: could not parse quotes from "#${quotesId}".`, error);
    return [];
  }
}

function initQuoteRotator(rotator) {
  const quotes = readQuotes(rotator.dataset.quotesId);
  if (!quotes.length) return;

  const blockEl = rotator.querySelector('[data-quote-block]');
  const textEl = rotator.querySelector('[data-quote-text]');
  const citeEl = rotator.querySelector('[data-quote-cite]');
  const statusEl = rotator.querySelector('[data-quote-status]');

  const controlsEl = rotator.querySelector('[data-quote-controls]');
  const toggleBtn = rotator.querySelector('[data-quote-toggle]');
  const prevBtn = rotator.querySelector('[data-quote-prev]');
  const nextBtn = rotator.querySelector('[data-quote-next]');

  const interval = parseInt(rotator.dataset.quoteInterval, 10) || DEFAULT_INTERVAL_MS;

  let current = 0;
  let timer = null;

  function paint(userInitiated) {
    textEl.textContent = '\u201c' + quotes[current].text + '\u201d';
    citeEl.textContent = quotes[current].cite;

    rotator.dispatchEvent(
      new CustomEvent('quote-rotator-change', {
        detail: {
          index: current,
          quote: quotes[current],
          userInitiated: !!userInitiated,
        },
      })
    );
  }

  // Announce the current quote to screen readers. Called only on user
  // navigation, never on the automatic timer.
  //
  // Clearing the region before setting it forces assistive tech to register a
  // fresh change; setting text in a single step (or setting identical text)
  // can otherwise be missed.
  function announce() {
    if (!statusEl) {
      return;
    }
    const position = `Quote ${current + 1} of ${quotes.length}`;
    const message = `${position}: ${quotes[current].text} ${quotes[current].cite}`;
    statusEl.textContent = message;
  }

  function rotate(userInitiated) {
    // Don't fade if the user prefers reduced motion;
    // just swap the content immediately.
    if (prefersReducedMotion) {
      paint(userInitiated);
      return;
    }

    // Fade out, swap content, fade back in.
    blockEl.classList.add('is-fading');
    setTimeout(function () {
      paint(userInitiated);
      blockEl.classList.remove('is-fading');
    }, QUOTE_FADE_MS);
  }

  // Show the quote at the given index, wrapping so any out-of-range index maps
  // back into 0..length-1. Adding `quotes.length` before the modulo keeps the
  // result positive so index -1 lands on the last quote.
  function goTo(index, userInitiated) {
    current = (index + quotes.length) % quotes.length;
    rotate(userInitiated);
  }

  function next(userInitiated) {
    goTo(current + 1, userInitiated);
  }

  function previous(userInitiated) {
    goTo(current - 1, userInitiated);
  }

  function clearTimer() {
    clearInterval(timer);
    timer = null;
  }

  function play() {
    // Clear any existing timer first so play() can't stack intervals.
    clearTimer();

    timer = setInterval(function () {
      next(false);
    }, interval);

    rotator.classList.remove('is-paused');

    if (toggleBtn) {
      toggleBtn.setAttribute('aria-label', 'Pause quote rotation');
    }
  }

  function stop() {
    clearTimer();

    rotator.classList.add('is-paused');

    if (toggleBtn) {
      toggleBtn.setAttribute('aria-label', 'Play quote rotation');
    }
  }

  function isPlaying() {
    return timer !== null;
  }

  // A single quote can't rotate, so hide the controls entirely.
  if (quotes.length < 2) {
    if (controlsEl) {
      controlsEl.hidden = true;
    }

    paint(false);
    return;
  }

  if (prevBtn) {
    prevBtn.addEventListener('click', function () {
      previous(true);
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', function () {
      next(true);
    });
  }

  if (toggleBtn) {
    toggleBtn.addEventListener('click', function () {
      isPlaying() ? stop() : play();
    });
  }

  rotator.addEventListener('quote-rotator-change', function (event) {
    console.log("Quote changed...");
    if (event.detail.userInitiated) {
      console.log("User initiated quote change, announcing...");
      announce();
      // Reset the timer so the user has time to read the new quote before it
      // auto-rotates again.
      if (isPlaying()) {
        play();
      }
    }
  });

  paint(false);

  // Respect reduced-motion: don't auto-rotate. Leave the widget in the paused
  // state so the toggle offers "Play" if the user wants motion.
  if (prefersReducedMotion) {
    stop();
  } else {
    play();
  }
}

function initAllQuoteRotators() {
  document.querySelectorAll('[data-quote-rotator]').forEach(initQuoteRotator);
}

// Boot once the DOM is ready. This lets the script load from the <head>
// (before the widget markup exists) as well as from the end of the <body>.
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initAllQuoteRotators);
} else {
  initAllQuoteRotators();
}
