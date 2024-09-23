import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES  # pip install tkinterdnd2
import os
import convert

#sample_rate = 0



# Function to process a wav file (placeholder function)
def process_wav(file_path, sample_rate, text_field_prestr):
    convert.convert(file_path, sample_rate, text_field_prestr)


# Handle drag-and-drop event
def on_drop(event, sample_rate, text_field_prestr):
    
    dropped_path_list = app.splitlist(event.data)
    

    # Get the path without the curly braces
    #sample_rate = text_field.get()
    for _ in dropped_path_list:
        if os.path.isdir(_):
            
           
            # If it's a directory, process all wav files in it
            for root, dirs, files in os.walk(_):
                for file in files:
                    if file.endswith(".wav"):
                        file_path = os.path.join(root, file)
                        process_wav(file_path, sample_rate, text_field_prestr)

    
        elif _.endswith(".wav"):
            # If it's a single WAV file, process it
            process_wav(_, sample_rate, text_field_prestr)
            print(os.path.basename(_))
        else:
            print("Please drop a WAV file or a folder containing WAV files.")

def debug_and_drop(event, text_field_rate, text_field_prestr):    
    if text_field_rate.get().isnumeric():
        on_drop(event, int(text_field_rate.get()), text_field_prestr.get())
    else:
        print("Bitte nur Zahlen eingeben!")

    #print(f"Text field: {text_field.get()}")
    #sample_rate = text_field.get()

    


# Set up the main GUI application
class DragDropApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title("Drag and Drop WAV Processor")
        self.geometry("400x300")

        # Create a text field with a default value of 24000
        self.text_field_rate = tk.Entry(self, width=30)
        self.text_field_rate.pack(pady=10)
        self.text_field_rate.insert(0, 24000)

        self.text_field_prestr = tk.Entry(self, width=30)
        self.text_field_prestr.pack(pady=10)
        self.text_field_prestr.insert(0, "conv_")
        

        # Create a label for instruction
        label = tk.Label(self, text="Drag and Drop WAV file or folder here", width=50, height=10)
        label.pack(pady=50)

        # Enable drag-and-drop
        self.drop_target_register(DND_FILES)
        # Pass the text_field when binding the <<Drop>> event
        self.dnd_bind('<<Drop>>', lambda event: debug_and_drop(event, self.text_field_rate, self.text_field_prestr))

# Start the application
if __name__ == "__main__":
    app = DragDropApp()
    app.mainloop()



