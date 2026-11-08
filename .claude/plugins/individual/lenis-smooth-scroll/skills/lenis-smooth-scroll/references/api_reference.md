# Lenis API Reference

Reference for the `lenis` package (formerly `@studio-freight/lenis`).

> Verify current options and the React API at
> https://github.com/darkroomengineering/lenis before relying on edge behavior.

## Installation

```bash
npm install lenis
```

Import the core and the base CSS:

```js
import Lenis from 'lenis'
import 'lenis/dist/lenis.css'
```

## Constructor Options

```js
const lenis = new Lenis({ /* options */ })
```

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `wrapper` | Element/Window | `window` | Scroll container |
| `content` | Element | `document.documentElement` | Scrolled content |
| `lerp` | number | `0.1` | Linear interpolation intensity (alternative to `duration`) |
| `duration` | number | `1.2` | Smoothing duration (used when `lerp` is unset) |
| `easing` | function | expo-out | `(t: 0..1) => number` easing for `duration` mode |
| `orientation` | string | `'vertical'` | `'vertical'` or `'horizontal'` |
| `gestureOrientation` | string | `'vertical'` | Which gestures scroll: `'vertical'`, `'horizontal'`, `'both'` |
| `smoothWheel` | boolean | `true` | Smooth mouse-wheel input |
| `syncTouch` | boolean | `false` | Smooth touch (experimental; off keeps native touch) |
| `wheelMultiplier` | number | `1` | Wheel delta multiplier |
| `touchMultiplier` | number | `1` | Touch delta multiplier |
| `infinite` | boolean | `false` | Infinite scroll loop |
| `autoRaf` | boolean | `false` | Run an internal RAF loop automatically |
| `overscroll` | boolean | `true` | Allow overscroll behavior |

Use either `lerp` OR `duration`+`easing`, not both.

## Methods

| Method | Description |
| --- | --- |
| `lenis.raf(time)` | Advance smoothing; call each frame with a ms timestamp |
| `lenis.scrollTo(target, options?)` | Scroll to a target (see below) |
| `lenis.stop()` | Pause smooth scroll and lock scrolling |
| `lenis.start()` | Resume |
| `lenis.resize()` | Recalculate dimensions after layout change |
| `lenis.destroy()` | Remove listeners and tear down |
| `lenis.on(event, callback)` | Subscribe to an event; returns an unsubscribe fn |
| `lenis.off(event, callback)` | Unsubscribe |

### scrollTo

```js
lenis.scrollTo(target, {
  offset: 0,            // px offset from target
  lerp: 0.1,            // or use duration
  duration: 1.5,        // seconds
  easing: (t) => t,     // easing function
  immediate: false,     // jump without animating
  lock: false,          // prevent user scroll during the tween
  force: false,         // scroll even if stopped
  onComplete: () => {},
})
```

`target` may be: a number (px), a CSS selector string (`'#id'`), an element, or
the keywords `'top'` / `'bottom'` / `'left'` / `'right'`.

## Events

```js
const unsub = lenis.on('scroll', (e) => {
  e.scroll      // current scroll (px)
  e.limit       // max scroll (px)
  e.velocity    // px per frame
  e.direction   // 1 (down/right) or -1 (up/left)
  e.progress    // 0..1 overall progress
})
```

## Instance Properties

| Property | Description |
| --- | --- |
| `lenis.scroll` | Current smoothed scroll position |
| `lenis.velocity` | Current scroll velocity |
| `lenis.progress` | Scroll progress 0..1 |
| `lenis.direction` | 1 or -1 |
| `lenis.isScrolling` | Whether a scroll is in progress |
| `lenis.isStopped` | Whether scrolling is locked |

## Required CSS

Importing `lenis/dist/lenis.css` provides these; include equivalents if you
style manually:

```css
html.lenis, html.lenis body { height: auto; }
.lenis.lenis-smooth { scroll-behavior: auto !important; }
.lenis.lenis-smooth [data-lenis-prevent] { overscroll-behavior: contain; }
.lenis.lenis-stopped { overflow: hidden; }
.lenis.lenis-smooth iframe { pointer-events: none; }
```

Use `data-lenis-prevent` on a scrollable child (e.g. a modal body) to exclude it
from Lenis.

## GSAP ScrollTrigger Integration

```js
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
gsap.registerPlugin(ScrollTrigger)

const lenis = new Lenis()
lenis.on('scroll', ScrollTrigger.update)
gsap.ticker.add((time) => lenis.raf(time * 1000))
gsap.ticker.lagSmoothing(0)
```

## React (`lenis/react`)

```jsx
import { ReactLenis, useLenis } from 'lenis/react'

// Root usage wraps the app; `root` mounts Lenis on <html>
<ReactLenis root options={{ duration: 1.2, easing: (t) => t }}>
  {children}
</ReactLenis>

// Access the instance anywhere below the provider
const lenis = useLenis(({ scroll }) => {
  // optional callback runs on scroll
})
```

For a custom RAF (e.g. with `@react-three/fiber`'s frame loop), pass
`options={{ autoRaf: false }}` and call `lenis.raf(time)` from your loop.

## Accessibility

Gate smoothing behind reduced-motion:

```js
const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
const lenis = new Lenis({ smoothWheel: !prefersReduced, duration: prefersReduced ? 0 : 1.2 })
```
