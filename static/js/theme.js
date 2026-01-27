const THEMES = ["blue", "purple", "green", "red"];
const THEME_CLASSES = THEMES.map(t => "theme-" + t);

function applyTheme(theme) {
  document.body.classList.remove(...THEME_CLASSES);
  document.body.classList.add("ai-bg", "theme-" + theme);
  localStorage.setItem("libra-theme", theme);
}

// --------------------
// CREATE THEME STACK
// --------------------
function createThemeStack() {
  let stack = document.querySelector(".theme-stack");
  if (stack) return stack;

  stack = document.createElement("div");
  stack.className = "theme-stack";
  stack.innerHTML = `
    <div class="theme-bubble theme-blue" data-theme="blue">Dusk Neon</div>
    <div class="theme-bubble theme-purple" data-theme="purple">Obsidian Glow</div>
    <div class="theme-bubble theme-green" data-theme="green">Dark Elegant</div>
    <div class="theme-bubble theme-red" data-theme="red">Berry Red</div>
  `;

  document.body.appendChild(stack);

  stack.querySelectorAll(".theme-bubble").forEach(bubble => {
    bubble.addEventListener("click", () => {
      applyTheme(bubble.dataset.theme);
      stack.style.display = "none";
    });
  });

  return stack;
}

// --------------------
// INIT SYSTEM
// --------------------
document.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("libra-theme");
  applyTheme(savedTheme && THEMES.includes(savedTheme) ? savedTheme : "blue");

  const themeToggle = document.getElementById("themeToggle");
  if (!themeToggle) return;

  const stack = createThemeStack();

  themeToggle.addEventListener("click", (e) => {
    e.stopPropagation();
    stack.style.display = stack.style.display === "flex" ? "none" : "flex";
  });

  // Close stack on outside click
  document.addEventListener("click", () => {
    stack.style.display = "none";
  });
});

// --------------------
// SYNC ACROSS TABS
// --------------------
window.addEventListener("storage", (e) => {
  if (e.key === "libra-theme" && e.newValue) {
    applyTheme(e.newValue);
  }
});
