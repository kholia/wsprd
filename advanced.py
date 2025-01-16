import numpy as np
from scipy.io import wavfile
from scipy import signal
import scipy.fftpack as fftpack
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List, Any

class WSPRDecoder:
    def __init__(self):
        # WSPR constants
        self.SYMBOL_PERIOD = 0.683  # seconds
        self.NUM_SYMBOLS = 162
        self.SIGNAL_LENGTH = 110.6  # seconds
        self.SYNC_SYMBOLS = [1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0]
        self.WSPR_FREQ_MIN = 1400  # Hz
        self.WSPR_FREQ_MAX = 1600  # Hz
        self.WSPR_FREQ_SPACING = 1.4648  # Hz per symbol

        # Callsign encoding constants
        self.CALLSIGN_CHARS = ' 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def read_wav(self, filename: str) -> Tuple[int, np.ndarray]:
        """Read WAV file and return sample rate and data"""
        sample_rate, data = wavfile.read(filename)

        # Convert stereo to mono if necessary
        if len(data.shape) > 1:
            data = np.mean(data, axis=1)

        # Ensure we have enough samples for full WSPR transmission
        required_samples = int(self.SIGNAL_LENGTH * sample_rate)
        if len(data) < required_samples:
            raise ValueError(f"WAV file too short. Need {required_samples} samples, got {len(data)}")

        return sample_rate, data

    def preprocess_signal(self, data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Preprocess the signal with bandpass filtering"""
        # Normalize the signal
        data = data / np.max(np.abs(data))

        # Design bandpass filter
        nyquist = sample_rate / 2
        low = self.WSPR_FREQ_MIN / nyquist
        high = self.WSPR_FREQ_MAX / nyquist
        b, a = signal.butter(3, [low, high], btype='band')

        # Apply filter
        filtered_data = signal.filtfilt(b, a, data)

        return filtered_data

    def detect_symbols(self, filtered_data: np.ndarray, sample_rate: int) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """Detect WSPR symbols and return frequency and quality metrics"""
        samples_per_symbol = int(self.SYMBOL_PERIOD * sample_rate)
        total_samples = len(filtered_data)

        # Pre-allocate arrays
        symbols = np.zeros(self.NUM_SYMBOLS, dtype=float)
        metrics = []

        # Calculate frequency resolution
        freq_resolution = sample_rate / samples_per_symbol

        print(f"Debug info:")
        print(f"Sample rate: {sample_rate} Hz")
        print(f"Samples per symbol: {samples_per_symbol}")
        print(f"Frequency resolution: {freq_resolution:.2f} Hz")

        # Process symbols
        for i in range(self.NUM_SYMBOLS):
            start = i * samples_per_symbol
            end = start + samples_per_symbol

            segment = filtered_data[start:end]
            window = np.blackman(len(segment))
            windowed_segment = segment * window

            # Compute FFT
            fft_result = np.abs(fftpack.fft(windowed_segment))
            freqs = fftpack.fftfreq(len(fft_result), 1/sample_rate)

            # Find peak in WSPR band
            wspr_mask = (freqs >= self.WSPR_FREQ_MIN) & (freqs <= self.WSPR_FREQ_MAX)
            peak_idx = np.argmax(fft_result[wspr_mask])
            peak_freq = freqs[wspr_mask][peak_idx]
            peak_amplitude = fft_result[wspr_mask][peak_idx]

            # Calculate signal quality metrics
            noise_floor = np.median(fft_result[wspr_mask])
            snr = 10 * np.log10(peak_amplitude / noise_floor)

            # Store frequency and metrics
            symbols[i] = peak_freq
            metrics.append({
                'frequency': peak_freq,
                'snr': snr,
                'amplitude': peak_amplitude,
                'noise_floor': noise_floor
            })

        print(f"Detected {len(symbols)} symbols")
        return symbols, metrics

    def plot_spectrum(self, metrics: List[Dict[str, Any]], title: str = "WSPR Signal Spectrum"):
        """Plot the signal spectrum over time"""
        plt.figure(figsize=(12, 6))

        # Extract frequencies and SNRs
        times = np.arange(len(metrics)) * self.SYMBOL_PERIOD
        freqs = [m['frequency'] for m in metrics]
        snrs = [m['snr'] for m in metrics]

        # Create scatter plot colored by SNR
        scatter = plt.scatter(times, freqs, c=snrs, cmap='viridis')
        plt.colorbar(scatter, label='SNR (dB)')

        plt.title(title)
        plt.xlabel('Time (s)')
        plt.ylabel('Frequency (Hz)')
        plt.ylim(self.WSPR_FREQ_MIN - 10, self.WSPR_FREQ_MAX + 10)
        plt.grid(True)

        # Add tone bands
        for i in range(4):
            freq = self.WSPR_FREQ_MIN + i * ((self.WSPR_FREQ_MAX - self.WSPR_FREQ_MIN) / 4)
            plt.axhline(y=freq, color='r', linestyle='--', alpha=0.3)

        plt.show()

    def sync_and_decode(self, symbols: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Synchronize and decode the symbols"""
        # Convert frequencies to symbol numbers (0-3 for WSPR)
        symbol_spacing = (self.WSPR_FREQ_MAX - self.WSPR_FREQ_MIN) / 4
        normalized_symbols = np.floor((symbols - self.WSPR_FREQ_MIN) / symbol_spacing).astype(int)
        normalized_symbols = np.clip(normalized_symbols, 0, 3)  # Ensure values are 0-3

        # Find sync pattern using circular correlation
        correlation = np.correlate(np.concatenate([normalized_symbols, normalized_symbols]),
                                 self.SYNC_SYMBOLS, mode='valid')
        sync_start = np.argmax(correlation) % len(normalized_symbols)

        print(f"Sync pattern found at position: {sync_start}")

        # Extract synchronized symbols
        synchronized_symbols = np.zeros(self.NUM_SYMBOLS, dtype=int)
        synchronized_freqs = np.zeros(self.NUM_SYMBOLS, dtype=float)

        for i in range(self.NUM_SYMBOLS):
            idx = (sync_start + i) % len(symbols)
            synchronized_symbols[i] = normalized_symbols[idx]
            synchronized_freqs[i] = symbols[idx]

        return synchronized_symbols, synchronized_freqs

    def convolutional_decode(self, symbols: np.ndarray) -> np.ndarray:
        """Simple convolutional decoder for WSPR symbols"""
        # This is a simplified implementation - real WSPR uses a more complex scheme
        decoded = np.zeros(len(symbols) // 2, dtype=int)
        for i in range(0, len(symbols) - 1, 2):
            symbol_pair = symbols[i:i+2]
            # Simple hard decision decoding
            decoded[i//2] = (symbol_pair[0] * 2 + symbol_pair[1]) % 4
        return decoded

    def decode_callsign(self, symbols: np.ndarray) -> str:
        """Decode callsign from symbols using WSPR protocol"""
        try:
            # Simplified decoding - real WSPR uses more complex encoding
            decoded_symbols = self.convolutional_decode(symbols)

            # Convert symbols to bits (2 bits per symbol)
            bits = []
            for symbol in decoded_symbols[:28]:  # First 28 bits typically contain callsign
                bits.extend([symbol & 2, symbol & 1])

            # Convert bits to characters (simplified)
            chars = []
            for i in range(0, len(bits), 6):
                if i + 6 <= len(bits):
                    char_bits = bits[i:i+6]
                    char_value = sum(b << (5-j) for j, b in enumerate(char_bits))
                    if char_value < len(self.CALLSIGN_CHARS):
                        chars.append(self.CALLSIGN_CHARS[char_value])

            result = ''.join(chars)
            return result if result.strip() else "Decoding failed: No valid callsign found"

        except Exception as e:
            return f"Decoding failed: {str(e)}"

    def decode_file(self, filename: str) -> Dict[str, Any]:
        """Main decoding function"""
        try:
            # Read and preprocess
            sample_rate, data = self.read_wav(filename)
            filtered_data = self.preprocess_signal(data, sample_rate)

            # Detect symbols and get metrics
            symbols, metrics = self.detect_symbols(filtered_data, sample_rate)

            # Plot spectrum
            self.plot_spectrum(metrics)

            # Synchronize and decode
            sync_symbols, sync_freqs = self.sync_and_decode(symbols)
            callsign = self.decode_callsign(sync_symbols)

            # Calculate average SNR
            avg_snr = np.mean([m['snr'] for m in metrics])

            return {
                'status': 'success',
                'symbols': sync_symbols.tolist(),
                'frequencies': sync_freqs.tolist(),
                'callsign': callsign,
                'symbol_count': len(sync_symbols),
                'average_snr': avg_snr,
                'metrics': metrics
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

# Example usage
if __name__ == "__main__":
    decoder = WSPRDecoder()
    result = decoder.decode_file("wspr_recording.wav")
    print(result)
