/* DataConverter Forge — shared site behavior: theme + local usage-limit system.
   No backend. No accounts. Everything is local to the browser (localStorage).
   Architecture is intentionally split so a future backend/auth/subscription
   layer can replace `Usage` + `Plan` without touching tool code. */

(function () {
  "use strict";

  /* ---------------- Theme ---------------- */
  const Theme = {
    key: "amf_theme",
    init() {
      const saved = localStorage.getItem(this.key);
      const theme = saved || (matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");
      document.documentElement.setAttribute("data-theme", theme);
      const btn = document.querySelector("[data-theme-toggle]");
      if (btn) {
        btn.textContent = theme === "light" ? "☾" : "☀";
        btn.addEventListener("click", () => this.toggle());
      }
    },
    toggle() {
      const cur = document.documentElement.getAttribute("data-theme");
      const next = cur === "light" ? "dark" : "light";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem(this.key, next);
      const btn = document.querySelector("[data-theme-toggle]");
      if (btn) btn.textContent = next === "light" ? "☾" : "☀";
    },
  };

  /* ---------------- Mobile nav ---------------- */
  function initNav() {
    const btn = document.querySelector("[data-menu-toggle]");
    const nav = document.querySelector("[data-main-nav]");
    const backdrop = document.querySelector("[data-nav-backdrop]");
    if (!btn || !nav) return;

    function setOpen(open) {
      nav.classList.toggle("open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      if (backdrop) backdrop.classList.toggle("open", open);
      document.body.classList.toggle("nav-open", open);
    }

    btn.addEventListener("click", () => setOpen(!nav.classList.contains("open")));
    if (backdrop) backdrop.addEventListener("click", () => setOpen(false));
    nav.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => setOpen(false)));
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") setOpen(false);
    });
    // Close automatically if the viewport is resized/rotated back to desktop width
    window.addEventListener("resize", () => {
      if (window.innerWidth > 860) setOpen(false);
    });
  }

  /* ---------------- Scroll reveal ----------------
     Marks section-heads, grids, and prose blocks as .reveal so they fade/slide
     in the first time they enter the viewport. Grids of cards get
     .reveal-stagger so each child animates in sequence. */
  function initReveal() {
    const candidates = document.querySelectorAll(
      ".section-head, .grid, .prose, .pricing-card"
    );
    if (!candidates.length) return;

    candidates.forEach((el) => {
      el.classList.add("reveal");
      if (el.classList.contains("grid")) el.classList.add("reveal-stagger");
    });

    if (!("IntersectionObserver" in window)) {
      candidates.forEach((el) => el.classList.add("in-view"));
      return;
    }

    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("in-view");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.08, rootMargin: "0px 0px -10px 0px" }
    );
    candidates.forEach((el) => io.observe(el));
  }

  /* ---------------- Plan (future premium hook) ----------------
     Today: always "free". Later: read a verified subscription
     status here (e.g. from a signed token issued by a backend
     after PayPal subscription confirmation). Nothing else in the
     codebase needs to change — every tool calls Usage.canRun(). */
  const Plan = {
    get current() {
      // Placeholder for future account/subscription check.
      return localStorage.getItem("amf_plan") || "free";
    },
    get limits() {
      return this.current === "pro"
        ? { dailyConversions: Infinity, maxFileSizeMB: 1024 }
        : { dailyConversions: 5, maxFileSizeMB: 5 };
    },
  };

  /* ---------------- Usage limiter ---------------- */
  const Usage = {
    key: "amf_usage",
    _today() {
      return new Date().toISOString().slice(0, 10);
    },
    _read() {
      try {
        const raw = JSON.parse(localStorage.getItem(this.key) || "{}");
        return raw.date === this._today() ? raw : { date: this._today(), count: 0 };
      } catch (e) {
        return { date: this._today(), count: 0 };
      }
    },
    remaining() {
      const limit = Plan.limits.dailyConversions;
      if (limit === Infinity) return Infinity;
      return Math.max(0, limit - this._read().count);
    },
    canRun() {
      return this.remaining() > 0;
    },
    record() {
      const data = this._read();
      data.count += 1;
      localStorage.setItem(this.key, JSON.stringify(data));
    },
    checkFileSize(bytes) {
      const maxBytes = Plan.limits.maxFileSizeMB * 1024 * 1024;
      return bytes <= maxBytes;
    },
    renderCounter(el) {
      if (!el) return;
      const limit = Plan.limits.dailyConversions;
      if (limit === Infinity) {
        el.innerHTML = `<span>Unlimited conversions — DataConverter Forge Pro</span>`;
        return;
      }
      const used = limit - this.remaining();
      let bars = "";
      for (let i = 0; i < limit; i++) bars += `<span class="bar ${i < used ? "used" : ""}"></span>`;
      el.innerHTML = `<div class="bars">${bars}</div><span>${this.remaining()} of ${limit} free conversions left today</span>`;
    },
  };

  // Expose for tool scripts.
  window.AMForge = { Theme, Usage, Plan };

  document.addEventListener("DOMContentLoaded", () => {
    Theme.init();
    initNav();
    initReveal();
  });
})();
