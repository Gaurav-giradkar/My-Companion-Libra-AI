const THEMES = [
  { id: "blue", label: "Neon Abyss", detail: "cool neon grid" },
  { id: "green", label: "Matrix Core", detail: "clean synth glow" },
  { id: "red", label: "Crimson Vibe", detail: "alert cinema hue" },
  { id: "purple", label: "Nebula Night", detail: "midnight plasma" },
];

const THEME_CLASSES = THEMES.map((theme) => `theme-${theme.id}`);

function getThemeMeta(themeId) {
  return THEMES.find((theme) => theme.id === themeId) || THEMES[0];
}

function syncThemeIndicators(themeId) {
  const theme = getThemeMeta(themeId);

  document.querySelectorAll("[data-theme-name]").forEach((node) => {
    node.textContent = theme.label;
  });

  const themeToggle = document.getElementById("themeToggle");
  if (themeToggle) {
    themeToggle.dataset.activeTheme = theme.label;
  }
}

function applyTheme(theme) {
  document.body.classList.remove(...THEME_CLASSES);
  document.body.classList.add("ai-bg", `theme-${theme}`);
  localStorage.setItem("libra-theme", theme);
  syncThemeIndicators(theme);
}

function createThemeStack() {
  let stack = document.querySelector(".theme-stack");
  if (stack) {
    return stack;
  }

  stack = document.createElement("div");
  stack.className = "theme-stack";
  stack.innerHTML = THEMES.map(
    (theme) => `
      <button type="button" class="theme-bubble theme-${theme.id}" data-theme="${theme.id}">
        <span class="theme-bubble-label">${theme.label}</span>
        <small>${theme.detail}</small>
      </button>
    `
  ).join("");

  document.body.appendChild(stack);

  stack.querySelectorAll(".theme-bubble").forEach((bubble) => {
    bubble.addEventListener("click", () => {
      applyTheme(bubble.dataset.theme);
      stack.classList.remove("is-open");
      const themeToggle = document.getElementById("themeToggle");
      if (themeToggle) {
        themeToggle.setAttribute("aria-expanded", "false");
      }
    });
  });

  return stack;
}

document.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("libra-theme");
  const preferredTheme =
    savedTheme && THEMES.some((theme) => theme.id === savedTheme) ? savedTheme : "blue";
  applyTheme(preferredTheme);

  const themeToggle = document.getElementById("themeToggle");
  if (!themeToggle) {
    return;
  }

  const stack = createThemeStack();
  themeToggle.setAttribute("aria-expanded", "false");

  themeToggle.addEventListener("click", (event) => {
    event.stopPropagation();
    const isOpen = stack.classList.toggle("is-open");
    themeToggle.setAttribute("aria-expanded", String(isOpen));
  });

  document.addEventListener("click", () => {
    stack.classList.remove("is-open");
    themeToggle.setAttribute("aria-expanded", "false");
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") {
      return;
    }

    stack.classList.remove("is-open");
    themeToggle.setAttribute("aria-expanded", "false");
  });
});

window.addEventListener("storage", (event) => {
  if (event.key === "libra-theme" && event.newValue) {
    applyTheme(event.newValue);
  }
});
