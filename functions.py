import wave
import numpy as np
import os
import struct


def convert(input_file, target_rate, text_field_prestr):

    # Look for Loop Points
    loop_points = read_loop_points.read_loop_points(input_file)
    loop_start = 0
    loop_end = 0
    midi_unity_note = read_midi_unity_note.read_midi_unity_note_from_smpl_chunk(input_file)
    print(midi_unity_note)
    output_file = os.path.dirname(input_file) + os.sep + text_field_prestr + os.path.basename(input_file)
    if loop_points:
        #If Loop Points are found
        for loop in loop_points:
            print(f"Loop from {loop['start']} to {loop['end']}, loop type: {loop['loop_type']}")
            loop_start = loop['start']
            loop_end = loop['end']
        # Read the original WAV file and loop points
        audio_data, original_rate, n_channels, sample_width = convert_with_loop.read_wav_with_loops(input_file)


        # Resample to target_rate
        resampled_data = convert_with_loop.resample_audio(audio_data, original_rate, target_rate)

        # Adjust loop points to the new sample rate
        new_loop_start, new_loop_end = convert_with_loop.adjust_loop_points(loop_start, loop_end, original_rate, target_rate)
        #print(new_loop_start, new_loop_end)
        
        # Write the resampled audio and the new loop points to a new WAV file
        convert_with_loop.write_wav_with_loops(output_file, resampled_data, target_rate, n_channels, sample_width)

        print(f"Conversion to {target_rate}hz completed successfully!")

        write_loop_points.add_loop_points_to_wav(output_file, output_file, new_loop_start, new_loop_end, midi_unity_note)

    else:
        print("No loop points found in the WAV file.")
        # Read the original WAV file and loop points
        audio_data, original_rate, n_channels, sample_width = convert_with_loop.read_wav_with_loops(input_file)
        resampled_data = convert_with_loop.resample_audio(audio_data, original_rate, target_rate)
        
        convert_with_loop.write_wav_with_loops(output_file, resampled_data, target_rate, n_channels, sample_width)


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
        dtype = np.int32  # 32-bit audio
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



def add_loop_points_to_wav(wav_file_path, output_wav_file, loop_start, loop_end, midi_unity_note):
    # Open the original WAV file
    with wave.open(wav_file_path, 'rb') as wav_in:
        params = wav_in.getparams()
        audio_data = wav_in.readframes(params.nframes)
        print(params)

    # Open a new WAV file to write the modified data
    with wave.open(output_wav_file, 'wb') as wav_out:
        wav_out.setparams(params)
        wav_out.writeframes(audio_data)

        # Create 'smpl' chunk for loop points
        smpl_chunk = b'smpl'  # Chunk ID
        smpl_chunk += struct.pack('<L', 60)  # Chunk size (constant for basic smpl chunk)
        smpl_chunk += struct.pack('<L', 0)  # Manufacturer
        smpl_chunk += struct.pack('<L', 0)  # Product
        smpl_chunk += struct.pack('<L', 1000000000)  # Sample Period (in nanoseconds)
        smpl_chunk += struct.pack('<L', midi_unity_note)  # MIDI unity note
        smpl_chunk += struct.pack('<L', 0)  # MIDI pitch fraction
        smpl_chunk += struct.pack('<L', 0)  # SMPTE format
        smpl_chunk += struct.pack('<L', 0)  # SMPTE offset
        smpl_chunk += struct.pack('<L', 1)  # Number of sample loops
        smpl_chunk += struct.pack('<L', 0)  # Sampler data

        # Add the loop point
        smpl_chunk += struct.pack('<L', 0)  # Cue point ID
        smpl_chunk += struct.pack('<L', 0)  # Type (0 = forward loop)
        smpl_chunk += struct.pack('<L', loop_start)  # Start of the loop
        smpl_chunk += struct.pack('<L', loop_end)    # End of the loop
        smpl_chunk += struct.pack('<L', 0)  # Fraction
        smpl_chunk += struct.pack('<L', 0)  # Play count (0 = infinite loop)

        # Write the smpl chunk into the new WAV file
        wav_out._file.write(smpl_chunk)

    print(f"Loop points added to {output_wav_file}")


