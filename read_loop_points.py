import wave
import struct

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
