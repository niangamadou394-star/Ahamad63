/* ==========================================================================
   Bande-son synthétisée (aucun sample, aucun droit) : nappe d'ambiance,
   pulsation discrète et sound design calé sur les animations (whoosh, pop…).
   ========================================================================== */
import { writeFileSync } from 'node:fs';

const SR = 48000;

// Petit générateur pseudo-aléatoire déterministe
function rng(seed) {
  let s = seed >>> 0;
  return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296) * 2 - 1;
}

// Filtre biquad (RBJ) à coefficients variables
function biquad() {
  let x1 = 0, x2 = 0, y1 = 0, y2 = 0;
  return (x, type, f, q) => {
    const w = (2 * Math.PI * Math.min(f, SR * .45)) / SR;
    const a = Math.sin(w) / (2 * q), c = Math.cos(w);
    let b0, b1, b2;
    if (type === 'bp') { b0 = a; b1 = 0; b2 = -a; }
    else if (type === 'lp') { b0 = (1 - c) / 2; b1 = 1 - c; b2 = b0; }
    else { b0 = (1 + c) / 2; b1 = -(1 + c); b2 = b0; } // hp
    const a0 = 1 + a, a1 = -2 * c, a2 = 1 - a;
    const y = (b0 * x + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2) / a0;
    x2 = x1; x1 = x; y2 = y1; y1 = y;
    return y;
  };
}

export function writeSoundtrack(file, duration, cues) {
  const N = Math.ceil((duration + .2) * SR);
  const L = new Float32Array(N), R = new Float32Array(N);
  const add = (i, l, r = l) => { if (i >= 0 && i < N) { L[i] += l; R[i] += r; } };
  const noise = rng(7);

  // --- Nappe : alternance de deux accords (ré mineur 9 / si♭ maj 7) -----
  const chords = [[146.83, 220.0, 261.63, 349.23, 329.63], [116.54, 174.61, 220.0, 293.66, 349.23]];
  const lpL = biquad(), lpR = biquad();
  for (let i = 0; i < N; i++) {
    const t = i / SR;
    const ci = Math.floor(t / 8) % 2, ct = (t % 8) / 8;
    const xf = ct > .85 ? (ct - .85) / .15 : 0; // fondu entre accords
    let s = 0;
    for (const [k, ch] of [[0, chords[ci]], [1, chords[(ci + 1) % 2]]]) {
      const g = k ? xf : 1 - xf;
      if (g <= 0) continue;
      ch.forEach((f, j) => {
        s += g * (Math.sin(2 * Math.PI * f * t + j) + .5 * Math.sin(2 * Math.PI * f * 1.003 * t)) / (j + 2);
      });
    }
    const fade = Math.min(1, t / 2.5) * Math.min(1, (duration - t) / 1.5);
    const lfo = .75 + .25 * Math.sin(2 * Math.PI * .13 * t);
    const v = s * .05 * fade * lfo;
    L[i] += lpL(v, 'lp', 1400, .7);
    R[i] += lpR(v * .96, 'lp', 1500, .7);
  }

  // --- Pulsation : 96 BPM, très discrète --------------------------------
  const beat = 60 / 96;
  for (let b = 0; b * beat < duration - 1.5; b++) {
    const t0 = b * beat;
    if (t0 < 1) continue;
    const i0 = Math.floor(t0 * SR);
    if (b % 2 === 0) { // battement grave
      for (let k = 0; k < SR * .35; k++) {
        const t = k / SR, f = 48 + 60 * Math.exp(-t * 30);
        add(i0 + k, Math.sin(2 * Math.PI * f * t) * Math.exp(-t * 9) * .22);
      }
    }
    const hp = biquad(); // charleston feutré sur chaque temps
    const io = Math.floor((t0 + beat / 2) * SR);
    for (let k = 0; k < SR * .05; k++) {
      const v = hp(noise(), 'hp', 7000, .7) * Math.exp(-k / SR * 90) * .035;
      add(io + k, v * .8, v);
    }
  }

  // --- Sound design calé sur les animations ------------------------------
  const FX = {
    whoosh(i0, len = .7, f0 = 300, f1 = 3800, g = .32) {
      const bp = biquad(), n = Math.floor(len * SR);
      for (let k = 0; k < n; k++) {
        const p = k / n, env = Math.sin(Math.PI * Math.pow(p, .7)) ** 2;
        const v = bp(noise(), 'bp', f0 * Math.pow(f1 / f0, p), 1.4) * env * g;
        add(i0 + k, v * (1 - p * .6), v * (.4 + p * .6));
      }
    },
    swipe(i0) { FX.whoosh(i0, .4, 1200, 6000, .22); },
    hit(i0) {
      for (let k = 0; k < SR * 1.2; k++) {
        const t = k / SR, f = 38 + 70 * Math.exp(-t * 18);
        add(i0 + k, Math.sin(2 * Math.PI * f * t) * Math.exp(-t * 3.5) * .5);
      }
      FX.whoosh(i0 - Math.floor(SR * .35), .45, 200, 2500, .25);
    },
    tick(i0) {
      for (let k = 0; k < SR * .06; k++) {
        const t = k / SR;
        add(i0 + k, Math.sin(2 * Math.PI * 1800 * t) * Math.exp(-t * 80) * .09);
      }
    },
    pop(i0) {
      for (let k = 0; k < SR * .14; k++) {
        const t = k / SR, f = 520 + 520 * Math.min(1, t * 25);
        const v = Math.sin(2 * Math.PI * f * t) * Math.exp(-t * 30) * .16;
        add(i0 + k, v, v * .9);
      }
    },
  };
  for (const c of cues) {
    const at = c.type === 'whoosh' ? c.t - .45 : c.t;
    (FX[c.type] || FX.tick)(Math.floor(at * SR));
  }

  // --- Limiteur doux + écriture WAV 16 bits stéréo -----------------------
  let peak = 0;
  for (let i = 0; i < N; i++) peak = Math.max(peak, Math.abs(L[i]), Math.abs(R[i]));
  const gain = peak > 0 ? .85 / Math.tanh(peak) : 1;
  const buf = Buffer.alloc(44 + N * 4);
  buf.write('RIFF', 0); buf.writeUInt32LE(36 + N * 4, 4); buf.write('WAVE', 8);
  buf.write('fmt ', 12); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22);
  buf.writeUInt32LE(SR, 24); buf.writeUInt32LE(SR * 4, 28); buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34);
  buf.write('data', 36); buf.writeUInt32LE(N * 4, 40);
  for (let i = 0; i < N; i++) {
    buf.writeInt16LE(Math.round(Math.tanh(L[i]) * gain * 32767), 44 + i * 4);
    buf.writeInt16LE(Math.round(Math.tanh(R[i]) * gain * 32767), 46 + i * 4);
  }
  writeFileSync(file, buf);
}
