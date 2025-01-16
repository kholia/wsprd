import numpy as np
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
from scipy.fftpack import fft

# Parameters
WSPR_SYMBOL_RATE = 1.4648  # symbols per second
WSPR_TONE_SPACING = 1.4648  # Hz
WSPR_CARRIER_FREQ = 1500  # Hz

def create_waterfall(wave_file):
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
    fft_size = 32768  # Use a larger FFT size for higher frequency resolution

    # Initialize the spectrogram matrix
    num_chunks = len(data) // samples_per_symbol
    spectrogram = np.zeros((fft_size // 2, num_chunks))

    # Process the signal in chunks of samples_per_symbol
    for i in range(num_chunks):
        chunk = data[i * samples_per_symbol : (i + 1) * samples_per_symbol]

        # Perform FFT on the chunk
        fft_result = fft(chunk, fft_size)
        fft_magnitude = np.abs(fft_result[:fft_size // 2])

        # Store the FFT magnitude in the spectrogram matrix
        spectrogram[:, i] = fft_magnitude

    # Create the waterfall display
    plt.figure(figsize=(100, 8))  # Wider figure for better readability

    # Time axis (in symbols)
    time_axis = np.arange(num_chunks) * (1 / WSPR_SYMBOL_RATE)

    # Frequency axis (in Hz)
    freq_axis = np.arange(fft_size // 2) * (sample_rate / fft_size)

    # Limit the frequency range to 1400 Hz to 1600 Hz
    freq_min = 1400
    freq_max = 1600
    freq_mask = (freq_axis >= freq_min) & (freq_axis <= freq_max)
    spectrogram_cropped = spectrogram[freq_mask, :]
    freq_axis_cropped = freq_axis[freq_mask]

    # Plot the spectrogram
    plt.imshow(spectrogram_cropped, aspect='auto', cmap='viridis',
               extent=[time_axis[0], time_axis[-1], freq_axis_cropped[0], freq_axis_cropped[-1]],
               origin='lower')

    # Add labels and title
    plt.xlabel('Time (seconds)')
    plt.ylabel('Frequency (Hz)')
    plt.title('WSPR Waterfall Display (1400 Hz to 1600 Hz)')
    plt.colorbar(label='Magnitude')

    # Set y-axis limits
    plt.ylim(freq_min, freq_max)

    # Enable zooming and panning
    plt.tight_layout()
    plt.savefig('waterfall.png', dpi=600, bbox_inches='tight')
    plt.show(block=True)  # Blocking call to keep the plot open

# Example usage
wave_file = 'wspr_signal.wav'
create_waterfall(wave_file)
