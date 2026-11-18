// Open Mind: theme switch (auto, light, dark) and the phone menu. Works without it; pages are static.
(function () {
  var root = document.documentElement, btn = document.getElementById('theme'), label = document.getElementById('theme-label');
  function get() { try { return localStorage.getItem('om-theme'); } catch (e) { return null; } }
  function set(v) { try { v ? localStorage.setItem('om-theme', v) : localStorage.removeItem('om-theme'); } catch (e) {} }
  function show(v) {
    if (v) root.setAttribute('data-theme', v); else root.removeAttribute('data-theme');
    var word = v === 'light' ? 'Light' : v === 'dark' ? 'Dark' : 'Auto';
    if (label) label.textContent = word;
    if (btn) btn.setAttribute('aria-label', 'Colour theme: ' + word.toLowerCase() + '. Change');
  }
  show(root.getAttribute('data-theme') || get());
  if (btn) btn.addEventListener('click', function () {
    var cur = root.getAttribute('data-theme'), next = cur === null ? 'light' : cur === 'light' ? 'dark' : null;
    set(next); show(next);
  });
  var head = document.querySelector('.head'), menu = document.getElementById('menu-btn');
  if (menu && head) {
    menu.addEventListener('click', function () {
      var open = head.classList.toggle('open');
      menu.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && head.classList.contains('open')) { head.classList.remove('open'); menu.setAttribute('aria-expanded', 'false'); menu.focus(); }
    });
  }
})();
