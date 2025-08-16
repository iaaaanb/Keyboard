import keyboard
import threading
import time
from wavemaker import SoundPlayer, AVAILABLE_SOUNDS
from notes import is_valid_note

class PianoKeyboard:
    """Interactive piano keyboard using computer keys"""
    
    def __init__(self):
        self.current_octave = 4
        self.current_sound = "piano"
        self.running = True
        
        # Keyboard layout mapping
        self.key_mapping = {
            # White keys (natural notes)
            'z': 'C', 'x': 'D', 'c': 'E', 'v': 'F', 
            'b': 'G', 'n': 'A', 'm': 'B',
            ',': 'C', '.': 'D', '/': 'E',  # Next octave
            
            # Black keys (sharps/flats)
            's': 'C#', 'd': 'D#', 'g': 'F#', 
            'h': 'G#', 'j': 'A#', 'l': 'C#', ';': 'D#',  # Next octave
        }
        
        # Sound selection (number keys)
        self.sound_keys = {
            '1': "piano",
            '2': "organ", 
            '3': "guitar",
            '4': "synth",
            '5': "bell",
            '6': "retro",
            '7': "pad",
            '8': "bass",
            '9': "sine",
        }
        
        # Chord definitions
        self.chords = {
            'major': ['C', 'E', 'G'],
            'minor': ['C', 'Eb', 'G'],
            'seventh': ['C', 'E', 'G', 'B'],
            'sus4': ['C', 'F', 'G'],
        }
        
        self.current_chord = 'major'
    
    def get_octave_for_note(self, note: str) -> int:
        """Calculate correct octave for note based on keyboard layout"""
        # Notes after 'B' go to next octave
        if note in ['C', 'D', 'E'] and hasattr(self, '_last_played_note'):
            if self._last_played_note in ['A', 'B', 'A#']:
                return self.current_octave + 1
        
        # Handle extended keys (,./;) which are next octave
        return self.current_octave
    
    def play_note(self, note: str):
        """Play a single note"""
        octave = self.get_octave_for_note(note)
        
        # Check if note is valid
        if not is_valid_note(note, octave):
            if octave > 0:  # Try lower octave
                octave -= 1
            if not is_valid_note(note, octave):
                print(f"⚠️  Note {note}{octave} not available")
                return
        
        # Play the note in a separate thread to avoid blocking
        threading.Thread(
            target=SoundPlayer.play_note, 
            args=(note, octave, self.current_sound, 1.0),
            daemon=True
        ).start()
        
        # Show what's playing
        sound_name = AVAILABLE_SOUNDS[self.current_sound][0]
        print(f"♪ {note}{octave} - {sound_name}")
        self._last_played_note = note
    
    def play_chord(self):
        """Play current chord type"""
        chord_notes = self.chords[self.current_chord]
        octave = self.current_octave
        
        # Play chord in separate thread
        threading.Thread(
            target=SoundPlayer.play_chord,
            args=(chord_notes, octave, self.current_sound, 2.0),
            daemon=True
        ).start()
        
        sound_name = AVAILABLE_SOUNDS[self.current_sound][0]
        chord_display = " + ".join([f"{note}{octave}" for note in chord_notes])
        print(f"🎵 {self.current_chord.title()} Chord: {chord_display} - {sound_name}")
    
    def change_octave(self, direction: int):
        """Change current octave"""
        new_octave = self.current_octave + direction
        if 0 <= new_octave <= 8:
            self.current_octave = new_octave
            self.show_status()
    
    def change_sound(self, sound_key: str):
        """Change current sound preset"""
        if sound_key in self.sound_keys:
            self.current_sound = self.sound_keys[sound_key]
            self.show_status()
    
    def cycle_chord(self):
        """Cycle through chord types"""
        chord_list = list(self.chords.keys())
        current_index = chord_list.index(self.current_chord)
        next_index = (current_index + 1) % len(chord_list)
        self.current_chord = chord_list[next_index]
        print(f"🎵 Chord type: {self.current_chord.title()}")
    
    def show_status(self):
        """Display current settings"""
        sound_name = AVAILABLE_SOUNDS[self.current_sound][0]
        print(f"🎵 {sound_name} | Octave: {self.current_octave} | Chord: {self.current_chord.title()}")
    
    def show_help(self):
        """Display help information"""
        print("\n" + "="*60)
        print("🎹 PIANO KEYBOARD HELP 🎹")
        print("="*60)
        
        print("\n🎹 PIANO KEYS:")
        print("   White keys: Z X C V B N M , . /")
        print("   Black keys: S D   G H J   L ;")
        print("\n   Layout visualization:")
        print("     S D   G H J   L ;")
        print("    Z X C V B N M , . /")
        print("    C D E F G A B C D E")
        
        print("\n🎵 SOUNDS (Number Keys 1-9):")
        for key, sound_id in self.sound_keys.items():
            sound_name = AVAILABLE_SOUNDS[sound_id][0]
            print(f"   {key}: {sound_name}")
        
        print("\n🎛️  CONTROLS:")
        print("   ↑/↓: Change octave")
        print("   SPACE: Play chord")
        print("   TAB: Cycle chord type (major/minor/7th/sus4)")
        print("   R: Random sound")
        print("   H: Show this help")
        print("   ESC/Q: Quit")
        
        print("\n🎵 CURRENT SETTINGS:")
        sound_name = AVAILABLE_SOUNDS[self.current_sound][0]
        print(f"   Sound: {sound_name}")
        print(f"   Octave: {self.current_octave}")
        print(f"   Chord: {self.current_chord.title()}")
        
        print("\n" + "="*60)
    
    def random_sound(self):
        """Switch to random sound"""
        import random
        self.current_sound = random.choice(list(self.sound_keys.values()))
        self.show_status()
    
    def on_key_press(self, event):
        """Handle keyboard events"""
        key = event.name.lower()
        
        # Sound selection (number keys)
        if key in self.sound_keys:
            self.change_sound(key)
            return
        
        # Piano keys
        if key in self.key_mapping:
            note = self.key_mapping[key]
            self.play_note(note)
            return
        
        # Control keys
        if key == 'up':
            self.change_octave(1)
        elif key == 'down':
            self.change_octave(-1)
        elif key == 'space':
            self.play_chord()
        elif key == 'tab':
            self.cycle_chord()
        elif key == 'r':
            self.random_sound()
        elif key == 'h':
            self.show_help()
        elif key in ['esc', 'q']:
            self.quit()
    
    def quit(self):
        """Quit the piano"""
        print("\n🎵 Thanks for playing! 🎵")
        self.running = False
    
    def start(self):
        """Start the piano keyboard"""
        print("🎹 Initializing Piano Keyboard...")
        
        # Test audio
        try:
            print("Testing audio system...")
            SoundPlayer.play_note('A', 4, 'sine', 0.2)
            SoundPlayer.wait()
            print("✓ Audio system ready!")
        except Exception as e:
            print(f"❌ Audio error: {e}")
            return
        
        # Show initial interface
        self.show_help()
        
        # Setup keyboard listener
        keyboard.on_press(self.on_key_press)
        
        try:
            print("\n🎵 Piano is ready! Press 'H' for help anytime. 🎵\n")
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
        finally:
            print("🎵 Shutting down...")
            keyboard.unhook_all()


def main():
    """Main function to run the piano"""
    try:
        piano = PianoKeyboard()
        piano.start()
    except ImportError as e:
        if "keyboard" in str(e):
            print("❌ Missing dependency!")
            print("Please install: pip3 install --break-system-packages keyboard")
        else:
            print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()