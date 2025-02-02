// This script handles the preloader, hamburger menu toggle, smooth scrolling, and header state.
document.addEventListener('DOMContentLoaded', () => {
  const hamburger = document.querySelector('.hamburger')
  const navLinks = document.querySelector('.nav-links')
  const header = document.querySelector('header')

  // Toggle mobile navigation menu
  hamburger.addEventListener('click', () => {
    navLinks.classList.toggle('active')
  })

  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault()
      document.querySelector(this.getAttribute('href')).scrollIntoView({
        behavior: 'smooth',
      })
      if (navLinks.classList.contains('active')) {
        navLinks.classList.remove('active')
      }
    })
  })

  // Change header style on scroll
  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
      header.classList.add('scrolled')
    } else {
      header.classList.remove('scrolled')
    }
  })

  // Remove preloader on window load
  window.addEventListener('load', () => {
    const preloader = document.getElementById('preloader')
    preloader.style.opacity = '0'
    setTimeout(() => {
      preloader.style.display = 'none'
    }, 500)
  })
})
