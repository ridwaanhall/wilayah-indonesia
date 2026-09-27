// Theme: light by default, dark on request. Loaded blocking in <head>, after the stylesheet, so the
// saved theme is applied before first paint and --bg can be read for the browser chrome colour.
(() => {
  const root = document.documentElement;
  const stored = () => {
    try { return localStorage.getItem("theme"); } catch { return null; }
  };
  const apply = (theme) => {
    root.dataset.theme = theme;
    const chrome = getComputedStyle(root).getPropertyValue("--bg").trim();
    document.querySelector('meta[name="theme-color"]')?.setAttribute("content", chrome);
  };

  apply(stored() === "dark" ? "dark" : "light");

  document.addEventListener("DOMContentLoaded", () => {
    // A WAI-ARIA switch: its name stays "Dark theme" and aria-checked carries the state.
    const toggle = document.querySelector("[data-theme-toggle]");
    const sync = () => toggle.setAttribute("aria-checked", String(root.dataset.theme === "dark"));
    sync();
    toggle.addEventListener("click", () => {
      const next = root.dataset.theme === "dark" ? "light" : "dark";
      apply(next);
      sync();
      try { localStorage.setItem("theme", next); } catch { /* Private mode: the choice lasts for this page only. */ }
    });
  });
})();
