import wave
import struct

def add_loop_points_to_wav(wav_file_path, output_wav_file, loop_start, loop_end):
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
        smpl_chunk += struct.pack('<L', 60)  # MIDI unity note
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

