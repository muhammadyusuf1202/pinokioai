// PinokioAI — Main JS

// Auto-hide flash messages
document.addEventListener('DOMContentLoaded', () => {
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(f => {
    setTimeout(() => {
      f.style.transition = 'opacity 0.5s';
      f.style.opacity = '0';
      setTimeout(() => f.remove(), 500);
    }, 3500);
  });

  // Intersection observer for stats
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.animation = 'fadeUp 0.6s ease both';
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.stat-card, .feature-card, .price-card').forEach(el => {
    observer.observe(el);
  });
});

// CSS fadeUp
const style = document.createElement('style');
style.textContent = `
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
`;
document.head.appendChild(style);
