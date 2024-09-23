import wave
import numpy as np


def read_wav_with_loops(file_path):
    """Reads a WAV file, extracts the audio, sample rate, and loop points (if any)."""
    with wave.open(file_path, 'rb') as wav_file:
        sample_rate = wav_file.getframerate()
        n_channels = wav_file.getnchannels()
        n_frames = wav_file.getnframes()
        audio_data = wav_file.readframes(n_frames)
    
    # Convert the byte data to numpy array based on sample width
    sample_width = wav_file.getsampwidth()
    if sample_width == 1:
        dtype = np.uint8  # 8-bit audio
    elif sample_width == 2:
        dtype = np.int16  # 16-bit audio
    elif sample_width == 3:
        raise ValueError(f"Unsupported sample width: {sample_width}") #24 support for later
    elif sample_width == 4:
        raise ValueError(f"Unsupported sample width: {sample_width}") #32 support for later
        #dtype = np.int32  # 32-bit audio
    else:
        raise ValueError(f"Unsupported sample width: {sample_width}")

    audio_data = np.frombuffer(audio_data, dtype=dtype)

    return audio_data, sample_rate, n_channels, sample_width

def write_wav_with_loops(file_path, audio_data, sample_rate, n_channels, sample_width):
    """Writes audio data to a WAV file and includes loop points (if any)."""
    with wave.open(file_path, 'wb') as wav_file:
        wav_file.setnchannels(n_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
        

    

def resample_audio(audio_data, original_rate, target_rate):
    """Resamples the audio data from the original sample rate to the target sample rate."""
    duration = len(audio_data) / original_rate
    num_samples = int(duration * target_rate)

    # Resample using linear interpolation
    old_indices = np.arange(len(audio_data))
    new_indices = np.linspace(0, len(audio_data) - 1, num_samples)
    resampled_data = np.interp(new_indices, old_indices, audio_data)

    return resampled_data.astype(audio_data.dtype)

def adjust_loop_points(loop_start, loop_end, original_rate, target_rate):
    """Adjusts the loop points based on the new sample rate."""
    adjusted_start = int(loop_start * target_rate / original_rate)
    adjusted_end = int(loop_end * target_rate / original_rate)
    return adjusted_start, adjusted_end


