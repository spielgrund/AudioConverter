import convert_with_loop
import read_loop_points
import write_loop_points
import read_midi_unity_note
import os

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

    