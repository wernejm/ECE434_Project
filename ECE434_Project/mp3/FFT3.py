#!/usr/bin/python3
from __future__ import print_function
from __future__ import division
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy.io import wavfile # get the api
from numpy import abs, append, arange, insert, linspace, log10, round, zeros
import time
import numpy as np
from scipy.ndimage.filters import gaussian_filter1d

# Number of audio samples to read every time frame
samples_per_frame = int(8000/60)
N_ROLLING_HISTORY = 2
# Array containing the rolling audio sample window
y_roll = np.random.rand(N_ROLLING_HISTORY, samples_per_frame) / 1e16
fft_window = np.hamming(int(8000 / 60) * N_ROLLING_HISTORY)
MIN_FREQUENCY = 0
MAX_FREQUENCY = 4000
FPS=60
MIC_RATE=8000
N_FFT_BINS = 513
MIN_VOLUME_THRESHOLD = 1e-7



class ExpFilter:
    """Simple exponential smoothing filter"""
    def __init__(self, val=0.0, alpha_decay=0.5, alpha_rise=0.5):
        """Small rise / decay factors = more smoothing"""
        assert 0.0 < alpha_decay < 1.0, 'Invalid decay smoothing factor'
        assert 0.0 < alpha_rise < 1.0, 'Invalid rise smoothing factor'
        self.alpha_decay = alpha_decay
        self.alpha_rise = alpha_rise
        self.value = val

    def update(self, value):
        if isinstance(self.value, (list, np.ndarray, tuple)):
            alpha = value - self.value
            alpha[alpha > 0.0] = self.alpha_rise
            alpha[alpha <= 0.0] = self.alpha_decay
        else:
            alpha = self.alpha_rise if value > self.value else self.alpha_decay
        self.value = alpha * value + (1.0 - alpha) * self.value
        return self.value


def rfft(data, window=None):
    window = 1.0 if window is None else window(len(data))
    ys = np.abs(np.fft.rfft(data * window))
    xs = np.fft.rfftfreq(len(data), 1.0 / config.MIC_RATE)
    return xs, ys


def fft(data, window=None):
    window = 1.0 if window is None else window(len(data))
    ys = np.fft.fft(data * window)
    xs = np.fft.fftfreq(len(data), 1.0 / config.MIC_RATE)
    return xs, ys


fft_plot_filter = ExpFilter(np.tile(1e-1, N_FFT_BINS),
                         alpha_decay=0.5, alpha_rise=0.99)
mel_gain = ExpFilter(np.tile(1e-1, N_FFT_BINS),
                         alpha_decay=0.01, alpha_rise=0.99)
mel_smoothing = ExpFilter(np.tile(1e-1, N_FFT_BINS),
                         alpha_decay=0.5, alpha_rise=0.99)
volume = ExpFilter(MIN_VOLUME_THRESHOLD,
                       alpha_decay=0.02, alpha_rise=0.02)



def hertz_to_mel(freq):
    """Returns mel-frequency from linear frequency input.
    Parameter
    ---------
    freq : scalar or ndarray
        Frequency value or array in Hz.
    Returns
    -------
    mel : scalar or ndarray
        Mel-frequency value or ndarray in Mel
    """
    return 2595.0 * log10(1 + (freq / 700.0))


def mel_to_hertz(mel):
    """Returns frequency from mel-frequency input.
    Parameter
    ---------
    mel : scalar or ndarray
        Mel-frequency value or ndarray in Mel
    Returns
    -------
    freq : scalar or ndarray
        Frequency value or array in Hz.
    """
    return 700.0 * (10**(mel / 2595.0)) - 700.0






def melfrequencies_mel_filterbank(num_bands, freq_min, freq_max, num_fft_bands):
    """Returns centerfrequencies and band edges for a mel filter bank
    Parameters
    ----------
    num_bands : int
        Number of mel bands.
    freq_min : scalar
        Minimum frequency for the first band.
    freq_max : scalar
        Maximum frequency for the last band.
    num_fft_bands : int
        Number of fft bands.
    Returns
    -------
    center_frequencies_mel : ndarray
    lower_edges_mel : ndarray
    upper_edges_mel : ndarray
    """

    mel_max = hertz_to_mel(freq_max)
    mel_min = hertz_to_mel(freq_min)
    delta_mel = abs(mel_max - mel_min) / (num_bands + 1.0)
    frequencies_mel = mel_min + delta_mel * arange(0, num_bands + 2)
    lower_edges_mel = frequencies_mel[:-2]
    upper_edges_mel = frequencies_mel[2:]
    center_frequencies_mel = frequencies_mel[1:-1]
    return center_frequencies_mel, lower_edges_mel, upper_edges_mel




def compute_melmat(num_mel_bands=11, freq_min=0, freq_max=4000,
                   num_fft_bands=513, sample_rate=8000):
    """Returns tranformation matrix for mel spectrum.
    Parameters
    ----------
    num_mel_bands : int
        Number of mel bands. Number of rows in melmat.
        Default: 24
    freq_min : scalar
        Minimum frequency for the first band.
        Default: 64
    freq_max : scalar
        Maximum frequency for the last band.
        Default: 8000
    num_fft_bands : int
        Number of fft-frequenc bands. This ist NFFT/2+1 !
        number of columns in melmat.
        Default: 513   (this means NFFT=1024)
    sample_rate : scalar
        Sample rate for the signals that will be used.
        Default: 44100
    Returns
    -------
    melmat : ndarray
        Transformation matrix for the mel spectrum.
        Use this with fft spectra of num_fft_bands_bands length
        and multiply the spectrum with the melmat
        this will tranform your fft-spectrum
        to a mel-spectrum.
    frequencies : tuple (ndarray <num_mel_bands>, ndarray <num_fft_bands>)
        Center frequencies of the mel bands, center frequencies of fft spectrum.
    """
    center_frequencies_mel, lower_edges_mel, upper_edges_mel =  \
        melfrequencies_mel_filterbank(
            num_mel_bands,
            freq_min,
            freq_max,
            num_fft_bands
        )

    center_frequencies_hz = mel_to_hertz(center_frequencies_mel)
    lower_edges_hz = mel_to_hertz(lower_edges_mel)
    upper_edges_hz = mel_to_hertz(upper_edges_mel)
    freqs = linspace(0.0, sample_rate / 2.0, num_fft_bands)
    melmat = zeros((num_mel_bands, num_fft_bands))

    for imelband, (center, lower, upper) in enumerate(zip(
            center_frequencies_hz, lower_edges_hz, upper_edges_hz)):

        left_slope = (freqs >= lower) == (freqs <= center)
        melmat[imelband, left_slope] = (
            (freqs[left_slope] - lower) / (center - lower)
        )

        right_slope = (freqs >= center) == (freqs <= upper)
        melmat[imelband, right_slope] = (
            (upper - freqs[right_slope]) / (upper - center)
        )

    return melmat, (center_frequencies_mel, freqs)




def create_mel_bank():
    global samples, mel_y, mel_x
    samples = int(MIC_RATE * N_ROLLING_HISTORY / (2.0 * FPS))
    mel_y, (_, mel_x) = compute_melmat(num_mel_bands=N_FFT_BINS,
                                               freq_min=MIN_FREQUENCY,
                                               freq_max=MAX_FREQUENCY,
                                               num_fft_bands=samples,
                                               sample_rate=MIC_RATE)


def microphone_update():
    global y_roll, prev_rms, prev_exp, prev_fps_update
    # Normalize samples between 0 and 1
    fs, data = wavfile.read('output.wav')
    y = data / 2.0**15
    # Construct a rolling window of audio samples
    #y_roll[:-1] = y_roll[1:]
    #y_roll[-1, :] = np.copy(y)
    y_data = np.concatenate(y[0:133], axis=0).astype(np.float32)
    MIN_VOLUME_THRESHOLD = 1e-7
    
    vol = np.max(np.abs(y_data))
    if vol < MIN_VOLUME_THRESHOLD:
        print('No audio input. Volume below threshold. Volume:', vol)
    else:
        # Transform audio input into the frequency domain
        N = len(y_data)
        N_zeros = 2**int(np.ceil(np.log2(N))) - N
        # Pad with zeros until the next power of two
        print(y_data)
        print(fft_window)
        y_data *= fft_window
        y_padded = np.pad(y_data, (0, N_zeros), mode='constant')
        YS = np.abs(np.fft.rfft(y_padded)[:N // 2])
        print(YS)
        # Construct a Mel filterbank from the FFT data
        mel = np.atleast_2d(YS).T * mel_y.T
        # Scale data to values more suitable for visualization
        # mel = np.sum(mel, axis=0)
        mel = np.sum(mel, axis=0)
        mel = mel**2.0
        # Gain normalization
        mel_gain.update(np.max(gaussian_filter1d(mel, sigma=1.0)))
        mel /= mel_gain.value
        mel = mel_smoothing.update(mel)
        # Map filterbank output onto LED strip

create_mel_bank()   
microphone_update()
