import numpy as np
import scipy.io.wavfile as wav
from scipy.fftpack import fft

# WSPR parameters
WSPR_SYMBOL_RATE = 1.4648  # symbols per second
WSPR_TONE_SPACING = 1.4648  # Hz
WSPR_CARRIER_FREQ = 1500  # Hz

def decode_wspr(wave_file):
    # Read the WAVE file
    sample_rate, data = wav.read(wave_file)

    # Ensure the data is mono
    if len(data.shape) > 1:
        data = data[:, 0]

    # Normalize the data
    data = data.astype(np.float32) / np.max(np.abs(data))

    # Calculate the number of samples per symbol
    samples_per_symbol = int(sample_rate / WSPR_SYMBOL_RATE)

    # Determine the FFT size based on the sample rate
    fft_size = 8192  # Default FFT size
    if sample_rate > 12000:
        fft_size = 32768  # Use a larger FFT size for higher sample rates

    # Initialize the decoded message
    decoded_message = []

    # Process the signal in chunks of samples_per_symbol
    for i in range(0, len(data), samples_per_symbol):
        chunk = data[i:i + samples_per_symbol]

        # Perform FFT on the chunk
        fft_result = fft(chunk, fft_size)
        fft_magnitude = np.abs(fft_result[:fft_size // 2])

        # Find the peak frequency
        peak_bin = np.argmax(fft_magnitude)
        peak_freq = peak_bin * (sample_rate / fft_size)

        # Calculate the tone index
        tone_index = int(round((peak_freq - WSPR_CARRIER_FREQ) / WSPR_TONE_SPACING))

        # Map the tone index to a symbol (0, 1, 2, or 3)
        symbol = tone_index % 4
        decoded_message.append(symbol)

        # Debugging output
        print(f"Chunk {i // samples_per_symbol + 1}: Peak Freq = {peak_freq:.2f} Hz, Tone Index = {tone_index}, Symbol = {symbol}")

    # Convert symbols to a message
    message = ' '.join(map(str, decoded_message))

    return message

# Example usage
wave_file = 'wspr_signal.wav'
decoded_message = decode_wspr(wave_file)
print(f"Decoded WSPR message: {decoded_message}")
