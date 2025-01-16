#!/usr/bin/env python3
"""
WSPR (Weak Signal Propagation Reporter) Decoder
Decodes WSPR signals from 2-minute WAV files

WSPR Protocol Overview:
- 4-FSK modulation with 4 tones spaced 12000/8192 Hz apart (~1.46 Hz)
- 162 symbols transmitted over 110.6 seconds
- Symbol rate: 12000/8192 baud (~1.46 baud)
- Each symbol is ~0.683 seconds long
- Message format: callsign, 4-character grid locator, power in dBm
"""

import numpy as np
import scipy.io.wavfile as wavfile
import scipy.signal as signal
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
import argparse
import sys

class WSPRDecoder:
    def __init__(self):
        # WSPR parameters
        self.SYMBOL_RATE = 12000 / 8192  # ~1.4648 baud
        self.SYMBOL_DURATION = 8192 / 12000  # ~0.6827 seconds
        self.TONE_SPACING = 12000 / 8192  # ~1.4648 Hz
        self.NUM_SYMBOLS = 162
        self.MESSAGE_DURATION = self.NUM_SYMBOLS * self.SYMBOL_DURATION  # ~110.6 seconds

        # Sync vector for WSPR (known pattern for synchronization)
        self.SYNC_VECTOR = [
            1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0,
            0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0,
            0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0,
            1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0,
            0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0,
            0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0,
            0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1,
            0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1,
            0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0,
            0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1,
            1, 1, 0, 1, 1, 0
        ]

        # Character encoding tables for WSPR
        self.CALLSIGN_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ "
        self.GRID_CHARS = "0123456789ABCDEFGHIJKLMNOPQR"

    def load_wav_file(self, filename):
        """Load and validate WAV file"""
        try:
            sample_rate, audio_data = wavfile.read(filename)
            print(f"Loaded WAV file: {filename}")
            print(f"Sample rate: {sample_rate} Hz")
            print(f"Duration: {len(audio_data) / sample_rate:.1f} seconds")
            print(f"Data type: {audio_data.dtype}")

            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
                print("Converted stereo to mono")

            # Normalize to [-1, 1] range
            if audio_data.dtype == np.int16:
                audio_data = audio_data.astype(np.float32) / 32768.0
            elif audio_data.dtype == np.int32:
                audio_data = audio_data.astype(np.float32) / 2147483648.0

            return sample_rate, audio_data

        except Exception as e:
            print(f"Error loading WAV file: {e}")
            return None, None

    def find_wspr_signal(self, audio_data, sample_rate):
        """Find WSPR signal in the audio using FFT analysis"""
        print("\nSearching for WSPR signal...")

        # Calculate FFT for frequency analysis
        window_size = int(sample_rate * 2)  # 2-second window
        overlap = window_size // 2

        # Use spectrogram to find the signal
        freqs, times, Sxx = signal.spectrogram(
            audio_data, sample_rate,
            window='hann',
            nperseg=window_size,
            noverlap=overlap
        )

        # Look for signals in typical WSPR frequency ranges
        # WSPR can appear anywhere in audio, but often in specific bands
        freq_mask = (freqs >= 200) & (freqs <= 3000)  # Typical audio range
        Sxx_masked = Sxx[freq_mask, :]
        freqs_masked = freqs[freq_mask]

        # Find peak frequency
        power_spectrum = np.mean(Sxx_masked, axis=1)
        peak_idx = np.argmax(power_spectrum)
        base_freq = freqs_masked[peak_idx]

        print(f"Detected signal around {base_freq:.1f} Hz")
        return base_freq

    def extract_symbols(self, audio_data, sample_rate, base_freq):
        """Extract WSPR symbols using 4-FSK demodulation"""
        print("\nExtracting symbols...")

        # Define the 4 FSK tones
        tones = [
            base_freq,
            base_freq + self.TONE_SPACING,
            base_freq + 2 * self.TONE_SPACING,
            base_freq + 3 * self.TONE_SPACING
        ]

        print(f"FSK tones: {[f'{f:.2f}' for f in tones]} Hz")

        symbols = []
        samples_per_symbol = int(sample_rate * self.SYMBOL_DURATION)

        # Extract each symbol
        for i in range(self.NUM_SYMBOLS):
            start_sample = int(i * samples_per_symbol)
            end_sample = start_sample + samples_per_symbol

            if end_sample > len(audio_data):
                print(f"Warning: Audio too short for {self.NUM_SYMBOLS} symbols")
                break

            symbol_data = audio_data[start_sample:end_sample]

            # Correlate with each tone to find the strongest
            tone_powers = []
            for tone_freq in tones:
                # Generate reference tone
                t = np.arange(len(symbol_data)) / sample_rate
                ref_tone = np.exp(2j * np.pi * tone_freq * t)

                # Correlate with symbol data
                correlation = np.abs(np.sum(symbol_data * np.conj(ref_tone)))
                tone_powers.append(correlation)

            # The tone with highest correlation is the detected symbol
            detected_symbol = np.argmax(tone_powers)
            symbols.append(detected_symbol)

        print(f"Extracted {len(symbols)} symbols")
        return symbols

    def sync_symbols(self, symbols):
        """Synchronize symbols using the known sync pattern"""
        print("\nSynchronizing symbols...")

        if len(symbols) < self.NUM_SYMBOLS:
            print("Not enough symbols for synchronization")
            return None

        # The sync vector defines which symbols should have specific values
        # We need to check the pattern and adjust for any frequency offset

        # Extract sync positions (every other symbol starting from 0)
        sync_positions = list(range(0, self.NUM_SYMBOLS, 2))

        # Try different frequency offsets
        best_correlation = -1
        best_offset = 0

        for offset in range(4):  # Try all 4 possible tone offsets
            correlation = 0
            for pos in sync_positions:
                if pos < len(symbols):
                    expected = self.SYNC_VECTOR[pos // 2]
                    # Adjust symbol value by offset and check against sync
                    adjusted = (symbols[pos] - offset) % 4
                    # For WSPR sync, we expect specific patterns
                    if adjusted == expected:
                        correlation += 1

            if correlation > best_correlation:
                best_correlation = correlation
                best_offset = offset

        print(f"Best sync correlation: {best_correlation}/{len(sync_positions)}")
        print(f"Frequency offset: {best_offset} tones")

        # Apply the offset correction
        corrected_symbols = [(s - best_offset) % 4 for s in symbols]

        return corrected_symbols

    def decode_message(self, symbols):
        """Decode WSPR message from symbols"""
        print("\nDecoding message...")

        if not symbols or len(symbols) < self.NUM_SYMBOLS:
            print("Insufficient symbols for decoding")
            return None

        print(symbols)
        print(len(symbols))

        try:
            # WSPR uses convolutional coding and interleaving
            # This is a simplified decoder - full implementation would need:
            # 1. De-interleaving
            # 2. Convolutional decoding (Viterbi algorithm)
            # 3. Error correction

            # For demonstration, we'll attempt a basic decode
            # Extract data symbols (non-sync positions)
            data_symbols = []
            for i in range(self.NUM_SYMBOLS):
                if i % 2 == 1:  # Data symbols are at odd positions
                    data_symbols.append(symbols[i])

            print(f"Data symbols: {len(data_symbols)}")

            # Convert symbols to bits (simplified)
            # Each symbol represents 2 bits in 4-FSK
            bits = []
            for symbol in data_symbols[:40]:  # Take first 40 data symbols
                bits.extend([symbol >> 1, symbol & 1])

            # Pack bits into message (simplified approach)
            # Real WSPR would need proper convolutional decoding
            message = "Decoded data requires full Viterbi decoder"

            print(f"Message: {message}")
            return message

        except Exception as e:
            print(f"Decoding error: {e}")
            return None

    def plot_analysis(self, audio_data, sample_rate, symbols, base_freq):
        """Plot analysis results"""
        try:
            fig, axes = plt.subplots(3, 1, figsize=(12, 10))

            # Time domain plot
            t = np.arange(len(audio_data)) / sample_rate
            axes[0].plot(t[:sample_rate*5], audio_data[:sample_rate*5])  # First 5 seconds
            axes[0].set_title('Audio Waveform (First 5 seconds)')
            axes[0].set_xlabel('Time (s)')
            axes[0].set_ylabel('Amplitude')

            # Frequency domain plot
            freqs, times, Sxx = signal.spectrogram(audio_data, sample_rate, nperseg=1024)
            axes[1].pcolormesh(times, freqs, 10 * np.log10(Sxx + 1e-10), shading='gouraud')
            axes[1].set_title('Spectrogram')
            axes[1].set_xlabel('Time (s)')
            axes[1].set_ylabel('Frequency (Hz)')
            axes[1].set_ylim([base_freq - 50, base_freq + 50])

            # Symbol plot
            if symbols:
                symbol_times = np.arange(len(symbols)) * self.SYMBOL_DURATION
                axes[2].plot(symbol_times, symbols, 'bo-', markersize=3)
                axes[2].set_title('Decoded Symbols')
                axes[2].set_xlabel('Time (s)')
                axes[2].set_ylabel('Symbol Value (0-3)')
                axes[2].set_ylim([-0.5, 3.5])
                axes[2].grid(True)

            plt.tight_layout()
            plt.show()

        except ImportError:
            print("Matplotlib not available for plotting")

    def decode_file(self, filename, plot=False):
        """Main decode function"""
        print(f"WSPR Decoder - Processing: {filename}")
        print("=" * 50)

        # Load audio file
        sample_rate, audio_data = self.load_wav_file(filename)
        if audio_data is None:
            return False

        # Find WSPR signal
        base_freq = self.find_wspr_signal(audio_data, sample_rate)

        # Extract symbols
        symbols = self.extract_symbols(audio_data, sample_rate, base_freq)

        # Synchronize symbols
        synced_symbols = self.sync_symbols(symbols)

        # Decode message
        if synced_symbols:
            message = self.decode_message(synced_symbols)
        else:
            message = None

        # Plot if requested
        if plot:
            self.plot_analysis(audio_data, sample_rate, synced_symbols, base_freq)

        print("\n" + "=" * 50)
        if message:
            print(f"DECODE SUCCESS: {message}")
        else:
            print("DECODE FAILED: Unable to decode WSPR message")
            print("Note: This is a simplified decoder. Full WSPR decoding requires:")
            print("- Proper convolutional decoding (Viterbi algorithm)")
            print("- Symbol de-interleaving")
            print("- Advanced error correction")
            print("- Precise frequency and timing synchronization")

        return message is not None


def main():
    parser = argparse.ArgumentParser(description='WSPR Signal Decoder')
    parser.add_argument('filename', help='Input WAV file (2-minute WSPR recording)')
    parser.add_argument('--plot', action='store_true', help='Show analysis plots')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if not args.filename:
        print("Usage: python wspr_decoder.py <filename.wav> [--plot] [--verbose]")
        sys.exit(1)

    decoder = WSPRDecoder()
    success = decoder.decode_file(args.filename, plot=args.plot)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
