/**
 * Client-side hints for required fields, email shape, password strength.
 * Authoritative validation remains on the server (WTForms).
 */
(function () {
  const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const strongPw =
    /^(?=.{8,128}$)(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).+$/;

  function mark(el, bad) {
    if (!el) return;
    el.classList.toggle("input-error", bad);
  }

  function validateEmail(input) {
    const v = (input.value || "").trim();
    mark(input, v.length > 0 && !emailRe.test(v));
  }

  function validatePassword(input) {
    const v = input.value || "";
    mark(input, v.length > 0 && !strongPw.test(v));
  }

  function attachForm(id, rules) {
    const form = document.getElementById(id);
    if (!form) return;
    form.addEventListener(
      "submit",
      function (e) {
        let ok = true;
        rules.forEach(function (r) {
          const el = form.querySelector(r.sel);
          if (!el) return;
          r.check(el);
          if (el.classList.contains("input-error")) ok = false;
        });
        if (!ok) e.preventDefault();
      },
      { passive: false },
    );
    rules.forEach(function (r) {
      const el = form.querySelector(r.sel);
      if (!el || !r.live) return;
      el.addEventListener(r.live, function () {
        r.check(el);
      });
    });
  }

  attachForm("login-form", [
    {
      sel: 'input[name="email"]',
      live: "blur",
      check: validateEmail,
    },
  ]);

  attachForm("register-form", [
    {
      sel: 'input[name="email"]',
      live: "blur",
      check: validateEmail,
    },
    {
      sel: 'input[name="password"]',
      live: "input",
      check: validatePassword,
    },
  ]);
})();
