import os
import ast
import numpy as np
import pygame
from plover.resource import resource_exists, resource_filename
from plover.oslayer.config import CONFIG_DIR

default_mode = "mapped"
default_melody_notes = [
    "C4", "C4", "G4", "G4", "A4", "A4",
    "G4", "F4", "F4", "E4", "E4", "D4",
    "D4", "C4", "G4", "G4", "F4", "F4",
    "E4", "E4", "D4", "G4", "G4", "F4",
    "F4", "E4", "E4", "D4", "C4", "C4",
    "G4", "G4", "A4", "A4", "G4", "F4",
    "F4", "E4", "E4", "D4", "D4", "C4"
]

default_note_map = {
    '#': 'F1', 'S-': 'C2', 'T-': 'G#2', 'K-': 'A#2', 'P-': 'D#3', 'W-': 'G3', 'H-': 'G#3',
    'R-': 'F2', 'A-': 'C3', 'O-': 'G#3', '*': 'A#3', '-E': 'D#4', '-U': 'G4', '-F': 'G#4',
    '-R': 'F3', '-P': 'C4', '-B': 'G#4', '-L': 'A#4', '-G': 'D#5', '-T': 'G5', '-S': 'G#5', '-D': 'F4',
    '-Z': 'C5',
}
delay_ms = 40

default_sample_path = "asset:plover_sound:keyboard-click.mp3"
if not resource_exists(default_sample_path):
    raise Exception("Couldn't find default audio sample file")
else:
   default_sample_path = resource_filename(default_sample_path)


class PlaySounds:
    def __init__(self, engine):
        self.config_file_path = os.path.join(CONFIG_DIR, "plover_sound_conf.py")
        self.set_initial_values()
        self.delay_ms = delay_ms
        self.engine = engine
        self.current_note_index = 0
        self.sounds = []
        if not resource_exists(self.sample_path):
            raise Exception("Couldn't find audio sample file")
        self.sample = resource_filename(self.sample_path)
        self.active_channels = []
        pygame.mixer.init()

        starting_freq = 27.5  # Frequency of A0
        ending_freq = 4186.01  # Frequency of C8
        num_notes = 88  # Number of notes on a standard piano

        note_ratios = 2 ** (1 / 12)  # The ratio between adjacent notes
        self.note_freqs = [starting_freq * (note_ratios ** i) for i in range(num_notes)]

        # Map frequencies to note names
        self.note_names = self.generate_note_names()

        # Handle overlapping notes
        pygame.mixer.set_num_channels(23)

    def set_initial_values(self):
        config_dict = self.load_config()
        # Set radio button
        self.mode = config_dict['mode']
        self.melody_notes = config_dict['melody_notes']
        self.note_map = config_dict['note_map']
        self.sample_path = config_dict['sample_path']

    def load_config(self):
        # Check if configuration file exists
        try:
            with open(self.config_file_path, 'r') as config_file:
                config_content = config_file.read()
                config_dict = ast.literal_eval(config_content)
        except FileNotFoundError:
            # Configuration file doesn't exist, create with default values
            config_dict = {
                'mode': default_mode,
                'melody_notes': default_melody_notes,
                'note_map': default_note_map,
                'sample_path': default_sample_path
            }
            with open(self.config_file_path, 'w') as config_file:
                config_file.write(str(config_dict))

        except SyntaxError:
            raise Exception("Error in config syntax")
            return
        return config_dict

    def generate_note_names(self):
        # Notes on the piano
        note_names = [
                "A0", "A#0", "B0",
                "C1", "C#1", "D1", "D#1", "E1", "F1", "F#1", "G1", "G#1",
                "A1", "A#1", "B1",
                "C2", "C#2", "D2", "D#2", "E2", "F2", "F#2", "G2", "G#2",
                "A2", "A#2", "B2",
                "C3", "C#3", "D3", "D#3", "E3", "F3", "F#3", "G3", "G#3",
                "A3", "A#3", "B3",
                "C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4",
                "A4", "A#4", "B4",
                "C5", "C#5", "D5", "D#5", "E5", "F5", "F#5", "G5", "G#5",
                "A5", "A#5", "B5",
                "C6", "C#6", "D6", "D#6", "E6", "F6", "F#6", "G6", "G#6",
                "A6", "A#6", "B6",
                "C7", "C#7", "D7", "D#7", "E7", "F7", "F#7", "G7", "G#7",
                "A7", "A#7", "B7",
                "C8"
                ]

        note_dict = {}
        for i, note in enumerate(note_names):
            note_dict[note] = self.note_freqs[i]

        return note_dict

    def start(self):
        self.engine.hook_connect("stroked", self.on_stroked)

    def stop(self):
        self.engine.hook_disconnect("stroked", self.on_stroked)

    def on_stroked(self, stroke):
        if not self.engine.output:
            return

        if self.mode == "sample":
            self.play_sample()
        elif self.mode == "melody":
            self.play_melody()
        elif self.mode == "mapped":
            self.play_mapped(stroke)
        else:
            pass

    def play_mapped(self, stroke):
        # Example of strokes: ['H-', '-E', '-U']

        # Get frequencies for each stroke
        frequencies = [self.note_names[self.note_map[i]] for i in stroke]

        # Generate sine waves for each frequency
        sounds = [self.generate_sine_wave(frequency, duration_ms=500, volume=0.3) for frequency in frequencies]

        # Play each sound on a separate channel with a delay between notes
        for sound in sounds:
            channel = pygame.mixer.find_channel()

            # If no available channel found, stop the oldest one
            if channel is None:
                oldest_channel = self.active_channels.pop(0)
                oldest_channel.stop()
                channel = pygame.mixer.find_channel()

            channel.play(sound)
            self.active_channels.append(channel)

            # Apply the delay between notes
            pygame.time.delay(self.delay_ms)

    def play_melody(self):
        frequency = self.note_names[self.melody_notes[self.current_note_index]]
        duration_ms = 2000
        volume = 0.3  # (0.0 to 1.0)
        sound = self.generate_sine_wave(frequency, duration_ms, volume)

        channel = pygame.mixer.find_channel()

        # If no available channel found, stop the oldest one
        if channel is None:
            oldest_channel = self.active_channels.pop(0)
            oldest_channel.stop()
            channel = pygame.mixer.find_channel()

        channel.play(sound)
        self.active_channels.append(channel)

        self.current_note_index += 1
        if self.current_note_index >= len(self.melody_notes):
            self.current_note_index = 0

        sample_rate = 44100

    def generate_sine_wave(self, frequency, duration_ms, volume):
        sample_rate = 44100
        num_samples = int(sample_rate * duration_ms / 1000)

        time = np.linspace(0, duration_ms / 1000, num_samples, endpoint=False)

        fade_in_duration = 0.0  # Fade-in duration in seconds
        fade_in_samples = int(sample_rate * fade_in_duration)
        fade_in = np.linspace(0, 1, fade_in_samples, endpoint=False)

        fade_out_duration = 1.0  # Fade-out duration in seconds
        fade_out_samples = int(sample_rate * fade_out_duration)

        # Ensure that the fade-out does not exceed half of the total duration
        fade_out_samples = min(fade_out_samples, num_samples // 2)

        # Calculate the starting index for the fade-out
        fade_out_start_index = num_samples - fade_out_samples

        # Create fade-out array starting from the calculated index
        fade_out = np.linspace(1, 0, fade_out_samples, endpoint=False)

        sine_wave = np.sin(2 * np.pi * frequency * time)

        sine_wave[:fade_in_samples] *= fade_in

        # Apply the fade-out envelope starting from the calculated index
        sine_wave[fade_out_start_index:] *= fade_out

        # Scale the sine wave to the range [-1, 1] and adjust the volume
        amplitude = 10 ** (-10 / 20)  # Convert -10 dB to amplitude
        sine_wave *= amplitude * volume  # Adjust volume

        # Convert the scaled sine wave to 16-bit integers
        sound_data = np.int16(sine_wave * 32767)

        # Convert the sound data to bytes
        sound_bytes = sound_data.tobytes()

        # Create a Sound object from the sound data
        sound = pygame.mixer.Sound(sound_bytes)

        return sound

    def play_sample(self):
        # Load the sample
        sample = pygame.mixer.Sound(self.sample)

        # Play the sample
        channel = pygame.mixer.find_channel()

        # If no available channel found, stop the oldest one
        if channel is None:
            oldest_channel = self.active_channels.pop(0)
            oldest_channel.stop()
            channel = pygame.mixer.find_channel()

        channel.play(sample)
        self.active_channels.append(channel)
