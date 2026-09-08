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

const DEFAULT_INTERVAL_MS = 8000;

// Default fade-out duration (ms) before the text is swapped. Overridable per
// rotator via the `data-quote-fade` attribute.
const DEFAULT_FADE_MS = 300;

// Read the users' OS level preference for reduced motion.
// If true, we don't use fade animation, and we start paused.
const prefersReducedMotion =
  window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

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

  const counterEl = rotator.querySelector('[data-quote-counter]');
  const currentEl = rotator.querySelector('[data-quote-current]');
  const totalEl = rotator.querySelector('[data-quote-total]');
  const dotsEl = rotator.querySelector('[data-quote-dots]');

  const nextBtn = rotator.querySelector('[data-quote-next]');

  // Indicator options (independent)
  const useDots = rotator.dataset.showDotIndicators === 'true';
  const useCounter = rotator.dataset.showCounter !== 'false';

  const interval = parseInt(rotator.dataset.quoteInterval, 10) || DEFAULT_INTERVAL_MS;
  const fadeMs = parseInt(rotator.dataset.quoteFade, 10) || DEFAULT_FADE_MS;

  let current = 0;
  let timer = null;
  let dots = [];
  let fadeTimer = null;

  // Set the CSS fade duration variable so the animation remains in sync.
  blockEl.style.setProperty('--quote-fade-ms', fadeMs + 'ms');

  // Reserve height for the tallest quote so the block never resizes as quotes
  // rotate (which would make the controls below jump around). We do this by
  // stacking a hidden copy of every quote in the same grid cell as the live
  // one; the copies are invisible but still take up space, so the block ends up
  // exactly as tall as the longest quote.
  buildSizers();

  // Build one hidden "sizer" copy of the live layer per quote. They share the
  // live layer's grid cell (see quote-widget.scss), so the block reserves the
  // height of the tallest quote. The copies are marked `.is-sizer`
  // (visibility:hidden) and stripped of the widget's data hooks so they're
  // never targeted, shown, or read by assistive tech.
  function buildSizers() {
    const liveLayer = rotator.querySelector('[data-quote-layer]');
    if (!liveLayer) return;

    quotes.forEach(function(quote) {
      const layer = liveLayer.cloneNode(true);
      layer.classList.add('is-sizer');
      layer.setAttribute('aria-hidden', 'true');
      layer.removeAttribute('data-quote-layer');

      const text = layer.querySelector('[data-quote-text]');
      const cite = layer.querySelector('[data-quote-cite]');
      if (text) {
        text.textContent = '\u201c' + quote.text + '\u201d';
        text.removeAttribute('data-quote-text');
      }
      if (cite) {
        cite.textContent = quote.cite;
        cite.removeAttribute('data-quote-cite');
      }

      blockEl.appendChild(layer);
    });
  }

  function paint() {
    textEl.textContent = '\u201c' + quotes[current].text + '\u201d';
    citeEl.textContent = quotes[current].cite;
    updateIndicators();
  }

  // Reflect the current quote in whichever indicator mode is active.
  function updateIndicators() {
    if (currentEl) {
      currentEl.textContent = current + 1;
    }

    dots.forEach(function(dot, index) {
      const isActive = index === current;
      dot.classList.toggle('is-active', isActive);
      if (isActive) {
        dot.setAttribute('aria-current', 'true');
      } else {
        dot.removeAttribute('aria-current');
      }
    });
  }

  // Build one clickable dot per quote. Clicking jumps to that quote, announces
  // it, and resets the auto-rotation countdown (same as the arrow buttons).
  function buildDots() {
    if (!dotsEl) return;

    dots = quotes.map(function(quote, index) {
      const dot = document.createElement('button');
      dot.type = 'button';
      dot.className = 'quote-stage__dot';
      dot.setAttribute('aria-label', 'Go to quote ' + (index + 1));
      dot.addEventListener('click', function() {
        goTo(index);
        announce();
        resetTimer();
      });
      dotsEl.appendChild(dot);
      return dot;
    });
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

    // Assistive tech only announces a *dynamic* change to a live region. Empty
    // it first, then fill it in a separate frame so the fill registers as a
    // genuine change (per MDN's live-region guidance).
    statusEl.textContent = '';
    requestAnimationFrame(function() {
      statusEl.textContent = message;
    });
  }

  function rotate() {
    // Don't fade if the user prefers reduced motion;
    // just swap the content immediately.
    if (prefersReducedMotion) {
      paint();
      return;
    }

    // Fade out, then swap the content and fade back in after the fade-out
    // duration. We clear the timer first, so rapid clicks simply
    // keep the block faded out and restart the timer -- there's never
    // more than one swap scheduled.
    clearTimeout(fadeTimer);
    blockEl.classList.add('is-fading');
    fadeTimer = setTimeout(function() {
      paint();
      blockEl.classList.remove('is-fading');
    }, fadeMs);
  }

  // Show the quote at the given index, wrapping so any out-of-range index maps
  // back into 0 through length-1. Adding `quotes.length` before the modulo keeps the
  // result positive so index -1 lands on the last quote.
  function goTo(index) {
    current = (index + quotes.length) % quotes.length;
    rotate();
  }

  function next() {
    goTo(current + 1);
  }

  function previous() {
    goTo(current - 1);
  }

  function clearTimer() {
    clearInterval(timer);
    timer = null;
  }

  function play() {
    // Clear any existing timer first so play() can't stack intervals.
    clearTimer();

    timer = setInterval(next, interval);

    rotator.classList.remove('is-paused');

    if (toggleBtn) {
      toggleBtn.setAttribute('aria-label', 'Pause quote rotation');
      toggleBtn.setAttribute('aria-pressed', 'false');
    }
  }

  function stop() {
    clearTimer();

    rotator.classList.add('is-paused');

    if (toggleBtn) {
      toggleBtn.setAttribute('aria-label', 'Play quote rotation');
      toggleBtn.setAttribute('aria-pressed', 'true');
    }
  }

  function isPlaying() {
    return timer !== null;
  }

  // Restart the countdown so the user gets a full interval to read the quote
  // they navigated to before it auto-rotates again.
  function resetTimer() {
    if (isPlaying()) {
      play();
    }
  }

  // A single quote can't rotate, so hide the controls entirely.
  if (quotes.length < 2) {
    if (controlsEl) {
      controlsEl.hidden = true;
    }

    paint();
    return;
  }

  if (totalEl) totalEl.textContent = quotes.length;

  // Set up each indicator
  if (useDots) {
    buildDots();
  } else {
    if (dotsEl) {
      dotsEl.hidden = true;
    }
  }

  if (!useCounter && counterEl) {
    counterEl.hidden = true;
  }

  if (prevBtn) {
    prevBtn.addEventListener('click', function() {
      previous();
      announce();
      resetTimer();
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', function() {
      next();
      announce();
      resetTimer();
    });
  }

  if (toggleBtn) {
    toggleBtn.addEventListener('click', function() {
      isPlaying() ? stop() : play();
    });
  }

  paint();

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
