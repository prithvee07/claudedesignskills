import Lenis from 'lenis'
import 'lenis/dist/lenis.css'

const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches

const lenis = new Lenis({
  duration: prefersReduced ? 0 : 1.2,
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  smoothWheel: !prefersReduced,
})

function raf(time) {
  lenis.raf(time)
  requestAnimationFrame(raf)
}
requestAnimationFrame(raf)

// Parallax + progress bar
const parallax = document.querySelectorAll('[data-speed]')
const bar = document.querySelector('.progress-bar')

lenis.on('scroll', ({ scroll, progress }) => {
  parallax.forEach((el) => {
    const speed = parseFloat(el.dataset.speed)
    el.style.transform = `translate3d(0, ${scroll * speed}px, 0)`
  })
  if (bar) bar.style.transform = `scaleX(${progress})`
})

// Reveal on scroll via IntersectionObserver (native scroll preserved)
const io = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible')
        io.unobserve(entry.target)
      }
    })
  },
  { threshold: 0.2 },
)
document.querySelectorAll('.reveal').forEach((el) => io.observe(el))

// Smooth anchor links
document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener('click', (e) => {
    e.preventDefault()
    lenis.scrollTo(link.getAttribute('href'))
  })
})
