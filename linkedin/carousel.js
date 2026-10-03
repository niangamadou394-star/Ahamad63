/* ==========================================================================
   Construit un carrousel LinkedIn à partir des données d'un épisode
   (../tiktok/episodes.js : une seule source de contenu pour les 2 formats).
   ========================================================================== */
(() => {
  // Une couleur signature par épisode.
  // c = couleur principale, c2 = secondaire, on = texte sur c, cc = accent lisible sur fond crème,
  // em = mise en valeur sur fond coloré, soft = teinte claire.
  const THEMES = {
    1: { c: '#FF5A3C', c2: '#FFB800', on: '#fff', on2: '#17131F', soft: '#FFE7E0', em: '#FFE27A' },
    2: { c: '#2D5BFF', c2: '#00C9A7', on: '#fff', on2: '#fff', soft: '#E3E9FF', em: '#9FF3E4' },
    3: { c: '#7A3CFF', c2: '#FF4FA3', on: '#fff', on2: '#fff', soft: '#EEE5FF', em: '#FFC2E0' },
    4: { c: '#FF7A00', c2: '#2D5BFF', on: '#fff', on2: '#fff', soft: '#FFEBD6', em: '#FFF0A8' },
    5: { c: '#00A37A', c2: '#FFC21A', on: '#fff', on2: '#17131F', soft: '#DDF5EC', em: '#FFE27A' },
    6: { c: '#FF2E7E', c2: '#7A3CFF', on: '#fff', on2: '#fff', soft: '#FFE0EC', em: '#FFE27A' },
    7: { c: '#0B7A8C', c2: '#FF7A59', on: '#fff', on2: '#fff', soft: '#DDF1F3', em: '#FFD6A5' },
    8: { c: '#3B2CC9', c2: '#FF5A3C', on: '#fff', on2: '#fff', soft: '#E6E3FF', em: '#FFB8A8' },
    9: { c: '#FFC21A', c2: '#FF5A3C', on: '#17131F', on2: '#fff', soft: '#FFF1C7', em: '#B42318', cc: '#C25E00', dark: true },
    10: { c: '#FF3D6E', c2: '#7A3CFF', on: '#fff', on2: '#fff', soft: '#FFE0E9', em: '#FFE27A', grad: true },
  };

  // Ajustements de texte propres à LinkedIn (le reste vient de la série TikTok).
  const OVERRIDES = {
    7: { hookSub: 'On démêle tout ça, slide par slide.' },
  };

  const ICON = {
    arrow: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h15M13 5l7 7-7 7"/></svg>',
    x: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.4" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12.5l5 5L20 6.5"/></svg>',
    repost: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M17 2l4 4-4 4"/><path d="M3 11V9a3 3 0 0 1 3-3h15M7 22l-4-4 4-4"/><path d="M21 13v2a3 3 0 0 1-3 3H3"/></svg>',
    bell: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9M10.3 21a1.9 1.9 0 0 0 3.4 0"/></svg>',
    comment: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linejoin="round"><path d="M4 5h16v11H9l-5 4z"/></svg>',
    bookmark: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linejoin="round"><path d="M6 3.5h12v17l-6-4.5-6 4.5z"/></svg>',
  };

  const nbsp = s => String(s).replace(/ ([?!:;»])/g, ' $1').replace(/« /g, '« ');
  const fmt = s => nbsp(s).replace(/\*(.+?)\*/g, '<em>$1</em>');
  const pad = n => String(n).padStart(2, '0');

  // ---- rendu de chaque type de scène en slide statique -------------------
  const R = {
    text: d => ({
      vivid: true,
      html: `<div class="body">${d.quote ? '<div class="quote-mark">“</div>' : ''}<div class="statement">${fmt(d.lines.join(' '))}</div>${d.small ? `<div class="statement-s">${fmt(d.small)}</div>` : ''}</div>`,
    }),
    list: d => ({
      html: `<div class="body">${d.kicker ? `<div class="kick">${fmt(d.kicker)}</div>` : ''}${d.title ? `<h2>${fmt(d.title)}</h2>` : ''}<div class="items${d.items.length > 3 ? ' many' : ''}">${d.items.map((it, i) => {
        const [t, ds] = Array.isArray(it) ? it : [it];
        return `<div class="it"><div class="n">${i + 1}</div><div><div class="t">${fmt(t)}</div>${ds ? `<div class="d">${fmt(ds)}</div>` : ''}</div></div>`;
      }).join('')}</div></div>`,
    }),
    stat: d => ({
      vivid: true,
      html: `<div class="body">${d.kicker ? `<div class="kick">${fmt(d.kicker)}</div>` : ''}<div class="bignum">${d.value}${d.suffix ? `<small>${d.suffix}</small>` : ''}</div><div class="stat-l">${fmt(d.label)}</div>${d.source ? `<div class="stat-s">${d.source}</div>` : ''}</div>`,
    }),
    compare: d => ({
      html: `<div class="body">${d.kicker ? `<div class="kick">${fmt(d.kicker)}</div>` : ''}<div class="cmp"><div class="card bad"><div class="lb"><span>${ICON.x}</span>${d.badLabel || 'À éviter'}</div><div class="tx">${fmt(d.bad)}</div></div><div class="card good"><div class="lb"><span>${ICON.check}</span>${d.goodLabel || 'À faire'}</div><div class="tx">${fmt(d.good)}</div></div></div></div>`,
    }),
    formula: d => ({
      html: `<div class="body">${d.kicker ? `<div class="kick">${fmt(d.kicker)}</div>` : ''}<div class="fml">${nbsp(d.text).replace(/\[([^\]]+)\]([,.]?)/g, '<span class="nw"><span class="slot">$1</span>$2</span>')}</div>${d.note ? `<div class="fml-n">${fmt(d.note)}</div>` : ''}</div>`,
    }),
    zoom: d => ({
      html: `<div class="body">${d.kicker ? `<div class="kick">${fmt(d.kicker)}</div>` : ''}<div class="fun">${d.levels.map((l, i, a) => `<div class="${i === a.length - 1 ? 'last' : ''}" style="width:${100 - i * (36 / (a.length - 1))}%">${fmt(l)}</div>`).join('')}</div></div>`,
    }),
    equation: d => ({
      html: `<div class="body">${d.kicker ? `<div class="kick">${fmt(d.kicker)}</div>` : ''}<h2>${fmt(d.title)}</h2><div class="eq">${d.formula.map((p, i) => p.length <= 1 ? `<span class="op">${p}</span>` : `<span class="chip${i ? ' c' : ''}">${p}</span>`).join('')}</div><div class="ex">${d.example.map(p => p.length <= 1 ? `<span class="op">${p}</span>` : `<span>${p}</span>`).join('')}</div><div class="res"><b>${d.result.value}</b><span>${fmt(d.result.unit)}<small>${fmt(d.result.label)}</small></span></div></div>`,
    }),
    timeline: d => ({
      html: `<div class="body">${d.kicker ? `<div class="kick">${fmt(d.kicker)}</div>` : ''}<h2>Ton lancement <em>en 30 jours.</em></h2><div class="tl">${d.steps.map(([a, b]) => `<div class="st"><b>${a}</b><span>${fmt(b)}</span></div>`).join('')}</div></div>`,
    }),
    checklist: d => ({
      html: `<div class="body">${d.kicker ? `<div class="kick">${fmt(d.kicker)}</div>` : ''}${d.title ? `<h2>${fmt(d.title)}</h2>` : ''}<div class="cks">${d.items.map(t => `<div class="ck"><span>${ICON.check}</span>${fmt(t)}</div>`).join('')}</div></div>`,
    }),
  };

  function cover(ep, hook, chapter, o) {
    const sub = o.hookSub || hook.sub || chapter?.desc || '';
    return {
      vivid: true, cls: 'cover',
      html: `<div class="stepbig">${pad(ep.n)}</div><div class="body"><div class="ep">Étape ${pad(ep.n)}/10 · ${ep.title}</div><h1>${fmt(hook.lines.join(' '))}</h1>${sub ? `<div class="sub">${fmt(sub)}</div>` : ''}<div class="path">${Array.from({ length: 10 }, (_, i) => `<i class="${i < ep.n ? 'on' : ''}"></i>`).join('')}</div><div class="path-l"><span>Idée</span><span>Lancement</span></div></div>`,
    };
  }

  function cta(ep, d) {
    const last = ep.n === 10;
    const acts = last
      ? [['comment', 'Commente « LANCEMENT »', 'et on en parle ensemble'], ['repost', 'Republie', 'pour un porteur de projet de ton réseau'], ['bell', 'Suis-moi', 'pour d’autres contenus comme celui-ci']]
      : [['bookmark', 'Enregistre ce post', 'tu en auras besoin plus tard'], ['repost', 'Republie', 'pour aider un porteur de projet'], ['bell', 'Suis-moi', 'pour ne pas rater l’étape suivante']];
    return {
      vivid: true, cls: 'cta',
      html: `<div class="body"><h1>${last ? fmt(d.big || 'Tu veux être *accompagné·e ?*') : 'Ce carrousel t’a <em>aidé·e ?</em>'}</h1>${!last && d.next ? `<div class="next"><div class="k">À suivre · Étape ${pad(ep.n + 1)}</div><div class="t">${fmt(d.next)}</div></div>` : ''}<div class="acts">${acts.map(([ic, a, s]) => `<div class="act"><span>${ICON[ic]}</span><div>${nbsp(a)}<small>${s}</small></div></div>`).join('')}</div></div>`,
    };
  }

  function build(ep, mount) {
    const th = THEMES[ep.n];
    const o = OVERRIDES[ep.n] || {};
    const hook = ep.scenes.find(s => s.type === 'hook');
    const chapter = ep.scenes.find(s => s.type === 'chapter');
    const ctaData = ep.scenes.find(s => s.type === 'cta') || {};
    const slides = [cover(ep, hook, chapter, o)];
    ep.scenes.forEach(s => { if (R[s.type]) slides.push(R[s.type](s)); });
    slides.push(cta(ep, ctaData));

    slides.forEach((s, i) => {
      const el = document.createElement('section');
      el.className = `slide ${s.vivid ? 'vivid' : ''} ${th.grad && s.vivid ? 'grad' : ''} ${th.dark ? 'dark' : ''} ${s.cls || ''}`;
      const vars = { '--c': th.c, '--c2': th.c2, '--on': th.on, '--on2': th.on2, '--soft': th.soft, '--hl': 'transparent' };
      Object.entries(vars).forEach(([k, v]) => el.style.setProperty(k, v));
      // accent lisible : sur fond crème on prend cc (ou c), sur fond coloré la couleur em
      el.style.setProperty('--cc', th.cc || th.c);
      const isLast = i === slides.length - 1;
      el.innerHTML = `<div class="blob b1"></div><div class="blob b2"></div><div class="dots"></div>
        <div class="top"><span class="tag"><i></i>De l’idée au lancement</span><span class="count">${pad(i + 1)} / ${pad(slides.length)}</span></div>
        ${s.html}
        <div class="foot"><div class="bar"><b style="width:${((i + 1) / slides.length) * 100}%"></b></div>${isLast ? '' : `<div class="swipe">${i === 0 ? 'Glisse' : ''}<span>${ICON.arrow}</span></div>`}</div>`;
      if (s.vivid) el.querySelectorAll('em').forEach(e => { e.style.color = th.em; });
      el.querySelectorAll('.card.good em, .fun .last em').forEach(e => { e.style.color = th.em; });
      if (!s.vivid) el.querySelectorAll('.body > .kick, h2 em, .fml-n em, .it em, .op, .st b, .chip.c').forEach(e => { e.style.color = th.cc || th.c; });
      mount.append(el);
    });
    return slides.length;
  }

  window.Carousel = { build, THEMES };
})();
