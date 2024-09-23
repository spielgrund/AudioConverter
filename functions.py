import wave
import numpy as np
import os
import struct


def convert(input_file, target_rate, text_field_prestr):

    # Look for Loop Points
    loop_points = read_loop_points(input_file)
    loop_start = 0
    loop_end = 0
    midi_unity_note = read_midi_unity_note_from_smpl_chunk(input_file)
    output_file = os.path.dirname(input_file) + os.sep + text_field_prestr + os.path.basename(input_file)

    try:
        # Code that may cause a ValueError
        audio_data, original_rate, n_channels, sample_width = read_wav_data(input_file)
    except ValueError:
        print("24 Bit and 32 Bit are not allowed!")
        raise
        
    


    if loop_points:
        #If Loop Points are found
        for loop in loop_points:
            #print(f"Loop from {loop['start']} to {loop['end']}, loop type: {loop['loop_type']}")
            loop_start = loop['start']
            loop_end = loop['end']
        # Read the original WAV file and loop points
        


        # Resample to target_rate
        resampled_data = resample_audio(audio_data, original_rate, target_rate)

        # Adjust loop points to the new sample rate
        new_loop_start, new_loop_end = adjust_loop_points(loop_start, loop_end, original_rate, target_rate)
        
        # Write the resampled audio and the new loop points to a new WAV file
        write_wav(output_file, resampled_data, target_rate, n_channels, sample_width)

        #print(f"Conversion to {target_rate}hz completed successfully!")

        add_loop_points_to_wav(output_file, output_file, new_loop_start, new_loop_end, midi_unity_note)

    else:
        #print("No loop points found in the WAV file.")
        # Read the original WAV file and loop points
        
        resampled_data = resample_audio(audio_data, original_rate, target_rate)
        
        write_wav(output_file, resampled_data, target_rate, n_channels, sample_width)


def read_loop_points(wav_file_path):
    with open(wav_file_path, 'rb') as f:
        # Read through the RIFF header
        riff_header = f.read(12)
        if riff_header[:4] != b'RIFF' or riff_header[8:12] != b'WAVE':
            raise ValueError("This is not a valid WAVE file.")
        
        # Parse chunks to find the 'smpl' chunk
        while True:
            chunk_header = f.read(8)
            if len(chunk_header) < 8:
                break  # Reached the end of the file
            
            chunk_id, chunk_size = struct.unpack('<4sI', chunk_header)
            if chunk_id == b'smpl':
                # Found the 'smpl' chunk, read it
                smpl_data = f.read(chunk_size)
                
                # The structure of 'smpl' chunk based on spec
                # Read manufacturer, product, sample period, MIDI unity note, pitch fraction, SMPTE format, SMPTE offset
                smpl_fields = struct.unpack('<7I', smpl_data[:28])
                
                # Number of sample loops
                num_sample_loops = struct.unpack('<I', smpl_data[28:32])[0]
                
                # Read sample loop data (each loop is 24 bytes)
                loops = []
                loop_data_start = 36
                for i in range(num_sample_loops):
                    loop_data = smpl_data[loop_data_start + i * 24: loop_data_start + (i + 1) * 24]
                    cue_point_id, loop_type, start, end, fraction, play_count = struct.unpack('<6I', loop_data)
                    loops.append({
                        'cue_point_id': cue_point_id,
                        'loop_type': loop_type,
                        'start': start,
                        'end': end,
                        'fraction': fraction,
                        'play_count': play_count
                    })
                
                return loops
            
            # Skip to the next chunk
            f.seek(chunk_size, 1)
    
    return None


def read_wav_data(file_path):
    #Reads a WAV file, extracts the audio, sample rate
    try:
        with wave.open(file_path, 'rb') as wav_file:
            sample_rate = wav_file.getframerate()
            n_channels = wav_file.getnchannels()
            n_frames = wav_file.getnframes()
            audio_data = wav_file.readframes(n_frames)
    except Exception as e:
        raise ValueError(f"24/32 Bit not supported") #24 support for later
        
    # Convert the byte data to numpy array based on sample width
    sample_width = wav_file.getsampwidth()
    if sample_width == 1:
        dtype = np.uint8  # 8-bit audio
    elif sample_width == 2:
        dtype = np.int16  # 16-bit audio
    elif sample_width == 3:
        raise ValueError(f"24/32 Bit not supported") #24 support for later
    elif sample_width == 4:
        raise ValueError(f"24/32 Bit not supported") #24 support for later
        #dtype = np.int32  # 32-bit audio
    else:
        raise ValueError(f"Unsupported sample width: {sample_width}")

    audio_data = np.frombuffer(audio_data, dtype=dtype)

    return audio_data, sample_rate, n_channels, sample_width


def write_wav(file_path, audio_data, sample_rate, n_channels, sample_width):
    #Writes audio data to a WAV file
    with wave.open(file_path, 'wb') as wav_file:
        wav_file.setnchannels(n_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
        

    

def resample_audio(audio_data, original_rate, target_rate):
    #Resamples the audio data from the original sample rate to the target sample rate.
    duration = len(audio_data) / original_rate
    num_samples = int(duration * target_rate)

    # Resample using linear interpolation
    old_indices = np.arange(len(audio_data))
    new_indices = np.linspace(0, len(audio_data) - 1, num_samples)
    resampled_data = np.interp(new_indices, old_indices, audio_data)

    return resampled_data.astype(audio_data.dtype)

def adjust_loop_points(loop_start, loop_end, original_rate, target_rate):
    #Adjusts the loop points based on the new sample rate.
    adjusted_start = int(loop_start * target_rate / original_rate)
    adjusted_end = int(loop_end * target_rate / original_rate)
    return adjusted_start, adjusted_end



def add_loop_points_to_wav(wav_file_path, output_wav_file, loop_start, loop_end, midi_unity_note):
    # Open the original WAV file
    with wave.open(wav_file_path, 'rb') as wav_in:
        params = wav_in.getparams()
        audio_data = wav_in.readframes(params.nframes)

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


def read_midi_unity_note_from_smpl_chunk(wav_file):
    with open(wav_file, 'rb') as f:
        # Read the RIFF header
        riff_header = f.read(12)  # First 12 bytes: RIFF header
        if riff_header[0:4] != b'RIFF' or riff_header[8:12] != b'WAVE':
            raise ValueError("Not a valid WAV file")

        # Read chunks until we find the 'smpl' chunk
        while True:
            # Read the chunk header (8 bytes: 4-byte chunk ID, 4-byte chunk size)
            chunk_header = f.read(8)
            if len(chunk_header) < 8:
                break  # End of file

            chunk_id, chunk_size = struct.unpack('<4sI', chunk_header)
            
            # If we find the 'smpl' chunk, read its contents
            if chunk_id == b'smpl':
                chunk_data = f.read(chunk_size)
                
                # The MIDI unity note is the fourth 4-byte integer (after manufacturer, product, sample period)
                # It starts at byte offset 12 in the 'smpl' chunk
                midi_unity_note = struct.unpack_from('<I', chunk_data, offset=12)[0]
                
                return midi_unity_note
            else:
                # Skip the chunk if it's not 'smpl'
                f.seek(chunk_size, 1)

    return 60  # 'smpl' chunk not found


