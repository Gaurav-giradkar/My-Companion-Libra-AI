const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function formatInterfaceTime(date = new Date()) {
  return date.toLocaleTimeString([], {
    hour: "numeric",
    minute: "2-digit",
  });
}

function formatInterfaceDate(date = new Date()) {
  return date.toLocaleDateString([], {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
}

function updateLiveTimeNodes() {
  const now = new Date();

  document.querySelectorAll("[data-live-time]").forEach((node) => {
    node.textContent = formatInterfaceTime(now);
  });

  document.querySelectorAll("[data-live-date]").forEach((node) => {
    node.textContent = formatInterfaceDate(now);
  });
}

function setupTiltCards() {
  if (prefersReducedMotion) {
    document.querySelectorAll("[data-tilt]").forEach((card) => {
      card.classList.add("is-visible");
    });
    return;
  }

  document.querySelectorAll("[data-tilt]").forEach((card) => {
    card.addEventListener("pointermove", (event) => {
      const rect = card.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width;
      const y = (event.clientY - rect.top) / rect.height;
      const rotateY = (x - 0.5) * 8;
      const rotateX = (0.5 - y) * 8;

      card.style.setProperty("--tilt-x", `${rotateX}deg`);
      card.style.setProperty("--tilt-y", `${rotateY}deg`);
      card.style.setProperty("--glow-x", `${x * 100}%`);
      card.style.setProperty("--glow-y", `${y * 100}%`);
    });

    card.addEventListener("pointerleave", () => {
      card.style.setProperty("--tilt-x", "0deg");
      card.style.setProperty("--tilt-y", "0deg");
      card.style.setProperty("--glow-x", "50%");
      card.style.setProperty("--glow-y", "50%");
    });
  });
}

function setupRevealCards() {
  const cards = document.querySelectorAll(".interactive-card");
  if (!cards.length) {
    return;
  }

  if (prefersReducedMotion || !("IntersectionObserver" in window)) {
    cards.forEach((card) => card.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) {
          return;
        }

        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.18 }
  );

  cards.forEach((card) => observer.observe(card));
}

function animateCount(node) {
  const target = Number(node.dataset.countup || "0");
  if (!Number.isFinite(target)) {
    return;
  }

  if (prefersReducedMotion) {
    node.textContent = String(target);
    return;
  }

  const duration = 1200;
  const startTime = performance.now();

  function frame(now) {
    const progress = Math.min((now - startTime) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    node.textContent = String(Math.round(target * eased));

    if (progress < 1) {
      requestAnimationFrame(frame);
    }
  }

  requestAnimationFrame(frame);
}

function setupCountups() {
  const nodes = document.querySelectorAll("[data-countup]");
  if (!nodes.length) {
    return;
  }

  if (prefersReducedMotion || !("IntersectionObserver" in window)) {
    nodes.forEach(animateCount);
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) {
          return;
        }

        animateCount(entry.target);
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.4 }
  );

  nodes.forEach((node) => observer.observe(node));
}

document.addEventListener("DOMContentLoaded", () => {
  updateLiveTimeNodes();
  setupTiltCards();
  setupRevealCards();
  setupCountups();

  window.setInterval(updateLiveTimeNodes, 1000);
});
