/* UraPress – leuchtendes TiffCore-Logo als Werbe-Animation.
   Portiert aus LogoPunkte.tsx (tiffcore.ch / tiff-software-solutions.com).
   Rand = Gold, T = Grün/Mint, Schwung = Weiss. Additives Leuchten. */
(function () {
  "use strict";
  var DICHTE = 0.55, HELL = 1.7, GROSS = 1.6;

  function erzeugePunkte() {
    var samen = 11;
    var zufall = function () { return (samen = (samen * 16807) % 2147483647) / 2147483647; };
    var punkte = [];
    var GOLD = 0, MINT = 1, GRUEN = 2, WEISS = 3;
    function neu(x, y, z, f, g, e, u, d) {
      punkte.push({ x: x - 256, y: y - 256, z: z, sx: (zufall() - 0.5) * 2400, sy: (zufall() - 0.5) * 1700, sz: (zufall() - 0.15) * 1500, f: f, g: g, e: e, u: u, d: d, ph: zufall() * 6.2832 });
    }
    function rundRechteck(x0, y0, x1, y1, r, u) {
      var w = x1 - x0 - 2 * r, h = y1 - y0 - 2 * r, a = (Math.PI * r) / 2, d = u * (2 * w + 2 * h + 4 * a), t;
      if (d < w) return [x0 + r + d, y0];
      d -= w; if (d < a) { t = d / r; return [x1 - r + Math.sin(t) * r, y0 + r - Math.cos(t) * r]; }
      d -= a; if (d < h) return [x1, y0 + r + d];
      d -= h; if (d < a) { t = d / r; return [x1 - r + Math.cos(t) * r, y1 - r + Math.sin(t) * r]; }
      d -= a; if (d < w) return [x1 - r - d, y1];
      d -= w; if (d < a) { t = d / r; return [x0 + r - Math.sin(t) * r, y1 - r + Math.cos(t) * r]; }
      d -= a; if (d < h) return [x0, y1 - r - d];
      d -= h; t = d / r; return [x0 + r - Math.cos(t) * r, y0 + r - Math.sin(t) * r];
    }
    [[0, 700, 1.7], [1, 400, 1.25], [2, 230, 1.0]].forEach(function (p) {
      var k = p[0], n = p[1], gr = p[2], einzug = 6 + k * 24, radius = 100 - einzug * 0.55, n2 = Math.round(n * DICHTE);
      for (var i = 0; i < n2; i++) {
        var u = i / n2, xy = rundRechteck(einzug, einzug, 512 - einzug, 512 - einzug, radius, u);
        var wx = Math.sin(u * 37 + k * 1.7) * 3.2 + Math.sin(u * 91 + k) * 1.6 + (zufall() - 0.5) * 3;
        var wy = Math.cos(u * 29 + k * 2.3) * 3.2 + Math.cos(u * 83 + k) * 1.6 + (zufall() - 0.5) * 3;
        neu(xy[0] + wx, xy[1] + wy, -k * 16 + (zufall() - 0.5) * 6, zufall() < 0.18 ? MINT : GOLD, gr, 0, u, u * 0.9);
      }
    });
    var leiste = [80, 72, 432, 181], stamm = [201, 72, 311, 440];
    var fl = (leiste[2] - leiste[0]) * (leiste[3] - leiste[1]), fl2 = (stamm[2] - stamm[0]) * (stamm[3] - stamm[1]);
    for (var i = 0, n = Math.round(1150 * DICHTE); i < n; i++) {
      var r = zufall() * (fl + fl2) < fl ? leiste : stamm;
      var x = r[0] + zufall() * (r[2] - r[0]), y = r[1] + zufall() * (r[3] - r[1]), c = zufall();
      neu(x, y, (zufall() - 0.5) * 14, c < 0.5 ? GRUEN : c < 0.88 ? MINT : GOLD, 0.8 + zufall() * 0.7, 1, 0, 0.5 + zufall() * 0.9);
    }
    var ecken = [[80, 72], [432, 72], [432, 181], [311, 181], [311, 440], [201, 440], [201, 181], [80, 181]];
    var kanten = ecken.map(function (e, i) { var f = ecken[(i + 1) % 8]; return Math.hypot(f[0] - e[0], f[1] - e[1]); });
    var umfang = kanten.reduce(function (a, b) { return a + b; }, 0);
    for (var i = 0, n = Math.round(520 * DICHTE); i < n; i++) {
      var d = (i / n) * umfang, k = 0;
      while (d > kanten[k]) { d -= kanten[k]; k++; }
      var a = ecken[k], b = ecken[(k + 1) % 8], t = d / kanten[k];
      neu(a[0] + (b[0] - a[0]) * t + (zufall() - 0.5) * 2.5, a[1] + (b[1] - a[1]) * t + (zufall() - 0.5) * 2.5, 6, MINT, 1.5, 1, i / n, 0.5 + zufall() * 0.9);
    }
    var l1 = 71, l2 = (Math.PI / 2) * 65, l3 = 209.5, lg = l1 + l2 + l3;
    for (var i = 0, n = Math.round(240 * DICHTE); i < n; i++) {
      var u = i / n, d = u * lg, x, y;
      if (d < l1) { x = 119 + d; y = 125.5; }
      else if (d < l1 + l2) { var t = (d - l1) / 65; x = 190 + Math.sin(t) * 65; y = 190.5 - Math.cos(t) * 65; }
      else { x = 255; y = 190.5 + (d - l1 - l2); }
      var q = (zufall() - 0.5) * 15;
      neu(x + (y === 125.5 ? 0 : q), y + (y === 125.5 ? q : 0), 14, zufall() < 0.25 ? GOLD : WEISS, 0.95 + zufall() * 0.45, 2, u, 1.3 + u * 0.8);
    }
    return punkte;
  }

  function start(canvas) {
    var ctx = canvas.getContext("2d");
    if (!ctx) return;
    var ruhig = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var klemme = function (v, a, b) { return Math.min(b, Math.max(a, v)); };
    var farben = ["240,200,113", "95,227,160", "47,191,116", "255,255,255"].map(function (rgb) {
      var c = document.createElement("canvas"); c.width = c.height = 48;
      var g = c.getContext("2d"), v = g.createRadialGradient(24, 24, 0, 24, 24, 24);
      v.addColorStop(0, "rgba(255,255,255,1)");
      v.addColorStop(0.16, "rgba(" + rgb + ",1)");
      v.addColorStop(0.42, "rgba(" + rgb + ",0.32)");
      v.addColorStop(1, "rgba(" + rgb + ",0)");
      g.fillStyle = v; g.fillRect(0, 0, 48, 48); return c;
    });
    var punkte = erzeugePunkte();
    var breite = 0, hoehe = 0, dpr = 1;
    function messen() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      breite = canvas.clientWidth; hoehe = canvas.clientHeight;
      canvas.width = Math.round(breite * dpr); canvas.height = Math.round(hoehe * dpr);
    }
    var F = 1150;
    function zeichne(t) {
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, breite, hoehe);
      ctx.globalCompositeOperation = "lighter";
      var gier = ruhig ? 0.2 : Math.sin(t * 0.45) * 0.4, nick = ruhig ? -0.05 : Math.sin(t * 0.33 + 1) * 0.12;
      var cg = Math.cos(gier), sg = Math.sin(gier), cn = Math.cos(nick), sn = Math.sin(nick);
      var mass = Math.min(breite, hoehe) / 620, mitteX = breite / 2, mitteY = hoehe / 2;
      for (var idx = 0; idx < punkte.length; idx++) {
        var p = punkte[idx];
        var k = ruhig ? 1 : klemme((t - p.d) / 1.7, 0, 1);
        k = 1 - Math.pow(1 - k, 3);
        if (k <= 0.004) continue;
        var x = p.sx + (p.x - p.sx) * k + Math.sin(t * 0.9 + p.ph) * 1.7;
        var y = p.sy + (p.y - p.sy) * k + Math.cos(t * 0.8 + p.ph * 1.3) * 1.7;
        var z = p.sz + (p.z - p.sz) * k + Math.sin(t * 0.7 + p.ph * 2) * 1.36;
        var x1 = x * cg + z * sg, z1 = -x * sg + z * cg;
        var y1 = y * cn - z1 * sn, z2 = y * sn + z1 * cn;
        var s = F / (F + z2), welle = 0;
        if (p.e === 0) welle = 0.6 * Math.pow(Math.max(0, Math.sin(p.u * 12.566 - t * 1.5)), 9);
        else if (p.e === 1) welle = 0.7 * Math.pow(Math.max(0, Math.sin((p.y + 256) * 0.013 - t * 2.1)), 12);
        else welle = 0.45 * Math.pow(Math.max(0, Math.sin(p.u * 6.283 * 1.5 - t * 2.6)), 6);
        var basis = p.e === 0 ? 0.74 : p.e === 1 ? 0.6 : 0.7;
        var flimmer = 0.68 + 0.32 * Math.sin(t * (1.4 + (p.ph % 2)) + p.ph * 3);
        var d = p.g * mass * s * 9 * GROSS * (1 + welle * 0.55);
        if (d < 0.4) continue;
        ctx.globalAlpha = klemme((basis * flimmer + welle) * HELL, 0, 1) * Math.min(1, k * 1.6);
        ctx.drawImage(farben[p.f], mitteX + x1 * s * mass - d / 2, mitteY + y1 * s * mass - d / 2, d, d);
      }
      ctx.globalAlpha = 1;
    }
    var sichtbar = false, bild = 0, start0 = performance.now();
    function schleife(jetzt) { if (sichtbar) zeichne((jetzt - start0) / 1000); bild = requestAnimationFrame(schleife); }
    var beob = new IntersectionObserver(function (e) {
      sichtbar = e[0].isIntersecting; if (!sichtbar) return; messen(); if (ruhig) zeichne(99);
    });
    beob.observe(canvas);
    window.addEventListener("resize", function () { messen(); });
    if (!ruhig) bild = requestAnimationFrame(schleife);
  }

  function init() {
    var list = document.querySelectorAll("canvas.up-hads__glow");
    for (var i = 0; i < list.length; i++) start(list[i]);
  }
  // Engine auch für andere Skripte (z. B. das Logo-Aufblitzen) verfügbar machen.
  window.UraGlow = { start: start };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
