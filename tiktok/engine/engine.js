/* ==========================================================================
   Moteur de motion design — construit une vidéo à partir des données d'un
   épisode (episodes.js). Toutes les animations sont des animations CSS dont
   les délais sont absolus : la vidéo est donc entièrement "seekable"
   (window.__seek(t)) pour un rendu image par image parfaitement déterministe.
   ========================================================================== */
(() => {
  const EASE = {
    out: 'cubic-bezier(.16,1,.3,1)',     // expo out — la signature "premium"
    inOut: 'cubic-bezier(.65,0,.35,1)',
    back: 'cubic-bezier(.34,1.56,.64,1)',
    soft: 'cubic-bezier(.33,1,.68,1)',
    lin: 'linear',
  };
  const TOTAL_EPISODES = 10;

  // ---------- helpers ----------
  const el = (tag, cls, html) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    return e;
  };
  const div = (cls, html) => el('div', cls, html);
  // Typographie française : espaces insécables avant ? ! : ; » et après «
  const nbsp = s => String(s).replace(/ ([?!:;»])/g, '\u00a0$1').replace(/« /g, '«\u00a0');
  const fmt = s => nbsp(s).replace(/\*(.+?)\*/g, '<em>$1</em>');

  // Ajoute une animation CSS avec un délai absolu (en secondes).
  function anim(node, name, dur, at, ease = 'out', fill = 'both', iter = '') {
    const s = `${name} ${dur}s ${EASE[ease] || ease} ${Math.max(0, at).toFixed(3)}s ${iter} ${fill}`;
    node.style.animation = node.style.animation ? `${node.style.animation}, ${s}` : s;
    return node;
  }

  // Ligne masquée qui se révèle par le bas.
  function maskLine(html, cls = '') {
    const m = div('mask ' + cls);
    const i = el('span', 'mi', html);
    m.append(i);
    return [m, i];
  }

  // Découpe une ligne en mots (en conservant les *emphases*).
  function words(line) {
    const out = [];
    let inEm = false;
    for (const raw of nbsp(line).split(' ')) {
      let w = raw;
      let em = inEm;
      if (w.startsWith('*')) { em = true; w = w.slice(1); inEm = true; }
      if (w.endsWith('*')) { w = w.slice(0, -1); inEm = false; }
      out.push(em ? `<em>${w}</em>` : w);
    }
    return out;
  }

  const ICON = {
    x: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12.5l5 5L20 6.5"/></svg>',
    plus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.4" stroke-linecap="round"><path d="M12 4v16M4 12h16"/></svg>',
    bookmark: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linejoin="round"><path d="M6 3.5h12v17l-6-4.5-6 4.5z"/></svg>',
    share: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M14 4l7 7-7 7M21 11H10a7 7 0 0 0-7 7"/></svg>',
    comment: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linejoin="round"><path d="M4 5h16v11H9l-5 4z"/></svg>',
    arrow: '<svg viewBox="0 0 60 30" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M2 15h54M42 3l14 12-14 12"/></svg>',
  };

  // ======================================================================
  //  SCÈNES — chaque type expose dur(data) et build(root, data, t0, ctx)
  // ======================================================================
  const SCENES = {};

  function kicker(root, text, t, ctx) {
    const k = div('kicker');
    const l = div('kl');
    k.append(l, el('span', '', fmt(text)));
    root.append(k);
    anim(l, 'scaleX', .7, t, 'out');
    anim(k.lastChild, 'fadeIn', .6, t + .1, 'soft');
  }

  // --- HOOK : grosse accroche typographique, mot par mot -----------------
  SCENES.hook = {
    dur: d => d.dur ?? 3.6 + (d.sub ? 1.4 : 0),
    build(root, d, t, ctx) {
      if (d.kicker) kicker(root, d.kicker, t, ctx);
      const box = div('hook-lines');
      box.dataset.fit = d.size ?? 168;
      root.append(box);
      let i = 0;
      d.lines.forEach(line => {
        const L = el('span', 'hook-line');
        words(line).forEach(w => {
          const m = el('span', 'w');
          const wi = el('span', 'wi', w);
          m.append(wi);
          L.append(m);
          anim(wi, 'revealUp', .9, t + .15 + i * .085, 'out');
          const em = wi.querySelector('em');
          if (em) anim(em, 'shimmer', 2.6, t + .5 + i * .085, 'lin', 'both', 'infinite');
          i++;
        });
        box.append(L);
      });
      ctx.cue(t + .1, 'hit');
      const u = div('uline');
      root.append(u);
      anim(u, 'scaleX', 1, t + .3 + i * .085, 'out');
      if (d.sub) {
        const s = div('hook-sub', fmt(d.sub));
        root.append(s);
        anim(s, 'fadeUp', .9, t + .7 + i * .085, 'out');
        ctx.cue(t + .7 + i * .085, 'tick');
      }
      anim(box, 'blurIn', 1.1, t, 'out');
    },
  };

  // --- CHAPTER : carte d'étape + parcours des 10 étapes ------------------
  SCENES.chapter = {
    dur: d => d.dur ?? 3.4,
    build(root, d, t, ctx) {
      const n = ctx.ep.n;
      const num = div('ch-num', String(n).padStart(2, '0'));
      root.append(num);
      anim(num, 'blurIn', 1.2, t, 'out');
      kicker(root, `Étape ${String(n).padStart(2, '0')} / ${TOTAL_EPISODES}`, t + .25, ctx);
      const [m, mi] = maskLine(fmt(d.title), 'ch-title');
      root.append(m);
      anim(mi, 'revealUp', 1, t + .35, 'out');
      if (d.desc) {
        const ds = div('ch-desc', fmt(d.desc));
        root.append(ds);
        anim(ds, 'fadeUp', .8, t + .6, 'out');
      }
      // Parcours
      const tr = div('track');
      const line = div('track-line');
      const fill = div('track-fill');
      const pos = k => (k - 1) / (TOTAL_EPISODES - 1);
      fill.style.setProperty('--from', Math.max(0, pos(n - 1)));
      fill.style.setProperty('--to', pos(n));
      tr.append(line, fill);
      anim(tr, 'fadeIn', .6, t + .5, 'soft');
      anim(fill, 'trackFill', 1.2, t + .8, 'inOut');
      for (let k = 1; k <= TOTAL_EPISODES; k++) {
        const nd = div('node' + (k < n ? ' done' : k === n ? ' now' : ''));
        nd.style.left = pos(k) * 100 + '%';
        if (k === n) {
          const r = div('ring');
          nd.append(r);
          anim(nd, 'pop', .7, t + 1.8, 'back');
          anim(r, 'pulseRing', 1.6, t + 2.1, 'soft', 'both', 'infinite');
        } else {
          anim(nd, 'pop', .5, t + .55 + k * .04, 'back');
        }
        tr.append(nd);
      }
      // Repères de début/fin, masqués quand ils chevaucheraient l'étiquette courante
      const ends = div('track-ends', `<span>${n > 3 ? 'Idée' : ''}</span><span>${n < 6 ? 'Lancement' : ''}</span>`);
      tr.append(ends);
      const lbl = div('track-lbl');
      const lbi = el('span', '', d.stage || d.title.replace(/\*/g, ''));
      lbl.append(lbi);
      lbl.style.left = pos(n) * 100 + '%';
      if (n === 1) lbl.style.transform = 'translateX(-13px)';
      if (n === TOTAL_EPISODES) lbl.style.transform = 'translateX(calc(-100% + 13px))';
      tr.append(lbl);
      lbi.style.display = 'inline-block';
      anim(lbi, 'fadeUp', .7, t + 2, 'out');
      root.append(tr);
      ctx.cue(t, 'whoosh');
      ctx.cue(t + 1.8, 'pop');
    },
  };

  // --- TEXT : phrase éditoriale, révélée ligne par ligne -----------------
  SCENES.text = {
    dur: d => d.dur ?? 2.4 + d.lines.length * .55 + (d.small ? 1.2 : 0),
    build(root, d, t, ctx) {
      const wrap = div('txt');
      const bar = div('bar');
      wrap.append(bar);
      anim(bar, 'scaleY', 1.2, t, 'out');
      if (d.quote) {
        const q = div('quote', '“');
        wrap.append(q);
        anim(q, 'fadeUp', .8, t, 'out');
      }
      const lines = div('txt-lines');
      if (d.size) lines.style.fontSize = d.size + 'px';
      d.lines.forEach((ln, i) => {
        const [m, mi] = maskLine(fmt(ln));
        lines.append(m);
        anim(mi, 'revealUp', 1, t + .15 + i * .16, 'out');
        const em = mi.querySelector('em');
        if (em) anim(em, 'shimmer', 2.6, t + .6 + i * .16, 'lin', 'both', 'infinite');
      });
      wrap.append(lines);
      if (d.small) {
        const s = div('txt-small sans', fmt(d.small));
        wrap.append(s);
        anim(s, 'fadeUp', .8, t + .7 + d.lines.length * .16, 'out');
      }
      root.append(wrap);
      ctx.cue(t, 'whoosh');
    },
  };

  // --- LIST : étapes numérotées --------------------------------------------
  SCENES.list = {
    step: d => d.step ?? (d.items.length > 4 ? .95 : 1.2),
    dur: d => d.dur ?? 1.4 + d.items.length * SCENES.list.step(d) + 2.6,
    build(root, d, t, ctx) {
      if (d.kicker) kicker(root, d.kicker, t, ctx);
      const box = div('list' + (d.compact || d.items.length > 4 ? ' compact' : ''));
      if (d.title) {
        const [m, mi] = maskLine(fmt(d.title), 'list-title');
        box.append(m);
        anim(mi, 'revealUp', 1, t + .15, 'out');
      }
      const step = SCENES.list.step(d);
      d.items.forEach((it, i) => {
        const [title, desc] = Array.isArray(it) ? it : [it];
        const at = t + .9 + i * step;
        const row = div('item');
        const dv = div('div');
        const n = div('n', String(i + 1).padStart(2, '0'));
        const tt = div('it', fmt(title));
        row.append(dv, n, tt);
        anim(dv, 'scaleX', .9, at, 'out');
        anim(n, 'fadeUp', .7, at + .05, 'out');
        anim(tt, 'slideR', .8, at + .12, 'out');
        if (desc) {
          const ds = div('id', fmt(desc));
          row.append(ds);
          anim(ds, 'fadeIn', .8, at + .35, 'soft');
        }
        box.append(row);
        ctx.cue(at, 'tick');
      });
      root.append(box);
      ctx.cue(t, 'whoosh');
    },
  };

  // --- STAT : compteur (avec anneau si pourcentage) ------------------------
  SCENES.stat = {
    dur: d => d.dur ?? 5.2,
    build(root, d, t, ctx) {
      const box = div('stat');
      if (d.kicker) kicker(box, d.kicker, t, ctx);
      const v = div('count');
      v.style.setProperty('--to', d.value);
      anim(v, 'countUp', 1.8, t + .3, 'out');
      if (d.ring) {
        const w = div('ring-wrap');
        w.innerHTML = `<svg viewBox="0 0 200 200"><defs><linearGradient id="gg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fde68a"/><stop offset="1" stop-color="#f0a500"/></linearGradient></defs><circle class="ring-bg" cx="100" cy="100" r="88" pathLength="100"/><circle class="ring-fg" cx="100" cy="100" r="88" pathLength="100"/></svg>`;
        const fg = w.querySelector('.ring-fg');
        fg.style.setProperty('--to', 100 - d.value);
        anim(fg, 'ring', 1.8, t + .3, 'out');
        const val = div('ring-val');
        val.append(v);
        if (d.suffix) val.append(el('small', '', d.suffix));
        w.append(val);
        box.append(w);
        anim(w, 'blurIn', 1, t, 'out');
      } else {
        const big = div('big-val');
        big.append(v);
        if (d.suffix) big.append(el('span', '', d.suffix));
        box.append(big);
        anim(big, 'blurIn', 1, t, 'out');
      }
      const lab = div('stat-label', fmt(d.label));
      box.append(lab);
      anim(lab, 'fadeUp', .9, t + 1.2, 'out');
      if (d.source) {
        const s = div('stat-src', d.source);
        box.append(s);
        anim(s, 'fadeIn', .8, t + 1.8, 'soft');
      }
      root.append(box);
      ctx.cue(t, 'whoosh');
      ctx.cue(t + 1.9, 'pop');
    },
  };

  // --- COMPARE : à éviter / à faire ------------------------------------------
  SCENES.compare = {
    dur: d => d.dur ?? 6.6,
    build(root, d, t, ctx) {
      if (d.kicker) kicker(root, d.kicker, t, ctx);
      const bad = div('card bad');
      bad.innerHTML = `<div class="lbl"><span class="ico">${ICON.x}</span>${d.badLabel || 'À éviter'}</div><div class="ct">${fmt(d.bad)}<div class="strike"></div></div>`;
      const good = div('card good');
      good.innerHTML = `<div class="lbl"><span class="ico">${ICON.check}</span>${d.goodLabel || 'À faire'}</div><div class="ct">${fmt(d.good)}</div>`;
      root.append(bad, good);
      anim(bad, 'fadeUp', .9, t + .2, 'out');
      anim(bad.querySelector('.strike'), 'scaleX', .6, t + 1.9, 'inOut');
      anim(bad, 'dim', .8, t + 2.3, 'out', 'forwards');
      anim(good, 'fadeUp', 1, t + 2.5, 'out');
      const em = good.querySelector('em');
      if (em) anim(em, 'shimmer', 2.6, t + 3, 'lin', 'both', 'infinite');
      ctx.cue(t, 'whoosh');
      ctx.cue(t + 1.9, 'swipe');
      ctx.cue(t + 2.5, 'pop');
    },
  };

  // --- FORMULA : phrase à trous ----------------------------------------------
  SCENES.formula = {
    dur: d => d.dur ?? 7,
    build(root, d, t, ctx) {
      if (d.kicker) kicker(root, d.kicker, t, ctx);
      const f = div('formula');
      const parts = d.text.split(/(\[[^\]]+\])/).filter(Boolean);
      let i = 0, s = 0;
      parts.forEach((p, pi) => {
        if (p.startsWith('[')) {
          const sl = el('span', 'slot', p.slice(1, -1));
          // la ponctuation qui suit reste collée à la case
          const nx = parts[pi + 1];
          const punct = nx && nx.match(/^[,.;:!?]+/);
          if (punct) {
            parts[pi + 1] = nx.slice(punct[0].length);
            const g = el('span', 'fw slot-g');
            g.append(sl, el('span', '', punct[0]));
            f.append(g);
            anim(g.lastChild, 'fadeIn', .4, t + 1.4 + s * .45, 'soft');
          } else f.append(sl);
          anim(sl, 'pop', .7, t + 1.4 + s * .45, 'back');
          ctx.cue(t + 1.4 + s * .45, 'pop');
          s++;
        } else {
          p.trim().split(/\s+/).filter(Boolean).forEach(w => {
            const sp = el('span', 'fw', w);
            f.append(sp);
            anim(sp, 'fadeUp', .6, t + .25 + i * .05, 'out');
            i++;
          });
        }
      });
      root.append(f);
      if (d.note) {
        const n = div('formula-note', fmt(d.note));
        root.append(n);
        anim(n, 'fadeUp', .8, t + 1.6 + s * .45, 'out');
      }
      ctx.cue(t, 'whoosh');
    },
  };

  // --- ZOOM : entonnoir de ciblage ---------------------------------------------
  SCENES.zoom = {
    dur: d => d.dur ?? 1.2 + d.levels.length * .9 + 2.6,
    build(root, d, t, ctx) {
      if (d.kicker) kicker(root, d.kicker, t, ctx);
      const box = div('zoom-bars');
      const N = d.levels.length;
      d.levels.forEach((lv, i) => {
        const last = i === N - 1;
        const b = div('zb' + (last ? ' final' : ''), fmt(lv));
        b.style.width = (100 - i * (40 / (N - 1))) + '%';
        const at = t + .4 + i * .9;
        anim(b, last ? 'pop' : 'fadeUp', last ? .8 : .7, at, last ? 'back' : 'out');
        if (!last) anim(b, 'dim', .6, at + .8, 'out', 'forwards');
        if (i) {
          const a = div('zoom-arrow');
          anim(a, 'scaleY', .4, at - .15, 'out');
          box.append(a);
        }
        box.append(b);
        ctx.cue(at, last ? 'pop' : 'tick');
      });
      root.append(box);
      ctx.cue(t, 'whoosh');
    },
  };

  // --- EQUATION : seuil de rentabilité ---------------------------------------
  SCENES.equation = {
    dur: d => d.dur ?? 8.2,
    build(root, d, t, ctx) {
      if (d.kicker) kicker(root, d.kicker, t, ctx);
      const [m, mi] = maskLine(fmt(d.title), 'eq-title');
      root.append(m);
      anim(mi, 'revealUp', 1, t + .1, 'out');
      const row = div('eq-row');
      d.formula.forEach((p, i) => {
        const isOp = p.length <= 1;
        const c = div(isOp ? 'op' : 'chip' + (i === 0 ? '' : ' gold'), p);
        row.append(c);
        anim(c, isOp ? 'pop' : 'fadeUp', .7, t + .7 + i * .25, isOp ? 'back' : 'out');
      });
      root.append(row);
      const ex = div('eq-ex');
      d.example.forEach((p, i) => {
        const c = el('span', p.length <= 1 ? 'op' : '', p);
        ex.append(c);
        anim(c, 'fadeUp', .7, t + 2.2 + i * .25, 'out');
      });
      root.append(ex);
      ctx.cue(t + 2.2, 'tick');
      const res = div('eq-res');
      const v = div('count');
      v.style.setProperty('--to', d.result.value);
      anim(v, 'countUp', 1.4, t + 3.6, 'out');
      res.append(v, div('rl', `${fmt(d.result.unit)}<span>${fmt(d.result.label)}</span>`));
      root.append(res);
      anim(res, 'pop', .9, t + 3.4, 'back');
      anim(res, 'glowPulse', 2.4, t + 4.4, 'soft', 'both', 'infinite');
      ctx.cue(t + 3.4, 'hit');
      ctx.cue(t, 'whoosh');
    },
  };

  // --- TIMELINE : rétroplanning vertical -------------------------------------
  SCENES.timeline = {
    dur: d => d.dur ?? 1.4 + d.steps.length * 1.05 + 2.6,
    build(root, d, t, ctx) {
      if (d.kicker) kicker(root, d.kicker, t, ctx);
      const tl = div('tl');
      const ln = div('tl-line');
      tl.append(ln);
      anim(ln, 'scaleY', d.steps.length * 1.05 + .4, t + .5, 'inOut');
      d.steps.forEach(([tag, txt], i) => {
        const at = t + .6 + i * 1.05;
        const s = div('tl-step' + (i === d.steps.length - 1 ? ' last' : ''));
        const dot = div('tl-dot');
        const tg = div('tl-tag', fmt(tag));
        const tx = div('tl-txt', fmt(txt));
        s.append(dot, tg, tx);
        anim(dot, 'pop', .6, at, 'back');
        anim(tg, 'slideR', .8, at + .05, 'out');
        anim(tx, 'fadeIn', .8, at + .25, 'soft');
        tl.append(s);
        ctx.cue(at, 'tick');
      });
      root.append(tl);
      ctx.cue(t, 'whoosh');
    },
  };

  // --- CHECKLIST ----------------------------------------------------------------
  SCENES.checklist = {
    dur: d => d.dur ?? 1.4 + d.items.length * .85 + 2.6,
    build(root, d, t, ctx) {
      if (d.kicker) kicker(root, d.kicker, t, ctx);
      if (d.title) {
        const [m, mi] = maskLine(fmt(d.title), 'list-title');
        root.append(m);
        anim(mi, 'revealUp', 1, t + .1, 'out');
      }
      d.items.forEach((it, i) => {
        const at = t + .9 + i * .85;
        const r = div('ck');
        const b = div('box', '<div class="fill"></div><svg viewBox="0 0 40 40"><path d="M8 21l8 8 16-17" pathLength="40"/></svg>');
        const tx = div('ck-t', fmt(it));
        r.append(b, tx);
        anim(r, 'fadeUp', .7, at - .45, 'out');
        anim(b.querySelector('.fill'), 'popFill', .45, at, 'back');
        anim(b.querySelector('path'), 'draw', .45, at + .2, 'out');
        root.append(r);
        ctx.cue(at, 'pop');
      });
      ctx.cue(t, 'whoosh');
    },
  };

  // --- CTA : épisode suivant / abonnement / commentaire -------------------------
  SCENES.cta = {
    dur: d => d.dur ?? 6,
    build(root, d, t, ctx) {
      if (d.big) {
        const [m, mi] = maskLine(fmt(d.big), 'cta-big');
        root.append(m);
        anim(mi, 'revealUp', 1, t + .1, 'out');
      }
      if (d.comment) {
        const c = div('comment-chip', `${ICON.comment}<span>${d.comment}</span>`);
        root.append(c);
        anim(c, 'pop', .8, t + .7, 'back');
        anim(c, 'glowPulse', 2.2, t + 1.5, 'soft', 'both', 'infinite');
        ctx.cue(t + .7, 'pop');
      }
      if (d.next) {
        const n = div('cta-next', `<div class="k"><span>À suivre · Épisode ${String(ctx.ep.n + 1).padStart(2, '0')}</span>${ICON.arrow}</div><div class="tt">${fmt(d.next)}</div>${d.nextSub ? `<div class="ts">${fmt(d.nextSub)}</div>` : ''}`);
        root.append(n);
        anim(n, 'fadeUp', 1, t + .1, 'out');
        anim(n.querySelector('.k svg'), 'nudge', 1.2, t + 1, 'inOut', 'both', 'infinite');
      }
      const acts = div('actions');
      (d.actions || [
        ['plus', 'Abonne-toi', 'pour ne rater aucune étape'],
        ['bookmark', 'Enregistre la vidéo', 'tu en auras besoin plus tard'],
      ]).forEach(([ic, a, s], i) => {
        const r = div('act', `<span class="ic${i ? ' ghost-ic' : ''}">${ICON[ic]}${i ? '' : '<span class="pulse"></span>'}</span><span>${a}<small>${s}</small></span>`);
        acts.append(r);
        const at = t + .9 + i * .3 + (d.comment ? .6 : 0);
        anim(r, 'slideR', .8, at, 'out');
        const p = r.querySelector('.pulse');
        if (p) anim(p, 'pulseRing', 1.6, at + .6, 'soft', 'both', 'infinite');
      });
      root.append(acts);
      ctx.cue(t, 'whoosh');
    },
  };

  // ======================================================================
  //  CONSTRUCTION DE L'ÉPISODE
  // ======================================================================
  function build(ep, mount) {
    const stage = div('stage');
    stage.style.setProperty('--accent', `var(--${ep.accent || 'coral'})`);
    const cues = [];
    const ctx = { ep, cue: (t, type) => cues.push({ t: +t.toFixed(3), type }) };

    // Arrière-plan
    const grid = div('layer bg-grid');
    const orbs = div('layer');
    const oa = div('orb orb-a'), ob = div('orb orb-b');
    orbs.append(oa, ob);
    const ghost = div('ghost', String(ep.n).padStart(2, '0'));
    const grain = div('layer grain');
    const vig = div('layer vignette');
    stage.append(grid, orbs, ghost);

    // Scènes
    let t = 0;
    const starts = [];
    ep.scenes.forEach((sc, i) => {
      const S = SCENES[sc.type];
      if (!S) throw new Error('Scène inconnue : ' + sc.type);
      const dur = S.dur(sc);
      const node = div('scene scene-' + sc.type);
      const inner = div('scene-inner');
      node.append(inner);
      S.build(inner, sc, t, ctx);
      anim(node, 'show', .001, t, 'lin', 'forwards');
      anim(inner, 'push', dur, t, 'lin', 'both');
      if (i < ep.scenes.length - 1) anim(node, 'sceneOut', .5, t + dur - .5, 'inOut', 'forwards');
      if (i > 0) {
        const sw = div('sweep');
        stage.append(sw);
        anim(sw, 'sweep', 1, t - .45, 'inOut', 'both');
      }
      stage.append(node);
      starts.push(t);
      t += dur;
    });
    const total = +(t + (ep.tail ?? 1.2)).toFixed(3);

    // Mouvement de fond sur toute la durée
    anim(grid, 'gridDrift', 12, 0, 'lin', 'both', 'infinite');
    anim(oa, 'orbA', 9, 0, 'inOut', 'both', 'infinite alternate');
    anim(ob, 'orbB', 11, 0, 'inOut', 'both', 'infinite alternate');
    anim(ghost, 'ghost', total, 0, 'lin', 'both');
    anim(ghost, 'fadeIn', 2, 0, 'soft', 'both');
    anim(grain, 'grain', .5, 0, 'steps(5)', 'both', 'infinite');

    // En-tête + barre de progression de l'épisode
    const hdr = div('hdr', `<div class="brand"><span class="mono">AN</span><span class="series">De l’idée <b>au lancement</b></span></div><div class="epno">Ép. ${String(ep.n).padStart(2, '0')}/${TOTAL_EPISODES}</div>`);
    const prog = div('progress', '<i></i>');
    anim(hdr, 'hdrIn', 1, .1, 'out');
    anim(prog, 'fadeIn', .8, .3, 'soft');
    anim(prog.firstChild, 'progress', total, 0, 'lin', 'both');
    stage.append(hdr, prog, grain, vig);

    mount.append(stage);
    return { stage, total, cues, starts };
  }

  // Ajuste la taille des titres d'accroche pour qu'ils tiennent dans la zone sûre.
  function fit(stage) {
    stage.querySelectorAll('[data-fit]').forEach(box => {
      let size = +box.dataset.fit;
      const max = box.parentElement.clientWidth;
      box.style.fontSize = size + 'px';
      const widest = () => Math.max(...[...box.children].map(l => l.scrollWidth));
      while (widest() > max && size > 60) { size -= 2; box.style.fontSize = size + 'px'; }
    });
  }

  window.MotionEngine = { build, fit, SCENES };
})();
