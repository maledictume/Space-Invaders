import pygame
import math
import numpy as np
import random

sounds = {}

def generate_sine_wave(freq, duration, volume=0.5, sample_rate=44100):
    samples = int(duration * sample_rate)
    buffer = np.zeros((samples, 2), dtype=np.int16)
    amplitude = volume * 32767
    for i in range(samples):
        value = int(amplitude * math.sin(2 * math.pi * freq * i / sample_rate))
        buffer[i][0] = value
        buffer[i][1] = value
    return pygame.sndarray.make_sound(buffer)

def generate_square_wave(freq, duration, volume=0.5, sample_rate=44100):
    samples = int(duration * sample_rate)
    buffer = np.zeros((samples, 2), dtype=np.int16)
    amplitude = volume * 32767
    period = sample_rate / freq
    for i in range(samples):
        value = amplitude if (i % period) < (period / 2) else -amplitude
        buffer[i][0] = value
        buffer[i][1] = value
    return pygame.sndarray.make_sound(buffer)

def generate_explosion_sound():
    sample_rate = 44100
    duration = 0.8
    samples = int(duration * sample_rate)
    buffer = np.zeros((samples, 2), dtype=np.int16)
    for i in range(samples):
        progress = i / samples
        freq = 200 * (1 - progress) + 50
        noise = random.randint(-20000, 20000) * (1 - progress)
        value = int(noise + 10000 * math.sin(2 * math.pi * freq * i / sample_rate) * (1 - progress))
        buffer[i][0] = value
        buffer[i][1] = value
    return pygame.sndarray.make_sound(buffer)

def generate_background_music():
    sample_rate = 44100
    duration = 2.0
    samples = int(duration * sample_rate)
    buffer = np.zeros((samples, 2), dtype=np.int16)
    bass_pattern = [220, 196, 165, 147]
    melody_pattern = [440, 392, 330, 294]
    for i in range(samples):
        progress = i / samples
        pattern_pos = int(progress * 4) % 4
        bass_freq = bass_pattern[pattern_pos]
        bass = 0.3 * math.sin(2 * math.pi * bass_freq * i / sample_rate)
        melody_freq = melody_pattern[pattern_pos]
        melody = 0.2 * math.sin(2 * math.pi * melody_freq * i / sample_rate)
        beat = 0 if (i % (sample_rate / 4)) < (sample_rate / 8) else 0.1
        value = int(32767 * (bass + melody + beat))
        buffer[i][0] = value
        buffer[i][1] = value
    sound = pygame.sndarray.make_sound(buffer)
    sound.set_volume(0.3)
    return sound

def init_audio():
    global sounds
    try:
        sounds['bgm'] = generate_background_music()
        sounds['shoot'] = generate_square_wave(880, 0.1, 0.3)
        sounds['enemy_shoot'] = generate_square_wave(220, 0.2, 0.2)
        sounds['explosion'] = generate_explosion_sound()
        sounds['mystery'] = generate_sine_wave(523.25, 0.5, 0.4)
        sounds['bgm'].play(-1)
    except Exception:
        pass

def play_sound(name):
    if name in sounds and sounds[name]:
        sounds[name].play()