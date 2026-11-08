# CSS Scroll-Driven Animations Reference

Reference for the native CSS scroll-timeline and view-timeline features.

> Browser support is still rolling out. Verify current status at
> https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_scroll-driven_animations
> and always provide a `@supports` fallback.

## Properties

| Property | Applies to | Description |
| --- | --- | --- |
| `animation-timeline` | animated element | Which timeline drives the animation: `auto`, `none`, `scroll(...)`, `view(...)`, or a named `--timeline` |
| `animation-range` | animated element | Start/end of the active window along the timeline |
| `scroll-timeline` | scroll container | Define a named scroll progress timeline |
| `scroll-timeline-name` / `scroll-timeline-axis` | scroll container | Longhands of `scroll-timeline` |
| `view-timeline` | subject element | Define a named view progress timeline |
| `view-timeline-name` / `view-timeline-axis` / `view-timeline-inset` | subject | Longhands of `view-timeline` |
| `timeline-scope` | ancestor | Hoist a named timeline so it's referenceable outside the subject subtree |

## Timeline functions

### scroll()

```
scroll( [ <scroller> ]? [ <axis> ]? )
```
- `<scroller>`: `nearest` (default) | `root` | `self`
- `<axis>`: `block` (default) | `inline` | `x` | `y`

Progress: 0% at scroll start, 100% at max scroll of that scroller.

### view()

```
view( [ <axis> ]? [ <inset> ]? )
```
- `<axis>`: `block` (default) | `inline` | `x` | `y`
- `<inset>`: adjusts when the subject is considered in view (e.g. `view(block 20%)`)

Progress: based on the subject element crossing the scrollport.

## animation-range named ranges (view timelines)

| Range | Meaning |
| --- | --- |
| `cover` | From when the subject first touches the viewport to when it fully leaves |
| `contain` | While the subject is fully within (or fully covers) the viewport |
| `entry` | While the subject is entering the viewport |
| `exit` | While the subject is leaving the viewport |
| `entry-crossing` | While the subject crosses the starting edge |
| `exit-crossing` | While the subject crosses the ending edge |

Each takes an optional percentage offset:

```css
animation-range: entry 0% cover 50%;   /* start entering, end at 50% cover */
animation-range: contain;              /* shorthand for contain 0% contain 100% */
```

For scroll (not view) timelines, use plain percentages:

```css
animation-range: 0% 100%;
```

## Named timeline usage

```css
/* Scroll timeline */
.scroller { scroll-timeline: --page block; }
.bar { animation: grow auto linear; animation-timeline: --page; }

/* View timeline on a subject, consumed by a sibling */
.subject { view-timeline: --subj block; }
.consumer {
  animation: reveal linear both;
  animation-timeline: --subj;
  animation-range: entry 0% cover 40%;
}

/* Reference a named timeline from outside the subject's subtree */
.ancestor { timeline-scope: --subj; }
```

## Fallback / support matrix

Gate enhancements and hide-by-animation states behind `@supports`:

```css
/* Baseline: visible, static */
.reveal { opacity: 1; }

@supports (animation-timeline: view()) {
  .reveal {
    opacity: 0;                 /* only hide where the animation can reveal it */
    animation: reveal linear both;
    animation-timeline: view();
    animation-range: entry 0% cover 30%;
  }
}
```

Feature test in JS when needed:

```js
const supported = CSS.supports('animation-timeline: scroll()')
```

## Reduced motion

```css
@media (prefers-reduced-motion: reduce) {
  .reveal, .parallax, .sticky-img {
    animation: none;
    opacity: 1;
    transform: none;
    clip-path: none;
  }
}
```

## Keyframe tips

- Animate compositor-friendly properties: `transform`, `translate`, `scale`,
  `rotate`, `opacity`, `clip-path`.
- Use `both` fill so the first/last keyframe holds outside `animation-range`.
- Timing function should usually be `linear` so progress maps evenly to scroll.
- `animation-duration` is ignored for scroll-driven animations; use `auto`.
