// Theme: dark by default, light on request. Loaded blocking in <head>, after the stylesheet, so the
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

  apply(stored() === "light" ? "light" : "dark");

  document.addEventListener("DOMContentLoaded", () => {
    const button = document.querySelector("[data-theme-toggle]");
    const label = () => button.setAttribute("aria-label", `Switch to ${root.dataset.theme === "dark" ? "light" : "dark"} theme`);
    label();
    button.addEventListener("click", () => {
      const next = root.dataset.theme === "dark" ? "light" : "dark";
      apply(next);
      label();
      try { localStorage.setItem("theme", next); } catch { /* Private mode: the choice lasts for this page only. */ }
    });
  });
})();
