---
name: lenis-smooth-scroll
description: Add smooth, inertia-based scrolling to the web with Lenis - a lightweight, performant smooth-scroll library. Use when building design-agency style sites with buttery smooth scroll, scroll-driven parallax, reveal-on-scroll sections, or anchor scrolling, and when synchronizing smooth scroll with GSAP ScrollTrigger, Theatre.js sequences, or React. Triggers on tasks involving Lenis, smooth scroll, inertia/momentum scrolling, scroll normalization, scrollTo anchors, parallax, scroll progress, or integrating smooth scroll with animation timelines. Modern alternative to Locomotive Scroll with a smaller footprint and native-scroll compatibility.
---

# Lenis Smooth Scroll

## Overview

Lenis is a lightweight smooth-scroll library that adds inertia-based scrolling while keeping native scroll behavior, accessibility, and `position: sticky` working. It normalizes wheel/touch input and exposes scroll state so animations can be driven from a single, smooth scroll value.

**When to Use This Skill**:
- Design-agency / portfolio sites that want smooth, weighted scrolling
- Scroll-driven parallax, pinned sections, and reveal-on-scroll effects
- Smooth anchor navigation (`scrollTo`)
- Driving GSAP ScrollTrigger, Theatre.js sequences, or canvas/WebGL from scroll
- Replacing Locomotive Scroll with a lighter, native-compatible option

**Key Benefits**:
- **Lightweight** and dependency-free core
- **Native-compatible**: keeps real scrollbar, `sticky`, anchor links, and a11y
- **Framework-agnostic** core plus a React binding (`lenis/react`)
- **Single source of truth**: one smooth scroll value to drive all motion
- **Composable**: pairs with GSAP ScrollTrigger and Theatre.js

---

## Core Concepts

### 1. Setup and the RAF loop

Lenis needs a requestAnimationFrame loop to advance its smoothing.

```js
import Lenis from 'lenis'
import 'lenis/dist/lenis.css' // required base styles

const lenis = new Lenis({
  duration: 1.2,              // smoothing duration (seconds-ish)
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)), // expo-out
  orientation: 'vertical',    // 'vertical' | 'horizontal'
  gestureOrientation: 'vertical',
  smoothWheel: true,
  wheelMultiplier: 1,
  touchMultiplier: 2,
})

function raf(time) {
  lenis.raf(time)
  requestAnimationFrame(raf)
}
requestAnimationFrame(raf)
```

### 2. Reading scroll state

Subscribe to the `scroll` event; the callback receives scroll, velocity, and progress.

```js
lenis.on('scroll', ({ scroll, velocity, progress, direction }) => {
  // scroll: px from top, velocity: px/frame, progress: 0..1, direction: 1/-1
  document.documentElement.style.setProperty('--scroll', scroll)
})
```

### 3. Programmatic scrolling (anchors)

```js
lenis.scrollTo('#section-2', {
  offset: 0,
  duration: 1.5,
  easing: (t) => 1 - Math.pow(1 - t, 3),
  immediate: false,
  onComplete: () => {},
})

// Also: lenis.scrollTo(0) (top), lenis.scrollTo('bottom'), lenis.scrollTo(1200)
```

### 4. Control methods

```js
lenis.stop()     // pause smooth scroll (e.g. when a modal opens)
lenis.start()    // resume
lenis.resize()   // recalculate after layout changes
lenis.destroy()  // tear down and remove listeners
```

---

## Common Patterns

### Pattern 1: GSAP ScrollTrigger integration (most common)

Drive ScrollTrigger from Lenis instead of native scroll, and run both from GSAP's ticker.

```js
import Lenis from 'lenis'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

const lenis = new Lenis()

// Update ScrollTrigger on every Lenis scroll
lenis.on('scroll', ScrollTrigger.update)

// Drive Lenis from GSAP's ticker (single RAF loop) and disable lag smoothing
gsap.ticker.add((time) => lenis.raf(time * 1000))
gsap.ticker.lagSmoothing(0)
```

### Pattern 2: Parallax layers

```js
const layers = document.querySelectorAll('[data-speed]')

lenis.on('scroll', ({ scroll }) => {
  layers.forEach((el) => {
    const speed = parseFloat(el.dataset.speed) // e.g. 0.2, -0.4
    el.style.transform = `translate3d(0, ${scroll * speed}px, 0)`
  })
})
```

### Pattern 3: Reveal on scroll

Use the native IntersectionObserver (Lenis keeps the real scroll, so observers work).

```js
const io = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('is-visible')
      io.unobserve(entry.target)
    }
  })
}, { threshold: 0.2 })

document.querySelectorAll('.reveal').forEach((el) => io.observe(el))
```

### Pattern 4: Scroll progress indicator

```js
const bar = document.querySelector('.progress-bar')
lenis.on('scroll', ({ progress }) => {
  bar.style.transform = `scaleX(${progress})`
})
```

### Pattern 5: React (`lenis/react`)

```jsx
import { ReactLenis, useLenis } from 'lenis/react'

function Layout({ children }) {
  return (
    <ReactLenis root options={{ duration: 1.2 }}>
      {children}
    </ReactLenis>
  )
}

function Nav() {
  const lenis = useLenis()
  return <button onClick={() => lenis?.scrollTo('#contact')}>Contact</button>
}
```

### Pattern 6: Drive a Theatre.js sequence from smooth scroll

```js
// Feed Lenis progress into a Theatre.js sequence position (see theatrejs-motion)
const SEQ_LENGTH = 5
lenis.on('scroll', ({ progress }) => {
  sheet.sequence.position = progress * SEQ_LENGTH
})
```

---

## Integration Patterns

- **GSAP ScrollTrigger**: Pattern 1 — let Lenis feed `ScrollTrigger.update`. See `gsap-scrolltrigger`.
- **Theatre.js**: Map Lenis `progress` onto `sequence.position`. See `theatrejs-motion`.
- **Three.js / R3F**: Use the smooth `scroll`/`velocity` to drive camera or uniforms. See `threejs-webgl`, `react-three-fiber`.
- **Barba.js**: Call `lenis.destroy()` on page leave and re-init on enter for SPA transitions. See `barba-js`.
- **Locomotive Scroll**: Lenis is the lighter modern alternative; prefer it for new projects.

---

## Performance Optimization

- **One RAF loop**: when using GSAP, drive Lenis from `gsap.ticker` instead of a second `requestAnimationFrame`.
- **Use transforms**: animate `translate3d`/`scale`, not `top`/`left`, for parallax.
- **Throttle heavy work**: the `scroll` event fires every frame; keep handlers cheap and avoid layout reads in them.
- **Prefer IntersectionObserver** for reveals over measuring positions each frame.
- **Call `lenis.resize()`** after DOM/layout changes (font load, accordion open) so mapping stays correct.
- **Respect reduced motion**: disable or shorten smoothing when `prefers-reduced-motion` is set.

---

## Common Pitfalls

- **Nothing scrolls / janky**: the RAF loop isn't running, or two loops fight. Use a single loop (GSAP ticker when GSAP is present).
- **Missing base CSS**: not importing `lenis/dist/lenis.css` (or the equivalent `html.lenis` rules) breaks sizing and sticky.
- **ScrollTrigger out of sync**: forgot `lenis.on('scroll', ScrollTrigger.update)` or `gsap.ticker.lagSmoothing(0)`.
- **Anchor links jump**: use `lenis.scrollTo('#id')` instead of native hash navigation for smooth behavior.
- **Modal scrolls the page behind**: call `lenis.stop()` when opening overlays, `lenis.start()` on close.
- **SPA leaks**: not calling `lenis.destroy()` on route/page change creates duplicate listeners.
- **Reduced motion ignored**: smooth scroll can cause discomfort; gate it behind `prefers-reduced-motion`.

---

## Resources

**Scripts** (`scripts/`):
- `init_lenis.py` — Scaffold Lenis setup from a preset: `vanilla`, `gsap`, `react`
- `generate_config.py` — Build a Lenis options object from choices (duration, orientation, easing, etc.)

**References** (`references/`):
- `api_reference.md` — Full options, methods, events, React binding, and CSS requirements

**Assets** (`assets/`):
- `starter_lenis/` — Minimal Vite starter with Lenis + a parallax and reveal demo

**Official**:
- Repo: https://github.com/darkroomengineering/lenis
- npm: https://www.npmjs.com/package/lenis

## Related Skills

- `gsap-scrolltrigger` — Pair Lenis with ScrollTrigger for scrubbed timelines
- `theatrejs-motion` — Map Lenis progress onto a Theatre.js sequence
- `locomotive-scroll` — Heavier predecessor; Lenis is the modern alternative
- `scroll-reveal-libraries` — Reveal-on-scroll effects that work alongside Lenis
- `threejs-webgl` / `react-three-fiber` — Drive 3D scenes from smooth scroll
