import struct

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