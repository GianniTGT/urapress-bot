/* UraPress – das leuchtende Tiff-Logo blitzt zufällig gross in der Mitte auf
   (Pop + leichtes Drehen), bleibt kurz und verschwindet wieder. Einmal pro Besuch. */
(function () {
  "use strict";
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  try { if (sessionStorage.getItem("ura_flash")) return; } catch (e) {}

  function flash() {
    try { sessionStorage.setItem("ura_flash", "1"); } catch (e) {}
    var wrap = document.createElement("div");
    wrap.className = "ura-flash";
    var a = document.createElement("a");
    a.href = "https://tiffcore.ch/?utm_source=urapress&utm_medium=flash&utm_campaign=logo";
    a.target = "_blank";
    a.rel = "sponsored noopener";
    a.setAttribute("aria-label", "TiffCore");
    var c = document.createElement("canvas");
    c.className = "up-hads__glow ura-flash__canvas";
    a.appendChild(c);
    wrap.appendChild(a);
    document.body.appendChild(wrap);
    if (window.UraGlow && window.UraGlow.start) window.UraGlow.start(c);
    // kurz zeigen, dann sanft ausblenden und entfernen
    setTimeout(function () { wrap.classList.add("is-on"); }, 30);
    setTimeout(function () { wrap.classList.remove("is-on"); wrap.classList.add("is-off"); }, 3600);
    setTimeout(function () { if (wrap.parentNode) wrap.parentNode.removeChild(wrap); }, 4600);
  }

  // zufällig 15–45 s nachdem die Seite da ist
  var delay = 15000 + Math.random() * 30000;
  setTimeout(flash, delay);
})();
