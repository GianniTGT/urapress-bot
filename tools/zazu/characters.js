// ZaZu und Sara – feste Zeichnungen. NICHT frei ändern, sonst sieht ZaZu anders aus.
const FUR='#BCAEA4', FURD='#A3958C', LIGHT='#ECE3DC', NOSE='#D9958F', EYE='#E9A33A', LINE='#3B312C', PAD='#E7A2A6';
const SKIN='#F3CBAE', HAIR='#2A2220', SHIRT='#1E1E24', BALL='#2F55C4';
const sw='stroke="'+LINE+'" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"';

function eye(cx,cy,mode,look=0){
  let s=`<circle cx="${cx}" cy="${cy}" r="15" fill="${EYE}" ${sw}/>`;
  const px=cx+look*6;
  if(mode==='wide'){ s+=`<ellipse cx="${px}" cy="${cy+1}" rx="7" ry="10" fill="#111"/><circle cx="${px-3}" cy="${cy-5}" r="3.5" fill="#fff"/>`; }
  else { s+=`<ellipse cx="${px}" cy="${cy+3}" rx="4" ry="9" fill="#111"/><circle cx="${px-2}" cy="${cy-1}" r="2.5" fill="#fff"/>`;
    // Lid halb zu (unbeeindruckt) bzw. schräg (beleidigt)
    const k = mode==='grumpy' ? (cx<0?-1:1) : 0; // innen tiefer
    const y1=cy-2+(k<0?-4:4)*Math.abs(k), y2=cy-2-(k<0?-4:4)*Math.abs(k);
    s+=`<path d="M${cx-18} ${cy-20} L${cx+18} ${cy-20} L${cx+18} ${cx<0?y2:y1} L${cx-18} ${cx<0?y1:y2} Z" fill="${FUR}"/>`;
    s+=`<path d="M${cx-16} ${cx<0?y1:y2} L${cx+16} ${cx<0?y2:y1}" ${sw}/>`;
  }
  return s;
}
function zazuHead(mode='flat',look=0,mouth='flat'){
  let s='';
  // Ohren
  s+=`<path d="M-66 -28 Q-76 -86 -34 -64 Z" fill="${FUR}" ${sw}/><path d="M-58 -36 Q-64 -70 -42 -60 Z" fill="${PAD}"/>`;
  s+=`<path d="M66 -28 Q76 -86 34 -64 Z" fill="${FUR}" ${sw}/><path d="M58 -36 Q64 -70 42 -60 Z" fill="${PAD}"/>`;
  s+=`<ellipse cx="0" cy="0" rx="80" ry="66" fill="${FUR}" ${sw}/>`;
  // Stirnstreifen
  s+=`<path d="M-14 -56 Q-10 -46 -14 -38 M0 -60 Q4 -50 0 -40 M14 -56 Q18 -46 14 -38" stroke="${FURD}" stroke-width="4" fill="none" stroke-linecap="round"/>`;
  // Schnauze
  s+=`<ellipse cx="-15" cy="22" rx="21" ry="15" fill="${LIGHT}"/><ellipse cx="15" cy="22" rx="21" ry="15" fill="${LIGHT}"/><ellipse cx="0" cy="38" rx="18" ry="9" fill="${LIGHT}"/>`;
  s+=eye(-30,-6,mode,look)+eye(30,-6,mode,look);
  s+=`<path d="M-8 9 Q0 5 8 9 Q3 18 0 18 Q-3 18 -8 9 Z" fill="${NOSE}" ${sw.replace('4','3')}/>`;
  if(mouth==='w') s+=`<path d="M0 18 Q-5 27 -12 24 M0 18 Q5 27 12 24" fill="none" ${sw.replace('4','3')}/>`;
  else if(mouth==='o') s+=`<ellipse cx="0" cy="30" rx="6" ry="7" fill="#7a3b3b" ${sw.replace('4','3')}/>`;
  else s+=`<path d="M0 18 L0 24 M-11 31 Q0 25 11 31" fill="none" ${sw.replace('4','3')}/>`;
  // Schnurrhaare
  s+=`<path d="M-36 20 L-86 12 M-36 26 L-86 30 M36 20 L86 12 M36 26 L86 30" stroke="${LINE}" stroke-width="2" stroke-linecap="round"/>`;
  return s;
}
function zazuSit(x,y,opt={}){
  const {mode='flat',look=0,mouth='flat',sc=1,paw=false}=opt;
  let s=`<g transform="translate(${x} ${y}) scale(${sc})">`;
  // Schwanz
  s+=`<path d="M70 150 Q130 150 118 100 Q112 80 96 88" fill="none" stroke="${LINE}" stroke-width="26" stroke-linecap="round"/><path d="M70 150 Q130 150 118 100 Q112 80 96 88" fill="none" stroke="${FUR}" stroke-width="18" stroke-linecap="round"/>`;
  s+=`<ellipse cx="0" cy="112" rx="84" ry="84" fill="${FUR}" ${sw}/>`;
  s+=`<ellipse cx="0" cy="92" rx="40" ry="46" fill="${LIGHT}"/>`;
  if(!paw){
    s+=`<path d="M-34 130 L-34 182 M34 130 L34 182" stroke="${FURD}" stroke-width="3" fill="none"/>`;
    s+=`<ellipse cx="-22" cy="190" rx="22" ry="12" fill="${LIGHT}" ${sw}/><ellipse cx="22" cy="190" rx="22" ry="12" fill="${LIGHT}" ${sw}/>`;
  } else {
    // Hinterpfote hochgehalten: grosse Pfote mit 4 Zehenballen, frei neben dem Kopf
    s+=`<path d="M44 150 Q112 132 124 76" fill="none" stroke="${LINE}" stroke-width="40" stroke-linecap="round"/><path d="M44 150 Q112 132 124 76" fill="none" stroke="${FUR}" stroke-width="32" stroke-linecap="round"/>`;
    s+=`<ellipse cx="132" cy="44" rx="38" ry="34" fill="${LIGHT}" ${sw}/>`;
    s+=`<path d="M114 58 Q132 38 150 58 Q148 72 132 72 Q116 72 114 58 Z" fill="${PAD}"/>`;
    [[106,38],[121,22],[143,22],[158,38]].forEach(([a,b])=>s+=`<ellipse cx="${a}" cy="${b}" rx="7.5" ry="9.5" fill="${PAD}"/>`);
    s+=`<ellipse cx="-22" cy="190" rx="22" ry="12" fill="${LIGHT}" ${sw}/>`;
  }
  s+=`<g transform="translate(0 0)">${zazuHead(mode,look,mouth)}</g></g>`;
  return s;
}
function sara(x,y,opt={}){
  const {mouth='smile',ball=true,sc=1,brow=0}=opt;
  let s=`<g transform="translate(${x} ${y}) scale(${sc})">`;
  s+=`<path d="M-58 -10 Q-66 80 -46 140 L46 140 Q66 80 58 -10 Q40 -70 0 -70 Q-40 -70 -58 -10 Z" fill="${HAIR}"/>`; // Haare hinten
  s+=`<path d="M-62 210 Q-60 120 -26 104 L26 104 Q60 120 62 210 Z" fill="${SHIRT}" ${sw}/>`;
  s+=`<rect x="-12" y="78" width="24" height="30" fill="${SKIN}"/>`;
  s+=`<ellipse cx="0" cy="20" rx="48" ry="56" fill="${SKIN}" ${sw}/>`;
  s+=`<path d="M-50 4 Q-46 -50 0 -52 Q46 -50 50 4 Q30 -22 4 -26 Q-24 -24 -50 4 Z" fill="${HAIR}"/>`; // Pony
  s+=`<ellipse cx="-17" cy="20" rx="5" ry="7" fill="#1b1b1b"/><ellipse cx="17" cy="20" rx="5" ry="7" fill="#1b1b1b"/>`;
  s+=`<path d="M-26 ${4+brow} L-9 ${2-brow} M9 ${2-brow} L26 ${4+brow}" ${sw.replace('4','3')}/>`;
  s+=`<ellipse cx="-28" cy="38" rx="8" ry="5" fill="#F0A3A0" opacity=".6"/><ellipse cx="28" cy="38" rx="8" ry="5" fill="#F0A3A0" opacity=".6"/>`;
  if(mouth==='smile') s+=`<path d="M-14 44 Q0 58 14 44" fill="#c4554f" ${sw.replace('4','3')}/>`;
  else if(mouth==='o') s+=`<ellipse cx="0" cy="50" rx="7" ry="8" fill="#c4554f" ${sw.replace('4','3')}/>`;
  else s+=`<path d="M-10 50 Q0 46 10 50" fill="none" ${sw.replace('4','3')}/>`;
  if(ball){
    s+=`<circle cx="0" cy="168" r="38" fill="${BALL}" ${sw}/><circle cx="-12" cy="152" r="6" fill="#0f1d4a"/><circle cx="6" cy="148" r="6" fill="#0f1d4a"/><circle cx="-2" cy="168" r="7" fill="#0f1d4a"/>`;
    s+=`<ellipse cx="-36" cy="172" rx="14" ry="11" fill="${SKIN}" ${sw}/><ellipse cx="36" cy="172" rx="14" ry="11" fill="${SKIN}" ${sw}/>`;
  }
  return s+'</g>';
}
