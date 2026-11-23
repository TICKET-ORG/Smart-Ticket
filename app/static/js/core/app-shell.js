export function initAppShell() {
  const shell = document.querySelector("[data-app-shell]");

  if (!shell) {
    return;
  }

  const toggle = shell.querySelector("[data-shell-toggle]");
  const closers = shell.querySelectorAll("[data-shell-close]");
  const sidebar = shell.querySelector("#app-sidebar");

  const setOpen = (open) => {
    shell.dataset.sidebarOpen = String(open);
    toggle?.setAttribute("aria-expanded", String(open));
    toggle?.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    document.body.classList.toggle("is-shell-locked", open);
  };

  toggle?.addEventListener("click", () => {
    setOpen(shell.dataset.sidebarOpen !== "true");
  });

  closers.forEach((element) => {
    element.addEventListener("click", () => setOpen(false));
  });

  sidebar?.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => setOpen(false));
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && shell.dataset.sidebarOpen === "true") {
      setOpen(false);
      toggle?.focus();
    }
  });

  const desktop = window.matchMedia("(min-width: 961px)");
  desktop.addEventListener("change", (event) => {
    if (event.matches) {
      setOpen(false);
    }
  });

  const roleSwitch = shell.querySelector("[data-role-switch]");

  if (roleSwitch) {
    document.addEventListener("click", (event) => {
      if (roleSwitch.open && !roleSwitch.contains(event.target)) {
        roleSwitch.open = false;
      }
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && roleSwitch.open) {
        roleSwitch.open = false;
        roleSwitch.querySelector("summary")?.focus();
      }
    });
  }
}
