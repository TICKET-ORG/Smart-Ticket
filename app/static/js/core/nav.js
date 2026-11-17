export function initNav() {
  const header = document.querySelector("[data-site-header]");
  const toggle = header?.querySelector("[data-nav-toggle]");

  if (!header || !toggle) {
    return;
  }

  const setOpen = (open) => {
    header.dataset.navOpen = String(open);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  };

  toggle.addEventListener("click", () => {
    setOpen(header.dataset.navOpen !== "true");
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && header.dataset.navOpen === "true") {
      setOpen(false);
      toggle.focus();
    }
  });

  header.querySelectorAll(".site-nav a").forEach((link) => {
    link.addEventListener("click", () => setOpen(false));
  });

  const desktop = window.matchMedia("(min-width: 901px)");
  desktop.addEventListener("change", (event) => {
    if (event.matches) {
      setOpen(false);
    }
  });
}