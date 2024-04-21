import numpy as np
import pygame
import random

class PlaySounds:
    def __init__(self, engine):
        self.engine = engine
        self.current_note_index = 0
        self.sounds = []
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
        pygame.mixer.set_num_channels(10)


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
        twinkle_notes = ["C4", "C4", "G4", "G4", "A4", "A4",
                             "G4", "F4", "F4", "E4", "E4", "D4",
                             "D4", "C4", "G4", "G4", "F4", "F4",
                             "E4", "E4", "D4", "G4", "G4", "F4",
                             "F4", "E4", "E4", "D4", "C4", "C4",
                             "G4", "G4", "A4", "A4", "G4", "F4",
                             "F4", "E4", "E4", "D4", "D4", "C4"]

        frequency = self.note_names[twinkle_notes[self.current_note_index]]

        duration_ms = 1000
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
        if self.current_note_index >= len(twinkle_notes):
            self.current_note_index = 0

    def generate_sine_wave(self, frequency, duration_ms, volume):
        sample_rate = 44100
        num_samples = int(sample_rate * duration_ms / 1000)

        time = np.linspace(0, duration_ms / 1000, num_samples, endpoint=False)

        fade_in_duration = 0.0  # Fade-in duration in seconds
        fade_in_samples = int(sample_rate * fade_in_duration)
        fade_in = np.linspace(0, 1, fade_in_samples)

        fade_out_duration = 0.5  # Fade-out duration in seconds
        fade_out_samples = int(sample_rate * fade_out_duration)
        fade_out = np.linspace(1, 0, fade_out_samples)

        sine_wave = np.sin(2 * np.pi * frequency * time)

        sine_wave[:fade_in_samples] *= fade_in

        # Apply the fade-out envelope
        sine_wave[-fade_out_samples:] *= fade_out

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

