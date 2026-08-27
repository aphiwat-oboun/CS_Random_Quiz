/**
 * CS Random Quiz — Web Audio API Sound Effects Synthesizer
 * รองรับ macOS (Safari / Chrome), iOS, Windows, Android 100%
 * พร้อมระบบ Auto-Unlock WebKit AudioContext สำหรับระบบความปลอดภัยของ Apple
 */

class SoundEffects {
  constructor() {
    this.audioCtx = null;
    this.isMuted = localStorage.getItem('cs_quiz_muted') === 'true';
    this.isUnlocked = false;
    this.initUnlockListeners();
  }

  // ปลดล็อกระบบเสียงสำหรับ macOS Safari / iOS ทันทีที่มีการแตะหรือคลิกหน้าจอ
  initUnlockListeners() {
    const unlockEvents = ['click', 'touchstart', 'touchend', 'pointerdown', 'mousedown', 'keydown'];
    const unlockHandler = () => {
      this.unlockAudio();
      unlockEvents.forEach(evt => document.removeEventListener(evt, unlockHandler, true));
    };

    unlockEvents.forEach(evt => {
      document.addEventListener(evt, unlockHandler, { capture: true, passive: true });
    });
  }

  unlockAudio() {
    const ctx = this.getAudioContext();
    if (ctx && ctx.state === 'suspended') {
      ctx.resume().then(() => {
        this.isUnlocked = true;
      }).catch(() => {});
    }
  }

  getAudioContext() {
    if (!this.audioCtx) {
      const AudioCtxClass = window.AudioContext || window.webkitAudioContext;
      if (AudioCtxClass) {
        this.audioCtx = new AudioCtxClass();
      }
    }
    if (this.audioCtx && this.audioCtx.state === 'suspended') {
      this.audioCtx.resume().catch(() => {});
    }
    return this.audioCtx;
  }

  toggleMute() {
    this.isMuted = !this.isMuted;
    localStorage.setItem('cs_quiz_muted', this.isMuted);
    return this.isMuted;
  }

  // 1. เสียงคลิกปุ่มสุ่ม (Punchy Button Click)
  playButtonClick() {
    if (this.isMuted) return;
    const ctx = this.getAudioContext();
    if (!ctx) return;

    ctx.resume().then(() => {
      try {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        
        osc.type = 'sine';
        osc.frequency.setValueAtTime(440, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(150, ctx.currentTime + 0.08);

        gain.gain.setValueAtTime(0.3, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.08);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + 0.08);
      } catch (e) {}
    }).catch(() => {});
  }

  // 2. เสียงตัวเลขสล็อตวิ่ง (Fast Slot Wheel Tick)
  playSlotTick(freq = 600) {
    if (this.isMuted) return;
    const ctx = this.getAudioContext();
    if (!ctx) return;

    ctx.resume().then(() => {
      try {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = 'triangle';
        osc.frequency.setValueAtTime(freq, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(300, ctx.currentTime + 0.04);

        gain.gain.setValueAtTime(0.2, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.04);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + 0.04);
      } catch (e) {}
    }).catch(() => {});
  }

  // 3. เสียงล็อกผลตัวเลขที่สุ่มได้ (Slot Winner Lock Chime)
  playSlotLock() {
    if (this.isMuted) return;
    const ctx = this.getAudioContext();
    if (!ctx) return;

    ctx.resume().then(() => {
      try {
        const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
        notes.forEach((freq, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();

          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, ctx.currentTime + idx * 0.08);

          gain.gain.setValueAtTime(0.25, ctx.currentTime + idx * 0.08);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + idx * 0.08 + 0.35);

          osc.connect(gain);
          gain.connect(ctx.destination);

          osc.start(ctx.currentTime + idx * 0.08);
          osc.stop(ctx.currentTime + idx * 0.08 + 0.35);
        });
      } catch (e) {}
    }).catch(() => {});
  }

  // 4. เสียงนับถอยหลัง (Timer Tick)
  playCountdownTick() {
    if (this.isMuted) return;
    const ctx = this.getAudioContext();
    if (!ctx) return;

    ctx.resume().then(() => {
      try {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = 'sine';
        osc.frequency.setValueAtTime(800, ctx.currentTime);

        gain.gain.setValueAtTime(0.09, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.05);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + 0.05);
      } catch (e) {}
    }).catch(() => {});
  }

  // 5. เสียงเตือนเวลาใกล้หมด (Warning Beep)
  playWarningBeep() {
    if (this.isMuted) return;
    const ctx = this.getAudioContext();
    if (!ctx) return;

    ctx.resume().then(() => {
      try {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = 'square';
        osc.frequency.setValueAtTime(950, ctx.currentTime);

        gain.gain.setValueAtTime(0.12, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.12);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + 0.12);
      } catch (e) {}
    }).catch(() => {});
  }

  // 6. เสียงเฉลยถูกต้อง / ชัยชนะ (Victory Fanfare)
  playVictoryFanfare() {
    if (this.isMuted) return;
    const ctx = this.getAudioContext();
    if (!ctx) return;

    ctx.resume().then(() => {
      try {
        const chords = [
          { freq: 523.25, time: 0 },    // C5
          { freq: 659.25, time: 0.1 },  // E5
          { freq: 783.99, time: 0.2 },  // G5
          { freq: 1046.50, time: 0.3 }, // C6
          { freq: 1318.51, time: 0.45 } // E6
        ];

        chords.forEach((note) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();

          osc.type = 'triangle';
          osc.frequency.setValueAtTime(note.freq, ctx.currentTime + note.time);

          gain.gain.setValueAtTime(0.3, ctx.currentTime + note.time);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + note.time + 0.6);

          osc.connect(gain);
          gain.connect(ctx.destination);

          osc.start(ctx.currentTime + note.time);
          osc.stop(ctx.currentTime + note.time + 0.6);
        });
      } catch (e) {}
    }).catch(() => {});
  }
}

// Global Sound Instance
window.quizSounds = new SoundEffects();
