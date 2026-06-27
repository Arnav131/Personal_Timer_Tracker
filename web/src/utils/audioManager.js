/**
 * audioManager — Web Audio API wrapper for alarm sounds.
 * Uses an OscillatorNode to generate a gentle chime tone
 * (no external audio file needed).
 */

let audioCtx = null;
let oscillator = null;
let gainNode = null;
let loopInterval = null;

function getContext() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  return audioCtx;
}

/**
 * Play a gentle chime once.
 */
export function playOnce() {
  try {
    const ctx = getContext();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(800, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(400, ctx.currentTime + 0.5);

    gain.gain.setValueAtTime(0.3, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.8);

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start(ctx.currentTime);
    osc.stop(ctx.currentTime + 0.8);
  } catch {
    // Audio not available
  }
}

/**
 * Play a repeating alarm tone (for enforcer).
 */
export function playLoop() {
  stopLoop();
  // Play immediately, then every 3 seconds
  playAlarmTone();
  loopInterval = setInterval(playAlarmTone, 3000);
}

function playAlarmTone() {
  try {
    const ctx = getContext();

    // Two-tone alarm: high-low
    for (let i = 0; i < 3; i++) {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';

      const startTime = ctx.currentTime + i * 0.3;
      osc.frequency.setValueAtTime(i % 2 === 0 ? 700 : 500, startTime);

      gain.gain.setValueAtTime(0.2, startTime);
      gain.gain.exponentialRampToValueAtTime(0.01, startTime + 0.25);

      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(startTime);
      osc.stop(startTime + 0.25);
    }
  } catch {
    // Audio not available
  }
}

/**
 * Stop the looping alarm.
 */
export function stopLoop() {
  if (loopInterval) {
    clearInterval(loopInterval);
    loopInterval = null;
  }
}
