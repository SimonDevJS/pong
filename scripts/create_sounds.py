import numpy as np
from scipy.io import wavfile
import os

# Function to create a simple beep sound
def create_beep(filename, frequency=440, duration=0.2, volume=0.5):
    # Sample rate
    sample_rate = 44100
    
    # Generate time array
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Generate sine wave
    note = np.sin(frequency * 2 * np.pi * t)
    
    # Apply volume
    note = note * volume
    
    # Apply fade in and fade out
    fade_duration = int(sample_rate * 0.01)
    fade_in = np.linspace(0, 1, fade_duration)
    fade_out = np.linspace(1, 0, fade_duration)
    
    note[:fade_duration] *= fade_in
    note[-fade_duration:] *= fade_out
    
    # Convert to 16-bit PCM
    audio = np.int16(note * 32767)
    
    # Save to file
    wavfile.write(filename, sample_rate, audio)
    print(f"Created sound file: {filename}")

# Create directory for sounds if it doesn't exist
os.makedirs("sounds", exist_ok=True)

# Create different sound effects
create_beep("sounds/golpe_paleta.wav", frequency=880, duration=0.1, volume=0.7)
create_beep("sounds/golpe_pared.wav", frequency=660, duration=0.1, volume=0.5)
create_beep("sounds/punto.wav", frequency=440, duration=0.3, volume=0.8)
create_beep("sounds/cuenta.wav", frequency=330, duration=0.2, volume=0.6)
create_beep("sounds/inicio.wav", frequency=[440, 550, 660], duration=0.5, volume=0.8)

print("All sound files created successfully!")
