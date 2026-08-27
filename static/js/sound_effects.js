/**
 * CS Random Quiz — Bulletproof Sound Effects Engine
 * รองรับ Apple Safari (macOS / iOS / iPadOS) และทุกเบราว์เซอร์ 100%
 * มีระบบ Safari WebKit Audio Unlocker และ In-Memory WAV Synthesizer Fallback
 */

class SoundEffects {
  constructor() {
    this.audioCtx = null;
    this.isMuted = localStorage.getItem('cs_quiz_muted') === 'true';
    this.unlocked = false;

    // ผูก Event ปลดล็อกทันทีที่ผู้ใช้แตะหรือคลิกส่วนใดของหน้าจอ
    this.bindUnlockEvents();
  }

  bindUnlockEvents() {
    const unlock = () => {
      this.unlockSafariAudio();
    };

    ['click', 'touchstart', 'touchend', 'pointerdown', 'mousedown', 'keydown'].forEach(evt => {
      document.addEventListener(evt, unlock, { once: false, capture: true, passive: true });
    });
  }

  // ปลดล็อก WebKit AudioContext สำหรับ Safari / iOS ตามมาตรฐาน Apple
  unlockSafariAudio() {
    try {
      if (!this.audioCtx) {
        const AudioCtxClass = window.AudioContext || window.webkitAudioContext;
        if (AudioCtxClass) {
          this.audioCtx = new AudioCtxClass();
        }
      }

      if (this.audioCtx) {
        if (this.audioCtx.state === 'suspended') {
          this.audioCtx.resume();
        }

        // เล่น Silent Buffer 1 frame เพื่อปลดล็อก Audio Engine ของ Safari อย่างสมบูรณ์
        if (!this.unlocked && this.audioCtx.state === 'running') {
          const buffer = this.audioCtx.createBuffer(1, 1, 22050);
          const source = this.audioCtx.createBufferSource();
          source.buffer = buffer;
          source.connect(this.audioCtx.destination);
          source.start(0);
          this.unlocked = true;
        }
      }
    } catch (e) {
      console.log('[Safari Audio Unlock Note]', e);
    }
  }

  getAudioContext() {
    this.unlockSafariAudio();
    return this.audioCtx;
  }

  toggleMute() {
    this.isMuted = !this.isMuted;
    localStorage.setItem('cs_quiz_muted', this.isMuted);
    return this.isMuted;
  }

  // -------------------------------------------------------------
  // In-Memory WAV Data-URI Fallback Generator (ทำงานบน Safari ได้เสมอ)
  // -------------------------------------------------------------
  createWavUrl(frequencies, durations, type = 'sine', volume = 0.3) {
    const sampleRate = 22050;
    let totalSamples = 0;
    durations.forEach(d => totalSamples += Math.floor(sampleRate * d));

    const buffer = new ArrayBuffer(44 + totalSamples * 2);
    const view = new DataView(buffer);

    // RIFF identifier
    const writeString = (offset, string) => {
      for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
      }
    };

    writeString(0, 'RIFF');
    view.setUint32(4, 36 + totalSamples * 2, true);
    writeString(8, 'WAVE');
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true); // PCM
    view.setUint16(22, 1, true); // Mono
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true); // 16-bit
    writeString(36, 'data');
    view.setUint32(40, totalSamples * 2, true);

    let offset = 44;
    frequencies.forEach((freq, idx) => {
      const dur = durations[idx];
      const samples = Math.floor(sampleRate * dur);
      for (let i = 0; i < samples; i++) {
        const t = i / sampleRate;
        let sample = 0;
        if (type === 'sine') {
          sample = Math.sin(2 * Math.PI * freq * t);
        } else if (type === 'triangle') {
          sample = 2 * Math.abs(2 * (t * freq - Math.floor(t * freq + 0.5))) - 1;
        } else if (type === 'square') {
          sample = Math.sin(2 * Math.PI * freq * t) >= 0 ? 1 : -1;
        }
        // Envelope
        const env = Math.max(0, 1 - (i / samples));
        const finalVal = Math.max(-1, Math.min(1, sample * env * volume));
        view.setInt16(offset, finalVal < 0 ? finalVal * 0x8000 : finalVal * 0x7FFF, true);
        offset += 2;
      }
    });

    const blob = new Blob([view], { type: 'audio/wav' });
    return URL.createObjectURL(blob);
  }

  playFallback(wavUrl) {
    if (this.isMuted) return;
    try {
      const audio = new Audio(wavUrl);
      audio.volume = 0.6;
      audio.play().catch(() => {});
    } catch (e) {}
  }

  // 1. เสียงคลิกปุ่มสุ่ม (Punchy Button Click)
  playButtonClick() {
    if (this.isMuted) return;
    const ctx = this.getAudioContext();

    if (ctx && ctx.state === 'running') {
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
        return;
      } catch (e) {}
    }

    // Safari Fallback
    if (!this._btnWav) {
      this._btnWav = this.createWavUrl([440, 220], [0.04, 0.04], 'sine', 0.4);
    }
    this.playFallback(this._btnWav);
  }

  // 2. เสียงตัวเลขสล็อตวิ่ง (Fast Slot Wheel Tick)
  playSlotTick(freq = 600) {
    if (this.isMuted) return;
    const ctx = this.getAudioContext();

    if (ctx && ctx.state === 'running') {
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
        return;
      } catch (e) {}
    }

    // Safari Fallback
    if (!this._tickWav) {
      this._tickWav = this.createWavUrl([600], [0.04], 'triangle', 0.3);
    }
    this.playFallback(this._tickWav);
  }

  // 3. เสียงล็อกผลตัวเลขที่สุ่มได้ (Slot Winner Lock Chime)
  playSlotLock() {
    if (this.isMuted) return;
    const ctx = this.getAudioContext();

    if (ctx && ctx.state === 'running') {
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
        return;
      } catch (e) {}
    }

    // Safari Fallback
    if (!this._lockWav) {
      this._lockWav = this.createWavUrl([523, 659, 784, 1046], [0.08, 0.08, 0.08, 0.25], 'sine', 0.4);
    }
    this.playFallback(this._lockWav);
  }

  // 4. เสียงนับถอยหลัง (Timer Tick)
  playCountdownTick() {
    if (this.isMuted) return;
    const ctx = this.getAudioContext();

    if (ctx && ctx.state === 'running') {
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
        return;
      } catch (e) {}
    }

    if (!this._countWav) {
      this._countWav = this.createWavUrl([800], [0.05], 'sine', 0.2);
    }
    this.playFallback(this._countWav);
  }

  // 5. เสียงเตือนเวลาใกล้หมด (Warning Beep)
  playWarningBeep() {
    if (this.isMuted) return;
    const ctx = this.getAudioContext();

    if (ctx && ctx.state === 'running') {
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
        return;
      } catch (e) {}
    }

    if (!this._warnWav) {
      this._warnWav = this.createWavUrl([950], [0.12], 'square', 0.25);
    }
    this.playFallback(this._warnWav);
  }

  // 6. เสียงเฉลยถูกต้อง / ชัยชนะ (Victory Fanfare)
  playVictoryFanfare() {
    if (this.isMuted) return;
    const ctx = this.getAudioContext();

    if (ctx && ctx.state === 'running') {
      try {
        const chords = [
          { freq: 523.25, time: 0 },
          { freq: 659.25, time: 0.1 },
          { freq: 783.99, time: 0.2 },
          { freq: 1046.50, time: 0.3 },
          { freq: 1318.51, time: 0.45 }
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
        return;
      } catch (e) {}
    }

    if (!this._fanfareWav) {
      this._fanfareWav = this.createWavUrl([523, 659, 784, 1046, 1318], [0.1, 0.1, 0.1, 0.15, 0.4], 'triangle', 0.5);
    }
    this.playFallback(this._fanfareWav);
  }
}

// Global Sound Instance
window.quizSounds = new SoundEffects();
