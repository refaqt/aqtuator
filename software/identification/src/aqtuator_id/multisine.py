import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, ifft
from scipy.optimize import minimize
import time
import math


# Keep in sync with Controllino firmware: MAX_CSV_SAMPLES in
# src/controllino/main-controllino/main-controllino.ino
MAX_CSV_SAMPLES = 2000


class MultisineOptimizer:
    def __init__(self, fmin_desired, fmax_desired, fs, df_des):
        """
        Initialize the multisine optimizer

        Parameters:
        fmin_desired (float): Minimum desired frequency (Hz)
        fmax_desired (float): Maximum desired frequency (Hz)
        fs (float): Sampling rate (Hz)
        df_des (float): Desired frequency resolution (Hz)
        """
        self.fmin_desired = fmin_desired
        self.fmax_desired = fmax_desired
        self.fs = fs
        self.df_des = df_des
        
        if self.fs <= 0:
            raise ValueError("fs must be > 0")
        if self.fmin_desired <= 0:
            raise ValueError("fmin_desired must be > 0")
        if self.fmax_desired <= 0:
            raise ValueError("fmax_desired must be > 0")
        if self.df_des <= 0:
            raise ValueError("df_des must be > 0")
        if self.fmax_desired <= self.fmin_desired:
            raise ValueError("fmax_desired must be > fmin_desired")
        if self.fmin_desired >= self.fs / 2:
            raise ValueError("fmin_desired must be < fs/2")

        # Choose minimum required length from two constraints:
        # 1) desired frequency resolution: df_actual = fs/N <= df_des
        # 2) lowest tone representable on FFT grid: fs/N <= fmin_desired
        n_from_df = int(math.ceil(self.fs / self.df_des))
        n_from_fmin = int(math.ceil(self.fs / self.fmin_desired))
        n_required = max(n_from_df, n_from_fmin)

        self.length_capped = False
        self.N_required = n_required
        self.N = int(n_required)
        if self.N > MAX_CSV_SAMPLES:
            self.N = int(MAX_CSV_SAMPLES)
            self.length_capped = True

        # Actual FFT-bin spacing/resolution of the generated signal.
        self.df_actual = self.fs / self.N

        # Determine FFT bin range to excite (integer bins map exactly).
        k_min = max(1, int(math.ceil(self.fmin_desired / self.df_actual)))

        # Exclude Nyquist bin for even N and any bin at/above fs/2.
        k_nyquist_exclusive = self.N // 2
        k_max_by_nyquist = max(0, k_nyquist_exclusive - 1)
        k_max_by_fmax = int(math.floor(self.fmax_desired / self.df_actual))
        k_max = min(k_max_by_fmax, k_max_by_nyquist)

        if k_max < k_min:
            # No valid tones within requested band on this grid.
            self.valid_freq_bins = np.array([], dtype=int)
            self.valid_frequencies = np.array([], dtype=float)
        else:
            self.valid_freq_bins = np.arange(k_min, k_max + 1, dtype=int)
            self.valid_frequencies = self.valid_freq_bins.astype(float) * self.df_actual

        self.K = int(self.valid_freq_bins.size)  # Actual number of usable frequencies

        # Backwards-compatible / diagnostic counts:
        # "requested" tones on the user-specified grid (not necessarily realizable).
        self.K_requested = int(math.floor((self.fmax_desired - self.fmin_desired) / self.df_des) + 1)
        self.K_original = self.K_requested

        # Actual band edges on FFT grid (if any tones exist).
        self.fmin_actual = float(self.valid_frequencies[0]) if self.K > 0 else float("nan")
        self.fmax_actual = float(self.valid_frequencies[-1]) if self.K > 0 else float("nan")
        self.fmin = self.df_actual  # lowest non-DC bin on this grid
        self.fmax = self.fmax_actual if self.K > 0 else self.fmin
        self.df = self.df_actual

    def calculate_crest_factor(self, signal):
        """Calculate the crest factor of a signal"""
        rms = np.sqrt(np.mean(np.abs(signal) ** 2))
        peak = np.max(np.abs(signal))
        return peak / rms

    def schroeder_phases(self):
        """
        Calculate initial phases using Schroeder's method (Eq. 8 in paper)
        φ_k = π*(k-1)²/K
        """
        k = np.arange(1, self.K + 1)
        phases = np.pi * (k - 1) ** 2 / self.K
        return phases

    def generate_multisine(self, phases, amplitudes=None):
        """
        Generate multisine signal from phases and amplitudes

        Parameters:
        phases: Phase values for each frequency component (length K)
        amplitudes: Amplitude values (default: flat spectrum with unit amplitude)
        """
        if amplitudes is None:
            amplitudes = np.ones(self.K)

        # Create frequency domain representation
        C = np.zeros(self.N, dtype=complex)
        for k in range(self.K):
            # Use the pre-computed FFT bin index
            freq_index = int(self.valid_freq_bins[k])
            C[freq_index] = amplitudes[k] * np.exp(1j * phases[k])

        # Generate time domain signal using IFFT
        x = self.N * ifft(C)
        return np.real(x)

    def yang_swapping_method(self, phases, amplitudes=None, max_iterations=100,
                             tolerance=1e-6, b1=10, b2=10000):
        """
        Yang's time-frequency domain swapping algorithm (Algorithm 1 in paper)
        with logarithmic threshold adaptation
        """
        if amplitudes is None:
            amplitudes = np.ones(self.K)

        best_cf = float('inf')
        best_phases = phases.copy()

        current_phases = phases.copy()

        for iteration in range(max_iterations):
            # Generate time domain signal
            x = self.generate_multisine(current_phases, amplitudes)

            # Calculate current CF
            current_cf = self.calculate_crest_factor(x)

            if current_cf < best_cf:
                best_cf = current_cf
                best_phases = current_phases.copy()

            # Calculate adaptive threshold (Eq. 12 in paper)
            a_L = np.log10(iteration + b1) / np.log10(b2)
            a_L = np.clip(a_L, 0.75, 0.95)  # Keep within recommended range

            # Apply amplitude clipping
            threshold = a_L * np.max(np.abs(x))
            x_clipped = np.where(np.abs(x) > threshold,
                                 threshold * np.sign(x),
                                 x)

            # Transform back to frequency domain
            X_clipped = fft(x_clipped) / self.N

            # Extract new phases only for valid frequency bins
            new_phases = np.angle(X_clipped[self.valid_freq_bins])

            # Check convergence
            phase_change = np.mean(np.abs(new_phases - current_phases))
            if phase_change < tolerance:
                break

            current_phases = new_phases

        return best_phases, best_cf

    def guillaume_optimization(self, initial_phases, amplitudes=None,
                               p_values=[4, 8, 16, 32, 64, 128]):
        """
        Guillaume's optimization method using p-norm minimization
        """
        if amplitudes is None:
            amplitudes = np.ones(self.K)

        current_phases = initial_phases.copy()

        for p in p_values:
            # Define objective function (p-norm of time domain signal)
            def objective(phases):
                x = self.generate_multisine(phases, amplitudes)
                return np.sum(np.abs(x) ** p) ** (1 / p)

            # Optimize phases
            result = minimize(objective, current_phases,
                              method='L-BFGS-B',
                              options={'maxiter': 100})

            current_phases = result.x

        return current_phases, self.calculate_crest_factor(
            self.generate_multisine(current_phases, amplitudes))

    def optimize_multisine(self, amplitudes=None):
        """
        Main optimization routine using Yang's method

        Parameters:
        amplitudes: Amplitude spectrum (default: flat spectrum)
        """
        if amplitudes is None:
            amplitudes = np.ones(self.K)

        # Start with Schroeder phases
        initial_phases = self.schroeder_phases()

        # Apply Yang's optimization method
        phases, cf = self.yang_swapping_method(initial_phases, amplitudes)

        return phases, cf

    def export_multisine(self, filename, phases, amplitudes=None, min_value=-1.0, max_value=1.0):
        """
        Export multisine data to CSV file
        
        Parameters:
        filename (str): Output CSV filename
        phases: Phase values for each frequency component
        amplitudes: Amplitude values (default: flat spectrum with unit amplitude)
        min_value (float): Minimum output value for rescaling (default: 0.0)
        max_value (float): Maximum output value for rescaling (default: 3.3)
        """
        if amplitudes is None:
            amplitudes = np.ones(self.K)

        # Generate time domain signal
        signal = self.generate_multisine(phases, amplitudes)
        
        # Rescale signal to specified range
        signal_min = np.min(signal)
        signal_max = np.max(signal)
        if signal_max > signal_min:
            signal = min_value + (signal - signal_min) / (signal_max - signal_min) * (max_value - min_value)
        else:
            # If signal is constant, set to middle of range
            signal = (min_value + max_value) / 2.0

        # Create time vector in seconds
        time_vector = np.arange(self.N) / self.fs

        # Create metadata header
        cf = self.calculate_crest_factor(signal)
        fmin_actual_str = f"{self.fmin_actual:.6f}" if self.K > 0 else "N/A"
        fmax_actual_str = f"{self.fmax_actual:.6f}" if self.K > 0 else "N/A"
        header_lines = [
            f"# Multisine Signal Data",
            f"# fmin_desired: {self.fmin_desired:.6f} Hz",
            f"# fmax_desired: {self.fmax_desired:.6f} Hz", 
            f"# fmin_grid: {self.fmin:.6f} Hz",
            f"# fmax_grid: {self.fmax:.6f} Hz",
            f"# fmin_actual: {fmin_actual_str} Hz",
            f"# fmax_actual: {fmax_actual_str} Hz",
            f"# fs: {self.fs:.6f} Hz",
            f"# df_des: {self.df_des:.6f} Hz",
            f"# df_actual: {self.df_actual:.6f} Hz",
            f"# N: {self.N}",
            f"# N_required: {self.N_required}",
            f"# length_capped: {int(self.length_capped)}",
            f"# K_requested: {self.K_requested}",
            f"# K_actual: {self.K}",
            f"# Crest Factor: {cf:.6f}",
            f"# Columns: Time_s, Signal"
        ]
        
        # Write header and data to CSV
        with open(filename, 'w') as f:
            for line in header_lines:
                f.write(line + '\n')
            f.write('Time_s,Signal\n')
            for i in range(self.N):
                f.write(f'{time_vector[i]:.10e},{signal[i]:.10e}\n')

        return signal


# Example usage
def main():
    """
    Example usage of the adapted multisine generator
    """
    # Example parameters
    fmin_desired = 20.0  # Hz
    fmax_desired = 800.0  # Hz
    fs = 8000.0  # Hz
    df_des = 4.0  # Hz
    
    print("Multisine Generator Example")
    print("=" * 50)
    print(f"Input parameters:")
    print(f"  fmin_desired: {fmin_desired} Hz")
    print(f"  fmax_desired: {fmax_desired} Hz")
    print(f"  fs: {fs} Hz")
    print(f"  df_des: {df_des} Hz")
    print()
    
    # Create optimizer
    optimizer = MultisineOptimizer(fmin_desired, fmax_desired, fs, df_des)
    
    # Display calculated parameters
    print("Calculated parameters:")
    print(f"  N_required: {optimizer.N_required}")
    print(f"  N: {optimizer.N} {'(CAPPED by Controllino limit)' if optimizer.length_capped else ''}")
    print(f"  df_des: {optimizer.df_des:.6f} Hz")
    print(f"  df_actual: {optimizer.df_actual:.6f} Hz")
    print(f"  fmin_grid: {optimizer.fmin:.6f} Hz")
    print(f"  fmax_grid: {optimizer.fmax:.6f} Hz")
    print(f"  K_requested (desired tones): {optimizer.K_requested}")
    print(f"  K_actual (usable tones): {optimizer.K}")
    if optimizer.K > 0:
        print(f"  Frequencies: {optimizer.fmin_actual:.3f} to {optimizer.fmax_actual:.3f} Hz")
    else:
        print(f"  Frequencies: No valid frequencies found")
    if optimizer.K_requested != optimizer.K:
        print(f"  Note: Requested {optimizer.K_requested} tones; generated {optimizer.K} tones on FFT grid")
    print()

    # Quick sanity checks (non-fatal)
    df_from_n = optimizer.fs / optimizer.N
    if abs(optimizer.df_actual - df_from_n) > 1e-12:
        print(f"WARNING: df_actual mismatch: df_actual={optimizer.df_actual} vs fs/N={df_from_n}")
    if optimizer.K > 0:
        freqs_from_bins = optimizer.valid_freq_bins.astype(float) * optimizer.df_actual
        if not np.allclose(freqs_from_bins, optimizer.valid_frequencies, rtol=0.0, atol=1e-12):
            print("WARNING: Frequency/bin mapping mismatch (valid_frequencies != valid_freq_bins*df_actual)")
    print()
    
    # Optimize multisine
    print("Optimizing multisine...")
    start_time = time.time()
    phases, cf = optimizer.optimize_multisine()
    elapsed_time = time.time() - start_time
    
    print(f"Optimization completed in {elapsed_time:.3f} seconds")
    print(f"Final crest factor: {cf:.6f}")
    print()
    
    # Export to CSV
    filename = f"multisine_{optimizer.fmin_desired}-{optimizer.fmax_desired}Hz_fs_{optimizer.fs}Hz_df_{optimizer.df}Hz_N{optimizer.N}.csv"
    signal = optimizer.export_multisine(filename, phases)
    print(f"Multisine exported to {filename}")
    
    # Create a simple visualization
    plt.figure(figsize=(12, 8))
    
    # Time domain plot
    plt.subplot(2, 1, 1)
    time_vector = np.arange(optimizer.N) / optimizer.fs
    
    # Show full signal, but limit to reasonable number of samples for readability
    max_samples = min(optimizer.N, 2000)  # Show max 2000 samples or full signal
    plt.plot(time_vector[:max_samples], signal[:max_samples])
    plt.title(f'Multisine Signal (CF={cf:.4f})')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.grid(True, alpha=0.3)
    
    # Frequency domain plot
    plt.subplot(2, 1, 2)
    freqs = np.fft.fftfreq(optimizer.N, 1/optimizer.fs)
    fft_signal = np.fft.fft(signal)
    plt.plot(freqs[:optimizer.N//2], np.abs(fft_signal[:optimizer.N//2]))
    plt.title('Frequency Spectrum')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.grid(True, alpha=0.3)
    plt.xlim(0, optimizer.fmax * 1.1)
    
    plt.tight_layout()
    plt.savefig('multisine_result.png', dpi=150)
    plt.show()
    
    return {
        'optimizer': optimizer,
        'phases': phases,
        'crest_factor': cf,
        'signal': signal,
        'filename': filename
    }


if __name__ == "__main__":
    results = main()