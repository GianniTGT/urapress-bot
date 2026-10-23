// ZaZu und Sara – Version 2 (mehr Details). Feste Zeichnungen: NICHT frei ändern, sonst sehen sie anders aus.
// ZaZu: British Shorthair, lilac (rauchig grau-rosa), kupfer-orange Augen, rundes Gesicht, dichtes Fell, 4 Zehen hinten.
// Sara: blonde lange Haare, blau-grüne Augen, Hoodie in Petrol.
const L = '#3B312C';                                   // Linie
const ZF = '#B9ACA6', ZF2 = '#A1938D', ZF3 = '#CFC4BF', ZLIGHT = '#EDE6E2', ZNOSE = '#C98C8E', ZPAD = '#D99AA0';
const ZEYE1 = '#F6B33E', ZEYE2 = '#D9781F';
const SKIN = '#F6D2B8', SKIN2 = '#E9B597', HAIR = '#EBC86E', HAIR2 = '#C99A3A', HAIR3 = '#F8E3A5';
const HOOD = '#1F7A7A', HOOD2 = '#165E5E', BALL = '#2F55C4';
const sw = (w = 4) => `stroke="${L}" stroke-width="${w}" stroke-linejoin="round" stroke-linecap="round"`;
let _uid = 0;
const uid = (p) => `${p}${++_uid}`;

function zDefs(id) {
  return `<defs>
  <radialGradient id="${id}h" cx="45%" cy="35%" r="75%"><stop offset="0" stop-color="${ZF3}"/><stop offset=".6" stop-color="${ZF}"/><stop offset="1" stop-color="${ZF2}"/></radialGradient>
  <radialGradient id="${id}b" cx="40%" cy="30%" r="80%"><stop offset="0" stop-color="${ZF3}"/><stop offset=".55" stop-color="${ZF}"/><stop offset="1" stop-color="${ZF2}"/></radialGradient>
  <radialGradient id="${id}e" cx="50%" cy="40%" r="60%"><stop offset="0" stop-color="${ZEYE1}"/><stop offset="1" stop-color="${ZEYE2}"/></radialGradient>
  </defs>`;
}

// Fellkante: Zacken entlang eines Bogens (für Wangen, Brust)
function tufts(cx, cy, rx, ry, a0, a1, n, depth) {
  let d = '';
  for (let i = 0; i <= n; i++) {
    const a = a0 + (a1 - a0) * i / n;
    const r = (i % 2) ? 1 + depth : 1;
    const x = cx + Math.cos(a) * rx * r, y = cy + Math.sin(a) * ry * r;
    d += (i ? ' L' : 'M') + x.toFixed(1) + ' ' + y.toFixed(1);
  }
  return d;
}

function zEye(id, cx, cy, mode, look) {
  const px = cx + look * 6;
  const cid = uid('c');
  let s = `<clipPath id="${cid}"><ellipse cx="${cx}" cy="${cy}" rx="17" ry="16"/></clipPath>`;
  s += `<ellipse cx="${cx}" cy="${cy}" rx="17" ry="16" fill="url(#${id}e)"/>`;
  if (mode === 'sleep') {
    return `<path d="M${cx - 15} ${cy + 2} Q${cx} ${cy + 12} ${cx + 15} ${cy + 2}" fill="none" ${sw(4)}/>`
      + `<path d="M${cx - 12} ${cy + 7} l-3 5 M${cx} ${cy + 9} l0 6 M${cx + 12} ${cy + 7} l3 5" ${sw(2)}/>`;
  }
  if (mode === 'wide') {
    s += `<ellipse cx="${px}" cy="${cy + 1}" rx="8" ry="11" fill="#1A1210"/>`;
    s += `<circle cx="${px - 4}" cy="${cy - 5}" r="4" fill="#fff"/><circle cx="${px + 4}" cy="${cy + 5}" r="1.8" fill="#fff" opacity=".8"/>`;
  } else {
    s += `<ellipse cx="${px}" cy="${cy + 3}" rx="4.5" ry="10" fill="#1A1210"/><circle cx="${px - 3}" cy="${cy - 1}" r="2.8" fill="#fff"/>`;
    // Augenlid: halb zu (flat) oder schräg nach innen (grumpy)
    const inner = cx < 0 ? 1 : -1;                      // Richtung zur Gesichtsmitte
    const tilt = mode === 'grumpy' ? 7 : 0;
    const yIn = cy - 3 + tilt, yOut = cy - 3 - tilt;
    const xIn = cx + inner * 19, xOut = cx - inner * 19;
    s += `<g clip-path="url(#${cid})"><path d="M${xOut} ${cy - 22} L${xIn} ${cy - 22} L${xIn} ${yIn} L${xOut} ${yOut} Z" fill="${ZF2}"/>`;
    s += `<path d="M${xOut} ${yOut} L${xIn} ${yIn}" ${sw(3.5)}/></g>`;
  }
  s += `<ellipse cx="${cx}" cy="${cy}" rx="17" ry="16" fill="none" ${sw(3.5)}/>`;
  return s;
}

function zazuHead(id, mode = 'flat', look = 0, mouth = 'flat') {
  let s = '';
  // Ohren (klein, rund, weit auseinander – British Shorthair)
  for (const k of [-1, 1]) {
    s += `<path d="M${k * 70} -24 Q${k * 82} -84 ${k * 32} -66 Z" fill="${ZF}" ${sw()}/>`;
    s += `<path d="M${k * 62} -32 Q${k * 70} -70 ${k * 40} -60 Z" fill="${ZPAD}" opacity=".85"/>`;
    s += `<path d="M${k * 58} -40 l${k * -6} -10 M${k * 52} -36 l${k * -8} -8" stroke="${ZLIGHT}" stroke-width="2" stroke-linecap="round"/>`;
  }
  // Kopf mit Wangen-Fell
  s += `<path d="${tufts(0, 4, 88, 66, 0.15 * Math.PI, 0.85 * Math.PI, 14, 0.07)}" fill="url(#${id}h)" ${sw()}/>`;
  s += `<ellipse cx="0" cy="0" rx="84" ry="66" fill="url(#${id}h)" ${sw()}/>`;
  s += `<path d="${tufts(0, 4, 86, 64, 0.18 * Math.PI, 0.82 * Math.PI, 14, 0.06)}" fill="url(#${id}h)" stroke="none"/>`;
  // Stirnzeichnung (dezentes «M») und Fellstriche
  s += `<path d="M-18 -58 Q-14 -46 -18 -36 M-4 -62 Q0 -50 -4 -38 M10 -62 Q14 -50 10 -38 M24 -58 Q28 -46 24 -36" stroke="${ZF2}" stroke-width="3.5" fill="none" stroke-linecap="round"/>`;
  s += `<path d="M-66 -6 l-10 4 M-68 8 l-10 6 M66 -6 l10 4 M68 8 l10 6" stroke="${ZF2}" stroke-width="2.5" stroke-linecap="round"/>`;
  // Schnauze
  s += `<ellipse cx="-16" cy="24" rx="23" ry="16" fill="${ZLIGHT}"/><ellipse cx="16" cy="24" rx="23" ry="16" fill="${ZLIGHT}"/><ellipse cx="0" cy="40" rx="19" ry="10" fill="${ZLIGHT}"/>`;
  for (const [x, y] of [[-24, 20], [-16, 26], [-28, 28], [24, 20], [16, 26], [28, 28]]) s += `<circle cx="${x}" cy="${y}" r="1.6" fill="${ZF2}"/>`;
  s += zEye(id, -32, -6, mode, look) + zEye(id, 32, -6, mode, look);
  // Nase
  s += `<path d="M-9 9 Q0 4 9 9 Q4 19 0 19 Q-4 19 -9 9 Z" fill="${ZNOSE}" ${sw(3)}/><ellipse cx="-2" cy="9" rx="3" ry="1.6" fill="#fff" opacity=".6"/>`;
  if (mouth === 'w') s += `<path d="M0 19 Q-6 29 -13 25 M0 19 Q6 29 13 25" fill="none" ${sw(3)}/>`;
  else if (mouth === 'o') s += `<path d="M0 19 L0 23" ${sw(3)}/><ellipse cx="0" cy="31" rx="6" ry="7" fill="#7a3b3b" ${sw(3)}/>`;
  else s += `<path d="M0 19 L0 25 M-12 32 Q0 25 12 32" fill="none" ${sw(3)}/>`;
  // Schnurrhaare
  s += `<path d="M-38 22 Q-64 14 -92 12 M-38 28 Q-64 28 -92 32 M-38 34 Q-60 40 -86 48 M38 22 Q64 14 92 12 M38 28 Q64 28 92 32 M38 34 Q60 40 86 48" stroke="${L}" stroke-width="1.8" fill="none" stroke-linecap="round" opacity=".85"/>`;
  return s;
}

function zazuSit(x, y, opt = {}) {
  const { mode = 'flat', look = 0, mouth = 'flat', sc = 1, paw = false } = opt;
  const id = uid('z');
  let s = `<g transform="translate(${x} ${y}) scale(${sc})">` + zDefs(id);
  // Schatten
  s += `<ellipse cx="6" cy="202" rx="104" ry="12" fill="#000" opacity=".12"/>`;
  // Schwanz: dick, mit leicht dunkleren Ringen
  const tail = 'M70 152 Q138 152 124 98 Q116 72 96 84';
  s += `<path d="${tail}" fill="none" stroke="${L}" stroke-width="32" stroke-linecap="round"/><path d="${tail}" fill="none" stroke="${ZF}" stroke-width="24" stroke-linecap="round"/>`;
  s += `<path d="M118 140 l10 -6 M126 118 l12 -2 M120 96 l12 4" stroke="${ZF2}" stroke-width="4" stroke-linecap="round"/>`;
  // Körper (rund, «Brotlaib»)
  s += `<ellipse cx="0" cy="116" rx="90" ry="88" fill="url(#${id}b)" ${sw()}/>`;
  // Brustfell (Halskrause)
  s += `<path d="${tufts(0, 64, 46, 34, 0.05 * Math.PI, 0.95 * Math.PI, 12, 0.18)}" fill="${ZLIGHT}" stroke="none"/>`;
  s += `<ellipse cx="0" cy="98" rx="40" ry="48" fill="${ZLIGHT}"/>`;
  s += `<path d="M-14 84 l-6 8 M0 90 l0 10 M14 84 l6 8 M-8 114 l-4 8 M8 114 l4 8" stroke="#D8CEC9" stroke-width="2.5" stroke-linecap="round"/>`;
  // Flanken-Fellstriche
  s += `<path d="M-74 104 l-8 6 M-78 128 l-8 4 M74 104 l8 6" stroke="${ZF2}" stroke-width="3" stroke-linecap="round"/>`;
  const frontPaw = (px) => `<path d="M${px} 132 L${px} 184" stroke="${ZF2}" stroke-width="3"/><ellipse cx="${px + (px < 0 ? 12 : -12)}" cy="192" rx="24" ry="13" fill="${ZLIGHT}" ${sw()}/><path d="M${px + (px < 0 ? 4 : -4)} 186 l0 10 M${px + (px < 0 ? 14 : -14)} 186 l0 10" ${sw(2.5)}/>`;
  if (!paw) {
    s += frontPaw(-36) + frontPaw(36);
  } else {
    // Hinterpfote hochgehalten: 4 Zehenballen – der Witz
    s += `<path d="M44 152 Q114 134 126 78" fill="none" stroke="${L}" stroke-width="44" stroke-linecap="round"/><path d="M44 152 Q114 134 126 78" fill="none" stroke="${ZF}" stroke-width="36" stroke-linecap="round"/>`;
    s += `<ellipse cx="134" cy="44" rx="40" ry="36" fill="${ZLIGHT}" ${sw()}/>`;
    s += `<path d="M115 59 Q134 38 153 59 Q151 74 134 74 Q117 74 115 59 Z" fill="${ZPAD}" ${sw(2.5)}/>`;
    [[107, 37], [122, 21], [146, 21], [161, 37]].forEach(([a, b]) => s += `<ellipse cx="${a}" cy="${b}" rx="8" ry="10" fill="${ZPAD}" ${sw(2.5)}/>`);
    s += frontPaw(-36);
  }
  s += zazuHead(id, mode, look, mouth) + '</g>';
  return s;
}

function sara(x, y, opt = {}) {
  const { mouth = 'smile', ball = true, sc = 1, brow = 0 } = opt;
  const id = uid('s');
  let s = `<g transform="translate(${x} ${y}) scale(${sc})"><defs>
    <linearGradient id="${id}hr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${HAIR3}"/><stop offset=".45" stop-color="${HAIR}"/><stop offset="1" stop-color="${HAIR2}"/></linearGradient>
    <linearGradient id="${id}hd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${HOOD}"/><stop offset="1" stop-color="${HOOD2}"/></linearGradient>
    <radialGradient id="${id}sk" cx="45%" cy="40%" r="70%"><stop offset="0" stop-color="#FBE0CC"/><stop offset="1" stop-color="${SKIN}"/></radialGradient></defs>`;
  // Schatten
  s += `<ellipse cx="0" cy="214" rx="78" ry="10" fill="#000" opacity=".1"/>`;
  // Haare hinten (lang, blond)
  s += `<path d="M-62 -14 Q-72 70 -60 150 Q-40 162 -26 150 L26 150 Q40 162 60 150 Q72 70 62 -14 Q44 -76 0 -76 Q-44 -76 -62 -14 Z" fill="url(#${id}hr)" ${sw(3.5)}/>`;
  s += `<path d="M-52 20 Q-56 80 -48 140 M-40 40 Q-42 96 -36 146 M52 20 Q56 80 48 140 M40 40 Q42 96 36 146" stroke="${HAIR2}" stroke-width="2.5" fill="none" stroke-linecap="round" opacity=".8"/>`;
  // Hoodie
  s += `<path d="M-66 212 Q-66 124 -28 104 L28 104 Q66 124 66 212 Z" fill="url(#${id}hd)" ${sw(3.5)}/>`;
  s += `<path d="M-28 104 Q0 132 28 104" fill="${HOOD2}" ${sw(3)}/>`;
  s += `<path d="M-10 122 L-12 160 M10 122 L12 160" stroke="#F2F2F2" stroke-width="3" stroke-linecap="round"/><circle cx="-12" cy="162" r="3" fill="#F2F2F2"/><circle cx="12" cy="162" r="3" fill="#F2F2F2"/>`;
  s += `<path d="M-40 176 Q0 186 40 176 L40 204 Q0 212 -40 204 Z" fill="${HOOD2}" opacity=".7"/>`;
  // Hals, Ohren, Gesicht
  s += `<path d="M-12 76 L-12 108 Q0 114 12 108 L12 76 Z" fill="${SKIN2}"/>`;
  s += `<ellipse cx="-49" cy="22" rx="8" ry="12" fill="${SKIN}" ${sw(3)}/><ellipse cx="49" cy="22" rx="8" ry="12" fill="${SKIN}" ${sw(3)}/>`;
  s += `<ellipse cx="0" cy="20" rx="48" ry="57" fill="url(#${id}sk)" ${sw(3.5)}/>`;
  // Augen: Weiss, Iris blau-grün, Pupille, Glanz, Wimpern
  for (const k of [-1, 1]) {
    const ex = k * 18;
    s += `<ellipse cx="${ex}" cy="20" rx="9" ry="10" fill="#fff" ${sw(2.5)}/>`;
    s += `<circle cx="${ex}" cy="21" r="6.5" fill="#3E8E9A"/><circle cx="${ex}" cy="21" r="3.4" fill="#14181A"/><circle cx="${ex - 2.2}" cy="18.5" r="2" fill="#fff"/>`;
    s += `<path d="M${ex - 10} 15 Q${ex} 7 ${ex + 10} 15" fill="none" ${sw(3)}/>`;
    s += `<path d="M${ex + k * 9} 13 l${k * 4} -4 M${ex + k * 6} 10 l${k * 2} -5" ${sw(2)}/>`;
    // Augenbrauen (hellbraun), brow>0 = ernst
    s += `<path d="M${ex - k * 10} ${2 + (k < 0 ? brow : brow)} Q${ex} ${-3 - brow} ${ex + k * 10} ${2 - brow}" fill="none" stroke="#B0844A" stroke-width="3.5" stroke-linecap="round"/>`;
  }
  s += `<path d="M0 26 Q-3 36 2 38" fill="none" stroke="${SKIN2}" stroke-width="3" stroke-linecap="round"/>`;
  s += `<ellipse cx="-30" cy="40" rx="9" ry="5" fill="#F2A0A0" opacity=".55"/><ellipse cx="30" cy="40" rx="9" ry="5" fill="#F2A0A0" opacity=".55"/>`;
  if (mouth === 'smile') s += `<path d="M-14 47 Q0 61 14 47 Q0 53 -14 47 Z" fill="#C4554F" ${sw(2.5)}/><path d="M-8 51 Q0 54 8 51" stroke="#fff" stroke-width="2.5" fill="none"/>`;
  else if (mouth === 'o') s += `<ellipse cx="0" cy="52" rx="7" ry="8" fill="#9B3F3A" ${sw(2.5)}/>`;
  else s += `<path d="M-10 52 Q0 48 10 52" fill="none" ${sw(3)}/>`;
  // Pony / Seitenscheitel
  s += `<path d="M-50 6 Q-48 -54 2 -58 Q50 -54 52 4 Q44 -20 22 -30 Q6 -12 -20 -18 Q-36 -10 -50 6 Z" fill="url(#${id}hr)" ${sw(3.5)}/>`;
  s += `<path d="M-30 -40 Q-12 -30 4 -36 M10 -46 Q26 -34 34 -18 M-40 -20 Q-30 -26 -18 -24" stroke="${HAIR3}" stroke-width="3" fill="none" stroke-linecap="round"/>`;
  if (ball) {
    s += `<circle cx="0" cy="170" r="40" fill="${BALL}" ${sw(3.5)}/><path d="M-26 150 Q-10 140 6 144" stroke="#7FA0F0" stroke-width="5" fill="none" stroke-linecap="round" opacity=".7"/>`;
    s += `<circle cx="-12" cy="154" r="6" fill="#0f1d4a"/><circle cx="6" cy="150" r="6" fill="#0f1d4a"/><circle cx="-2" cy="170" r="7" fill="#0f1d4a"/>`;
    s += `<ellipse cx="-38" cy="174" rx="15" ry="12" fill="${SKIN}" ${sw(3)}/><ellipse cx="38" cy="174" rx="15" ry="12" fill="${SKIN}" ${sw(3)}/>`;
  }
  return s + '</g>';
}


// ---- Weitere Körper-Posen (Ursprung 0,0 = Mitte des Kopfes, wie bei zazuSit) ----

// Liegend («Brotlaib»), Kopf vorne links, Pfoten eingezogen, Schwanz um den Körper
function zazuLie(x, y, opt = {}) {
  const { mode = 'flat', look = 0, mouth = 'flat', sc = 1 } = opt;
  const id = uid('z');
  let s = `<g transform="translate(${x} ${y}) scale(${sc})">` + zDefs(id);
  s += `<ellipse cx="70" cy="122" rx="160" ry="12" fill="#000" opacity=".12"/>`;
  s += `<ellipse cx="80" cy="62" rx="150" ry="62" fill="url(#${id}b)" ${sw()}/>`;
  s += `<path d="M150 30 l12 -4 M170 50 l12 0 M40 22 l6 -10 M90 14 l4 -10" stroke="${ZF2}" stroke-width="3" stroke-linecap="round"/>`;
  const tail = 'M222 82 Q236 120 170 122 Q110 124 70 118';
  s += `<path d="${tail}" fill="none" stroke="${L}" stroke-width="30" stroke-linecap="round"/><path d="${tail}" fill="none" stroke="${ZF}" stroke-width="22" stroke-linecap="round"/>`;
  s += `<path d="M190 112 l4 10 M150 114 l2 10 M110 112 l2 10" stroke="${ZF2}" stroke-width="4" stroke-linecap="round"/>`;
  s += `<ellipse cx="-22" cy="110" rx="30" ry="13" fill="${ZLIGHT}" ${sw()}/><ellipse cx="34" cy="114" rx="30" ry="13" fill="${ZLIGHT}" ${sw()}/>`;
  s += `<path d="M-34 106 l0 9 M-22 105 l0 10 M22 110 l0 9 M34 109 l0 10" ${sw(2.5)}/>`;
  s += zazuHead(id, mode, look, mouth) + '</g>';
  return s;
}

// Schlafend: eingerollt, Kopf auf den Pfoten, Augen zu, «z z z»
function zazuSleep(x, y, opt = {}) {
  const { sc = 1 } = opt;
  const id = uid('z');
  let s = `<g transform="translate(${x} ${y}) scale(${sc})">` + zDefs(id);
  s += `<ellipse cx="40" cy="120" rx="150" ry="13" fill="#000" opacity=".12"/>`;
  s += `<ellipse cx="60" cy="58" rx="132" ry="66" fill="url(#${id}b)" ${sw()}/>`;
  s += `<path d="M120 10 l10 -6 M150 34 l12 -2 M70 0 l4 -10" stroke="${ZF2}" stroke-width="3" stroke-linecap="round"/>`;
  const tail = 'M180 92 Q170 132 90 128 Q20 126 -40 104';
  s += `<path d="${tail}" fill="none" stroke="${L}" stroke-width="32" stroke-linecap="round"/><path d="${tail}" fill="none" stroke="${ZF}" stroke-width="24" stroke-linecap="round"/>`;
  s += `<path d="M150 118 l4 10 M100 122 l2 10 M50 120 l0 10" stroke="${ZF2}" stroke-width="4" stroke-linecap="round"/>`;
  s += `<ellipse cx="-10" cy="74" rx="40" ry="16" fill="${ZLIGHT}" ${sw()}/><path d="M-26 68 l0 10 M-12 66 l0 12 M4 68 l0 10" ${sw(2.5)}/>`;
  s += `<g transform="translate(0 4) rotate(-8)">${zazuHead(id, 'sleep', 0, 'flat')}</g>`;
  s += `<text x="70" y="-70" font-family="Comic Neue, sans-serif" font-weight="700" fill="${ZF2}"><tspan font-size="30">z</tspan><tspan dx="6" dy="-18" font-size="38">z</tspan><tspan dx="6" dy="-22" font-size="48">Z</tspan></text>`;
  return s + '</g>';
}

// Laufend: Seitenansicht nach rechts, Beine im Schritt, Schwanz hoch, Kopf schaut zum Leser
function zazuWalk(x, y, opt = {}) {
  const { mode = 'flat', look = 1, mouth = 'flat', sc = 1 } = opt;
  const id = uid('z');
  let s = `<g transform="translate(${x} ${y}) scale(${sc})">` + zDefs(id);
  s += `<ellipse cx="-90" cy="196" rx="140" ry="12" fill="#000" opacity=".12"/>`;
  const tail = 'M-200 70 Q-250 30 -232 -30 Q-226 -52 -206 -50';
  s += `<path d="${tail}" fill="none" stroke="${L}" stroke-width="30" stroke-linecap="round"/><path d="${tail}" fill="none" stroke="${ZF}" stroke-width="22" stroke-linecap="round"/>`;
  s += `<path d="M-238 10 l-12 2 M-236 -20 l-12 -4" stroke="${ZF2}" stroke-width="4" stroke-linecap="round"/>`;
  // Beine hinten (dunkler) und vorne, im Schritt
  const leg = (x1, y1, x2, y2, c) => `<path d="M${x1} ${y1} L${x2} ${y2}" stroke="${L}" stroke-width="30" stroke-linecap="round"/><path d="M${x1} ${y1} L${x2} ${y2}" stroke="${c}" stroke-width="22" stroke-linecap="round"/><ellipse cx="${x2 + 6}" cy="${y2 + 8}" rx="18" ry="10" fill="${ZLIGHT}" ${sw(3.5)}/>`;
  s += leg(-170, 110, -200, 180, ZF2) + leg(-30, 110, -6, 180, ZF2);
  s += `<ellipse cx="-100" cy="92" rx="122" ry="64" fill="url(#${id}b)" ${sw()}/>`;
  s += `<path d="M-160 60 l-8 6 M-120 44 l-4 -8 M-60 46 l2 -8 M-140 120 l-6 8" stroke="${ZF2}" stroke-width="3" stroke-linecap="round"/>`;
  s += `<ellipse cx="-40" cy="112" rx="36" ry="30" fill="${ZLIGHT}"/>`;
  s += leg(-150, 120, -128, 184, ZF) + leg(-14, 118, -40, 184, ZF);
  s += zazuHead(id, mode, look, mouth) + '</g>';
  return s;
}

// ---- Gianni: kurze dunkle Haare mit grauen Schläfen, kurzer Bart, blaues Hemd ----
const GHAIR = '#3A2E28', GGREY = '#8E8680', GSHIRT = '#2C4F86', GSHIRT2 = '#223F6C';
function gianni(x, y, opt = {}) {
  const { mouth = 'smile', sc = 1, brow = 0 } = opt;
  const id = uid('g');
  let s = `<g transform="translate(${x} ${y}) scale(${sc})"><defs>
    <radialGradient id="${id}sk" cx="45%" cy="40%" r="70%"><stop offset="0" stop-color="#F5D3B6"/><stop offset="1" stop-color="#E7B894"/></radialGradient>
    <linearGradient id="${id}sh" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${GSHIRT}"/><stop offset="1" stop-color="${GSHIRT2}"/></linearGradient></defs>`;
  s += `<ellipse cx="0" cy="214" rx="86" ry="10" fill="#000" opacity=".1"/>`;
  // Hemd mit Kragen und Knopfleiste
  s += `<path d="M-78 212 Q-80 120 -30 100 L30 100 Q80 120 78 212 Z" fill="url(#${id}sh)" ${sw(3.5)}/>`;
  s += `<path d="M-24 100 L0 132 L24 100" fill="#fff" ${sw(3)}/><path d="M-24 100 L-10 128 L-30 122 Z M24 100 L10 128 L30 122 Z" fill="${GSHIRT}" ${sw(3)}/>`;
  s += `<path d="M0 132 L0 210" stroke="${GSHIRT2}" stroke-width="3"/><circle cx="0" cy="150" r="3" fill="#E8E8E8"/><circle cx="0" cy="176" r="3" fill="#E8E8E8"/><circle cx="0" cy="202" r="3" fill="#E8E8E8"/>`;
  s += `<path d="M-46 180 l-6 30 M46 180 l6 30" stroke="${GSHIRT2}" stroke-width="3" stroke-linecap="round"/>`;
  // Hals, Ohren, Gesicht
  s += `<path d="M-14 74 L-14 104 Q0 112 14 104 L14 74 Z" fill="#E2AE8A"/>`;
  s += `<ellipse cx="-52" cy="20" rx="9" ry="13" fill="#EDBF9C" ${sw(3)}/><ellipse cx="52" cy="20" rx="9" ry="13" fill="#EDBF9C" ${sw(3)}/>`;
  s += `<path d="M-50 -6 Q-52 60 -26 78 Q0 92 26 78 Q52 60 50 -6 Q50 -50 0 -52 Q-50 -50 -50 -6 Z" fill="url(#${id}sk)" ${sw(3.5)}/>`;
  // kurzer Bart (Kinn + Wangen) und Schnurrbart
  s += `<path d="M-46 26 Q-44 64 -24 76 Q0 90 24 76 Q44 64 46 26 Q40 52 24 58 Q0 66 -24 58 Q-40 52 -46 26 Z" fill="${GHAIR}" opacity=".85"/>`;
  s += `<path d="M-16 44 Q0 38 16 44 Q10 48 0 47 Q-10 48 -16 44 Z" fill="${GHAIR}"/>`;
  for (const [a, b] of [[-36, 50], [-30, 60], [30, 60], [36, 50], [-20, 70], [20, 70]]) s += `<circle cx="${a}" cy="${b}" r="1.6" fill="#5A4A40"/>`;
  // Augen (braun), Augenbrauen kräftig
  for (const k of [-1, 1]) {
    const ex = k * 19;
    s += `<ellipse cx="${ex}" cy="16" rx="8" ry="7.5" fill="#fff" ${sw(2.5)}/><circle cx="${ex}" cy="17" r="5" fill="#6B4226"/><circle cx="${ex}" cy="17" r="2.6" fill="#14100E"/><circle cx="${ex - 2}" cy="15" r="1.6" fill="#fff"/>`;
    s += `<path d="M${ex - k * 12} ${4 + brow} Q${ex} ${-4 - brow} ${ex + k * 12} ${2 - brow}" fill="none" stroke="${GHAIR}" stroke-width="5.5" stroke-linecap="round"/>`;
  }
  s += `<path d="M2 20 Q-4 34 4 36" fill="none" stroke="#C99577" stroke-width="3" stroke-linecap="round"/>`;
  if (mouth === 'smile') s += `<path d="M-13 51 Q0 62 13 51 Q0 56 -13 51 Z" fill="#B5524C" ${sw(2.5)}/>`;
  else if (mouth === 'o') s += `<ellipse cx="0" cy="54" rx="6" ry="7" fill="#8E3A35" ${sw(2.5)}/>`;
  else s += `<path d="M-10 54 Q0 50 10 54" fill="none" ${sw(3)}/>`;
  // Haare kurz, graue Schläfen
  s += `<path d="M-50 4 Q-56 -50 -6 -60 Q46 -62 52 0 Q46 -24 40 -30 Q10 -40 -20 -34 Q-40 -30 -44 -14 Z" fill="${GHAIR}" ${sw(3.5)}/>`;
  s += `<path d="M-50 4 Q-52 -10 -46 -20 L-44 -4 Z M50 4 Q52 -10 46 -20 L44 -4 Z" fill="${GGREY}"/>`;
  s += `<path d="M-30 -48 Q-10 -56 14 -52 M-20 -40 Q0 -46 22 -42" stroke="#5A4A40" stroke-width="2.5" fill="none" stroke-linecap="round"/>`;
  return s + '</g>';
}
