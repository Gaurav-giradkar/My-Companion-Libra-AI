// document.addEventListener("DOMContentLoaded", () => {
//   const themes = [
//     "theme-blue",
//     "theme-purple",
//     "theme-green",
//     "theme-red"
//   ];

//   let currentTheme = 0;
//   const themeToggle = document.getElementById("themeToggle");
//   if (!themeToggle) return;

//   // Load saved theme
//   const savedTheme = localStorage.getItem("libra-theme");
//   if (savedTheme && themes.includes(savedTheme)) {
//     document.body.classList.remove(...themes);
//     document.body.classList.add(savedTheme);
//     currentTheme = themes.indexOf(savedTheme);
//   } else {
//     document.body.classList.add("theme-blue");
//     currentTheme = 0;
//   }

//   // Toggle theme
//   themeToggle.addEventListener("click", () => {
//     document.body.classList.remove(...themes);

//     currentTheme = (currentTheme + 1) % themes.length;
//     const newTheme = themes[currentTheme];

//     document.body.classList.add(newTheme);
//     localStorage.setItem("libra-theme", newTheme);

//     // Click animation
//     themeToggle.style.transform = "scale(1.3)";
//     setTimeout(() => {
//       themeToggle.style.transform = "scale(1)";
//     }, 150);
//   });
// });

// window.addEventListener("storage", (e) => {
//   if (e.key === "libra-theme" && e.newValue) {
//     document.body.classList.remove("theme-blue", "theme-purple", "theme-green", "theme-red");
//     document.body.classList.add(e.newValue);
//   }
// });













// const THEMES = ["theme-blue", "theme-purple", "theme-green", "theme-red"];

// function applyTheme(theme) {
//   document.body.classList.remove(...THEMES);
//   document.body.classList.add("ai-bg", theme);
//   localStorage.setItem("libra-theme", theme);
// }

// // Restore theme on load
// document.addEventListener("DOMContentLoaded", () => {
//   const savedTheme = localStorage.getItem("libra-theme");

//   if (savedTheme && THEMES.includes(savedTheme)) {
//     applyTheme(savedTheme);
//   } else {
//     applyTheme("theme-blue"); // default
//   }

//   const themeToggle = document.getElementById("themeToggle");
//   if (!themeToggle) return;

//   let currentTheme = THEMES.indexOf(
//     localStorage.getItem("libra-theme") || "theme-blue"
//   );

//   // Toggle theme button
//   themeToggle.addEventListener("click", () => {
//     currentTheme = (currentTheme + 1) % THEMES.length;
//     applyTheme(THEMES[currentTheme]);

//     // Click animation
//     themeToggle.style.transform = "scale(1.3)";
//     setTimeout(() => {
//       themeToggle.style.transform = "scale(1)";
//     }, 150);
//   });
// });

// // Sync theme across open tabs/pages
// window.addEventListener("storage", (e) => {
//   if (e.key === "libra-theme" && e.newValue) {
//     document.body.classList.remove(...THEMES);
//     document.body.classList.add("ai-bg", e.newValue);
//   }
// });













// const THEMES = ["theme-blue", "theme-purple", "theme-green", "theme-red"];

// function applyTheme(theme) {
//   document.body.classList.remove(...THEMES);
//   document.body.classList.add("ai-bg", theme);
//   localStorage.setItem("libra-theme", theme);
// }

// // Restore theme on every page load
// document.addEventListener("DOMContentLoaded", () => {
//   const savedTheme = localStorage.getItem("libra-theme");

//   if (THEMES.includes(savedTheme)) {
//     applyTheme(savedTheme);
//   } else {
//     applyTheme("theme-blue");
//   }

//   const toggle = document.getElementById("themeToggle");
//   if (!toggle) return;

//   let current = THEMES.indexOf(
//     localStorage.getItem("libra-theme") || "theme-blue"
//   );

//   toggle.addEventListener("click", () => {
//     current = (current + 1) % THEMES.length;
//     applyTheme(THEMES[current]);

//     toggle.style.transform = "scale(1.3)";
//     setTimeout(() => toggle.style.transform = "scale(1)", 150);
//   });
// });

// // Sync across open tabs
// window.addEventListener("storage", (e) => {
//   if (e.key === "libra-theme" && THEMES.includes(e.newValue)) {
//     applyTheme(e.newValue);
//   }
// });



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
