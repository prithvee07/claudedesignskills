---
name: css-scroll-driven-animations
description: Build scroll-driven animations with native CSS - no JavaScript library. Use when creating scroll progress bars, reveal-on-scroll, parallax, sticky image reveals, or horizontal scroll sections using the CSS scroll-timeline and view-timeline features. Triggers on tasks involving animation-timeline, scroll(), view(), scroll-timeline, view-timeline, animation-range, timeline-scope, or CSS-only scroll animation. Lighter, main-thread-free alternative to GSAP ScrollTrigger or AOS for effects that map element animation to scroll position, with progressive enhancement via @supports.
---

# CSS Scroll-Driven Animations

## Overview

Scroll-driven animations link a CSS `@keyframes` animation to scroll position instead of time, using the native `animation-timeline` property. They run off the main thread, need no JavaScript, and degrade gracefully with `@supports`.

**When to Use This Skill**:
- Scroll progress indicators
- Reveal / fade / slide-in as elements enter the viewport
- Parallax and pinned-section effects without a library
- Horizontal scroll galleries tied to vertical scroll
- Any effect that maps an animation's progress to scroll position

**Two timeline kinds**:
- **Scroll progress timeline** (`scroll()`): progress of a scroll container (0% top → 100% bottom).
- **View progress timeline** (`view()`): progress of an element as it crosses the viewport (enters → exits).

**Browser support**: Chromium-based browsers ship this; Safari/Firefox vary. Always gate with `@supports (animation-timeline: scroll())` and provide a sensible static fallback.

---

## Core Concepts

### 1. Anonymous scroll timeline

```css
@keyframes grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }

.progress-bar {
  transform-origin: left;
  animation: grow auto linear;
  animation-timeline: scroll(root block); /* nearest root scroller, block axis */
}
```

`scroll(<scroller> <axis>)`: scroller is `root` | `nearest` | `self`; axis is
`block` | `inline` | `x` | `y`.

### 2. Anonymous view timeline

```css
@keyframes reveal {
  from { opacity: 0; transform: translateY(40px); }
  to   { opacity: 1; transform: translateY(0); }
}

.card {
  animation: reveal linear both;
  animation-timeline: view();
  animation-range: entry 0% cover 40%; /* start as it enters, finish at 40% covered */
}
```

### 3. animation-range

Controls where in the timeline the animation starts and ends. Named ranges for
view timelines: `cover`, `contain`, `entry`, `exit`, `entry-crossing`,
`exit-crossing`, each with a 0–100% offset.

```css
animation-range: entry 0% entry 100%;   /* only while entering */
animation-range: cover 0% cover 100%;    /* whole time element overlaps viewport */
```

### 4. Named timelines (share one timeline across elements)

```css
.scroller { scroll-timeline: --page block; }      /* define */
.indicator {
  animation: grow auto linear;
  animation-timeline: --page;                      /* reference */
}

/* View timeline named on a subject, used by a sibling/descendant */
.image { view-timeline: --img block; }
.caption {
  animation: reveal linear both;
  animation-timeline: --img;
  animation-range: contain 0% contain 100%;
}
```

Use `timeline-scope: --img;` on a common ancestor to reference a named timeline
from outside the subject's subtree.

### 5. Progressive enhancement

```css
.card { opacity: 1; } /* visible by default (fallback) */

@supports (animation-timeline: view()) {
  .card {
    opacity: 0;
    animation: reveal linear both;
    animation-timeline: view();
    animation-range: entry 0% cover 40%;
  }
}
```

---

## Common Patterns

### Pattern 1: Scroll progress bar

```css
@keyframes grow { to { transform: scaleX(1); } }
.progress {
  position: fixed; inset: 0 0 auto 0; height: 4px; background: #7b5cff;
  transform: scaleX(0); transform-origin: left;
  animation: grow auto linear;
  animation-timeline: scroll(root);
}
```

### Pattern 2: Reveal on enter

```css
@keyframes reveal { from { opacity: 0; translate: 0 2rem; } to { opacity: 1; translate: 0 0; } }
.reveal {
  animation: reveal linear both;
  animation-timeline: view();
  animation-range: entry 0% cover 30%;
}
```

### Pattern 3: Parallax layer

```css
@keyframes parallax { to { translate: 0 -20%; } }
.bg {
  animation: parallax linear;
  animation-timeline: view();
  animation-range: cover;
}
```

### Pattern 4: Sticky image reveal (clip)

```css
@keyframes unclip { from { clip-path: inset(45%); } to { clip-path: inset(0%); } }
.sticky-img {
  position: sticky; top: 0;
  animation: unclip linear both;
  animation-timeline: view();
  animation-range: entry 0% cover 50%;
}
```

### Pattern 5: Horizontal scroll driven by vertical scroll

```css
.h-wrap { height: 300vh; }                     /* tall track */
.h-sticky { position: sticky; top: 0; height: 100vh; overflow: hidden; }
@keyframes slide { to { transform: translateX(-66%); } }
.h-row {
  display: flex;
  animation: slide auto linear;
  animation-timeline: scroll(root);            /* progress of page scroll */
}
```

### Pattern 6: Color / theme shift with scroll

```css
@keyframes tint { from { background: #0b0b12; } to { background: #1b1030; } }
body {
  animation: tint auto linear;
  animation-timeline: scroll(root);
}
```

---

## Integration Patterns

- **Pure CSS first**: reach for this before a JS library for simple scroll maps.
- **GSAP ScrollTrigger**: use JS when you need scrubbed timelines with complex logic, pinning with callbacks, or broad browser support. See `gsap-scrolltrigger`.
- **Lenis smooth scroll**: native scroll-driven animations work with Lenis since it keeps real scroll. See `lenis-smooth-scroll`.
- **AOS / scroll-reveal**: this replaces many reveal-library use cases with zero JS. See `scroll-reveal-libraries`.
- **Design systems**: expose durations/ranges as custom properties for consistency. See `modern-web-design`.

---

## Performance Optimization

- **Off main thread**: these animations are compositor-driven; animate `transform`, `opacity`, `clip-path`, and `translate`/`scale` for best performance.
- **Avoid layout-triggering properties** (`width`, `top`, `margin`) in scroll keyframes.
- **Prefer anonymous `view()`/`scroll()`** for one-off effects; use named timelines only when sharing.
- **Keep keyframes simple**; the browser interpolates against scroll with no JS cost.
- **Respect reduced motion**: wrap effects so they are disabled under `prefers-reduced-motion: reduce`.

---

## Common Pitfalls

- **No fallback**: unsupported browsers run the animation once (or not at all). Set the final/visible state as default and enhance with `@supports`.
- **Element hidden forever**: setting `opacity: 0` without the animation applying (unsupported browser) hides content. Gate the `opacity: 0` inside `@supports`.
- **Wrong scroller**: `scroll(root)` vs `scroll(nearest)` matters when inside a scroll container.
- **`animation-range` units**: named ranges (`entry`, `cover`) apply to view timelines; percentages alone reference the whole timeline.
- **`timeline-scope` missing**: referencing a named timeline outside the subject subtree needs `timeline-scope` on a common ancestor.
- **Using `both`/`forwards` incorrectly**: use `both` so start and end states hold outside the active range.
- **Reduced motion ignored**: large parallax/clip moves can cause discomfort.

---

## Resources

**Scripts** (`scripts/`):
- `generate_scroll_css.py` — Generate CSS for a scroll-driven effect (progress, reveal, parallax, sticky-clip, horizontal, tint), with a `@supports` fallback wrapper
- `check_reduced_motion.py` — Wrap generated CSS with a `prefers-reduced-motion` guard

**References** (`references/`):
- `api_reference.md` — Properties, functions, named ranges, and the support/fallback matrix

**Assets** (`assets/`):
- `starter_css_scroll/` — Static HTML/CSS demo: progress bar, reveal, parallax, sticky reveal (no JS)

**Reference links**:
- MDN scroll-driven animations: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_scroll-driven_animations
- scroll-driven-animations.style: https://scroll-driven-animations.style/

## Related Skills

- `gsap-scrolltrigger` — JS scroll animation when logic/pinning/support is needed
- `lenis-smooth-scroll` — Smooth scroll that works alongside native timelines
- `scroll-reveal-libraries` — Library reveals this can replace
- `modern-web-design` — Tokenizing motion for a design system
