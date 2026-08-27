// News carousel widget
//
// Enhances each `.news-carousel` on the page with previous/next buttons that
// scroll the rail one card at a time, and keeps those buttons disabled when the
// rail is already at its far-left or far-right end.
//
// The rail itself scrolls and snaps with pure CSS (see news-carousel.css), so
// this script is a progressive enhancement: without JS the cards still scroll
// natively (swipe/wheel/keyboard on the focusable track). The buttons simply
// drive that same native scroll.
//
// Per-carousel hooks (matched within each `.news-carousel`):
//   [data-news-carousel-track]  the scrolling rail (<ul>)
//   [data-news-carousel-prev]   previous button
//   [data-news-carousel-next]   next button
//
// Accessibility notes:
//   - End buttons are `disabled` (not removed from the DOM) so keyboard focus
//     is never yanked away mid-interaction. CSS fades them to opacity:0 so they
//     read as "hidden" visually while staying focus-safe.
//   - Button state is recomputed on native scroll and on resize, so the buttons
//     stay in sync however the user moves the rail.

// Sub-pixel rounding means scrollLeft rarely equals the exact maximum, so we
// treat "within this many px of an end" as being at that end.
const END_TOLERANCE_PX = 36;

function initNewsCarousel(carousel) {
  const track = carousel.querySelector('[data-news-carousel-track]');
  const prevBtn = carousel.querySelector('[data-news-carousel-prev]');
  const nextBtn = carousel.querySelector('[data-news-carousel-next]');

  if (!track) {
    return;
  }

  // Distance to scroll per button press: one card plus the gap between cards.
  // Measured from a real item so it tracks the responsive card width.
  function stepDistance() {
    const item = track.querySelector('.news-carousel__item');
    if (!item) {
      return track.clientWidth;
    }

    const gap = parseFloat(getComputedStyle(track).columnGap) || 0;
    return item.getBoundingClientRect().width + gap;
  }

  function maxScrollLeft() {
    return track.scrollWidth - track.clientWidth;
  }

  // Disable each button when the rail can't scroll further that direction.
  function updateButtons() {
    const atStart = track.scrollLeft <= END_TOLERANCE_PX;
    const atEnd = track.scrollLeft >= maxScrollLeft() - END_TOLERANCE_PX;

    if (prevBtn) {
      prevBtn.disabled = atStart;
    }

    if (nextBtn) {
      nextBtn.disabled = atEnd;
    }

    // Show an edge fade on whichever side has more content to scroll to, as a
    // visual cue that the rail is scrollable. CSS keys off these classes.
    carousel.classList.toggle('news-carousel--has-prev', !atStart);
    carousel.classList.toggle('news-carousel--has-next', !atEnd);
  }

  function scrollByStep(direction) {
    track.scrollBy({ left: direction * stepDistance(), behavior: 'smooth' });
  }

  if (prevBtn) {
    prevBtn.addEventListener('click', function() {
      scrollByStep(-1);
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', function() {
      scrollByStep(1);
    });
  }

  // Keep button state in sync with every way the rail can move.
  track.addEventListener('scroll', updateButtons, { passive: true });
  window.addEventListener('resize', updateButtons);

  // Set the initial state.
  updateButtons();
}

function initAllNewsCarousels() {
  document.querySelectorAll('.news-carousel').forEach(initNewsCarousel);
}

// Boot once the DOM is ready. This lets the script load from the <head>
// (before the widget markup exists) as well as from the end of the <body>.
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initAllNewsCarousels);
} else {
  initAllNewsCarousels();
}
