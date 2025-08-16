import numpy as np
import sounddevice as sd
from notes import get_frequency

SAMPLE_RATE = 44100

class WaveGenerator:
    """Generate different types of waveforms"""
    
    def __init__(self, note: str, octave: int, amplitude: float = 0.3):
        self.note = note
        self.octave = octave
        self.frequency = get_frequency(note, octave)
        self.amplitude = amplitude
    
    def _generate_time_array(self, duration: float) -> np.ndarray:
        """Create time array for given duration"""
        return np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    
    def sine_wave(self, duration: float) -> np.ndarray:
        """Generate smooth sine wave"""
        t = self._generate_time_array(duration)
        return self.amplitude * np.sin(2 * np.pi * self.frequency * t)
    
    def square_wave(self, duration: float) -> np.ndarray:
        """Generate retro square wave"""
        t = self._generate_time_array(duration)
        sine = np.sin(2 * np.pi * self.frequency * t)
        return self.amplitude * np.sign(sine)
    
    def sawtooth_wave(self, duration: float) -> np.ndarray:
        """Generate buzzy sawtooth wave"""
        t = self._generate_time_array(duration)
        return self.amplitude * (2 * (t * self.frequency - np.floor(t * self.frequency + 0.5)))
    
    def triangle_wave(self, duration: float) -> np.ndarray:
        """Generate soft triangle wave"""
        t = self._generate_time_array(duration)
        return self.amplitude * (2 * np.abs(2 * (t * self.frequency - np.floor(t * self.frequency + 0.5))) - 1)
    
    def harmonic_wave(self, duration: float, harmonics: list = [1, 0.5, 0.25, 0.125]) -> np.ndarray:
        """Generate wave with multiple harmonics"""
        t = self._generate_time_array(duration)
        wave = np.zeros_like(t)
        
        for i, harmonic_amp in enumerate(harmonics):
            harmonic_freq = self.frequency * (i + 1)
            wave += harmonic_amp * np.sin(2 * np.pi * harmonic_freq * t)
        
        return self.amplitude * wave / len(harmonics)


class AudioEffects:
    """Apply audio effects to waveforms"""
    
    @staticmethod
    def apply_envelope(wave: np.ndarray, attack: float = 0.1, decay: float = 0.1, 
                      sustain: float = 0.7, release: float = 0.2) -> np.ndarray:
        """Apply ADSR envelope to wave"""
        total_samples = len(wave)
        total_duration = total_samples / SAMPLE_RATE
        
        attack_samples = int(attack * SAMPLE_RATE)
        decay_samples = int(decay * SAMPLE_RATE)
        release_samples = int(release * SAMPLE_RATE)
        sustain_samples = total_samples - attack_samples - decay_samples - release_samples
        
        envelope = np.ones(total_samples)
        
        # Attack
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay
        if decay_samples > 0:
            start_idx = attack_samples
            end_idx = start_idx + decay_samples
            envelope[start_idx:end_idx] = np.linspace(1, sustain, decay_samples)
        
        # Sustain
        if sustain_samples > 0:
            start_idx = attack_samples + decay_samples
            end_idx = start_idx + sustain_samples
            envelope[start_idx:end_idx] = sustain
        
        # Release
        if release_samples > 0:
            envelope[-release_samples:] = np.linspace(sustain, 0, release_samples)
        
        return wave * envelope
    
    @staticmethod
    def apply_reverb(wave: np.ndarray, reverb_amount: float = 0.3, 
                    delay_ms: float = 100) -> np.ndarray:
        """Add reverb effect"""
        delay_samples = int(SAMPLE_RATE * delay_ms / 1000)
        reverb_wave = np.zeros_like(wave)
        
        # Add multiple delayed copies with decreasing amplitude
        for i in range(3):
            delay = delay_samples * (i + 1)
            amplitude = reverb_amount * (0.6 ** i)
            
            if delay < len(wave):
                reverb_wave[delay:] += amplitude * wave[:-delay]
        
        return wave + reverb_wave
    
    @staticmethod
    def apply_vibrato(wave: np.ndarray, rate: float = 5, depth: float = 0.02) -> np.ndarray:
        """Add vibrato (pitch modulation)"""
        t = np.linspace(0, len(wave) / SAMPLE_RATE, len(wave), False)
        vibrato = 1 + depth * np.sin(2 * np.pi * rate * t)
        return wave * vibrato
    
    @staticmethod
    def apply_tremolo(wave: np.ndarray, rate: float = 6, depth: float = 0.3) -> np.ndarray:
        """Add tremolo (amplitude modulation)"""
        t = np.linspace(0, len(wave) / SAMPLE_RATE, len(wave), False)
        tremolo = 1 - depth * np.sin(2 * np.pi * rate * t)
        return wave * tremolo
    
    @staticmethod
    def apply_distortion(wave: np.ndarray, drive: float = 2.0) -> np.ndarray:
        """Add distortion effect"""
        return np.tanh(drive * wave) / drive


class SoundPresets:
    """Pre-configured instrument sounds"""
    
    @staticmethod
    def piano(note: str, octave: int, duration: float = 1.0) -> np.ndarray:
        """Electric piano sound"""
        gen = WaveGenerator(note, octave, amplitude=0.4)
        wave = gen.harmonic_wave(duration, [1, 0.7, 0.3, 0.1])
        wave = AudioEffects.apply_tremolo(wave, rate=4, depth=0.15)
        wave = AudioEffects.apply_envelope(wave, attack=0.01, decay=0.1, sustain=0.7, release=0.3)
        return wave
    
    @staticmethod
    def organ(note: str, octave: int, duration: float = 2.0) -> np.ndarray:
        """Church organ sound"""
        gen = WaveGenerator(note, octave, amplitude=0.3)
        wave = gen.harmonic_wave(duration, [1, 0.8, 0.6, 0.4, 0.3, 0.2])
        wave = AudioEffects.apply_reverb(wave, reverb_amount=0.4)
        wave = AudioEffects.apply_envelope(wave, attack=0.2, decay=0.1, sustain=0.8, release=0.5)
        return wave
    
    @staticmethod
    def guitar(note: str, octave: int, duration: float = 1.5) -> np.ndarray:
        """Acoustic guitar sound"""
        gen = WaveGenerator(note, octave, amplitude=0.4)
        wave = gen.harmonic_wave(duration, [1, 0.6, 0.3, 0.1])
        # Exponential decay for plucked string
        t = np.linspace(0, duration, len(wave), False)
        decay = np.exp(-2 * t / duration)
        wave = wave * decay
        wave = AudioEffects.apply_reverb(wave, reverb_amount=0.2)
        return wave
    
    @staticmethod
    def synth_lead(note: str, octave: int, duration: float = 1.0) -> np.ndarray:
        """Synthesizer lead sound"""
        gen = WaveGenerator(note, octave, amplitude=0.3)
        wave = gen.sawtooth_wave(duration)
        wave = AudioEffects.apply_vibrato(wave, rate=5, depth=0.02)
        wave = AudioEffects.apply_envelope(wave, attack=0.05, decay=0.1, sustain=0.6, release=0.3)
        wave = AudioEffects.apply_reverb(wave, reverb_amount=0.3)
        return wave
    
    @staticmethod
    def bell(note: str, octave: int, duration: float = 3.0) -> np.ndarray:
        """Bell sound"""
        gen = WaveGenerator(note, octave, amplitude=0.4)
        # Inharmonic frequencies for bell-like sound
        t = gen._generate_time_array(duration)
        wave = (np.sin(2 * np.pi * gen.frequency * t) +
                0.6 * np.sin(2 * np.pi * gen.frequency * 2.1 * t) +
                0.4 * np.sin(2 * np.pi * gen.frequency * 3.2 * t))
        
        # Slow exponential decay
        decay = np.exp(-0.8 * t / duration)
        wave = gen.amplitude * wave * decay
        wave = AudioEffects.apply_reverb(wave, reverb_amount=0.5)
        return wave
    
    @staticmethod
    def retro(note: str, octave: int, duration: float = 0.5) -> np.ndarray:
        """8-bit retro game sound"""
        gen = WaveGenerator(note, octave, amplitude=0.3)
        wave = gen.square_wave(duration)
        wave = AudioEffects.apply_envelope(wave, attack=0.01, decay=0.05, sustain=0.6, release=0.1)
        return wave
    
    @staticmethod
    def pad(note: str, octave: int, duration: float = 3.0) -> np.ndarray:
        """Ambient pad sound"""
        gen = WaveGenerator(note, octave, amplitude=0.2)
        wave = gen.harmonic_wave(duration, [1, 0.6, 0.8, 0.4, 0.5])
        wave = AudioEffects.apply_vibrato(wave, rate=3, depth=0.015)
        wave = AudioEffects.apply_reverb(wave, reverb_amount=0.6)
        wave = AudioEffects.apply_envelope(wave, attack=0.8, decay=0.2, sustain=0.7, release=1.0)
        return wave
    
    @staticmethod
    def bass(note: str, octave: int, duration: float = 0.8) -> np.ndarray:
        """Bass sound"""
        gen = WaveGenerator(note, octave, amplitude=0.5)
        wave = gen.sawtooth_wave(duration)
        wave = AudioEffects.apply_envelope(wave, attack=0.02, decay=0.1, sustain=0.5, release=0.2)
        wave = AudioEffects.apply_distortion(wave, drive=1.5)
        return wave
    
    @staticmethod
    def sine(note: str, octave: int, duration: float = 1.0) -> np.ndarray:
        """Pure sine wave"""
        gen = WaveGenerator(note, octave, amplitude=0.3)
        wave = gen.sine_wave(duration)
        wave = AudioEffects.apply_envelope(wave, attack=0.05, decay=0.05, sustain=0.8, release=0.1)
        return wave


class SoundPlayer:
    """Handle playing sounds and chords"""
    
    @staticmethod
    def play_note(note: str, octave: int, sound_type: str = "piano", duration: float = 1.0):
        """Play a single note"""
        try:
            # Get the appropriate sound function
            sound_func = getattr(SoundPresets, sound_type, SoundPresets.piano)
            wave = sound_func(note, octave, duration)
            sd.play(wave, SAMPLE_RATE)
        except Exception as e:
            print(f"Error playing {note}{octave}: {e}")
    
    @staticmethod
    def play_chord(notes: list, octave: int, sound_type: str = "piano", duration: float = 2.0):
        """Play multiple notes simultaneously"""
        try:
            sound_func = getattr(SoundPresets, sound_type, SoundPresets.piano)
            combined_wave = None
            
            for note in notes:
                wave = sound_func(note, octave, duration)
                wave = wave * 0.7  # Reduce volume for mixing
                
                if combined_wave is None:
                    combined_wave = wave
                else:
                    # Ensure same length for addition
                    min_length = min(len(combined_wave), len(wave))
                    combined_wave = combined_wave[:min_length] + wave[:min_length]
            
            sd.play(combined_wave, SAMPLE_RATE)
        except Exception as e:
            print(f"Error playing chord: {e}")
    
    @staticmethod
    def wait():
        """Wait for current playback to finish"""
        sd.wait()


# Available sound presets for easy access
AVAILABLE_SOUNDS = {
    "piano": ("Electric Piano", SoundPresets.piano),
    "organ": ("Church Organ", SoundPresets.organ),
    "guitar": ("Acoustic Guitar", SoundPresets.guitar),
    "synth": ("Synthesizer", SoundPresets.synth_lead),
    "bell": ("Bell", SoundPresets.bell),
    "retro": ("8-bit Retro", SoundPresets.retro),
    "pad": ("Ambient Pad", SoundPresets.pad),
    "bass": ("Bass", SoundPresets.bass),
    "sine": ("Pure Sine", SoundPresets.sine),
}

def demo_sounds():
    """Demo all available sounds"""
    print("🎵 Sound Demo 🎵")
    print("=" * 20)
    
    for sound_key, (sound_name, sound_func) in AVAILABLE_SOUNDS.items():
        print(f"Playing: {sound_name}")
        wave = sound_func('C', 4, 1.0)
        sd.play(wave, SAMPLE_RATE)
        sd.wait()
        print("  ✓ Done\n")

if __name__ == "__main__":
    demo_sounds()