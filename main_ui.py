import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES  # pip install tkinterdnd2
from tkinter import messagebox
import os
import functions
import re

#pyinstaller --onefile --add-data "C:\Users\timme\AppData\Local\Programs\Python\Python312\Lib\site-packages\tkinterdnd2\tkdnd\win-x64;tkinterDnD2" "main_ui.py"
# pyinstaller.exe --collect-all TkinterDnD2 --windowed main_ui.py
# pyinstaller -F -w main_ui.py --additional-hooks-dir=.


# Function to process a wav file (placeholder function)
def process_wav(file_path, sample_rate, text_field_prestr):
    functions.convert(file_path, sample_rate, text_field_prestr)

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
            
        else:
            print("Please drop a WAV file or a folder containing WAV files.")

def debug_and_drop(event, text_field_rate, text_field_prestr):
    #check if Khz is number and Between 1-192000 and if prestring contains illegal symbols
    if text_field_rate.get().isnumeric() and (1 <= int(text_field_rate.get()) <= 192000):
        text_field_prestr = re.sub('[^\\w_.)( -]', '', text_field_prestr.get())

        try:
            on_drop(event, int(text_field_rate.get()), text_field_prestr)
        except ValueError as e:
             # Handle the ValueError without crashing the program
            messagebox.showerror("Input Error", str(e))
    else:
        print("Please insert Number between 1 - 192000")


# Set up the main GUI application
class DragDropApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title("Drag and Drop WAV Processor")
        self.geometry("400x300")

        # Create a text field with a default value of 24000
        self.label_khz = tk.Label(self, text="Hertz")
        self.label_khz.pack(pady=5)
        self.text_field_rate = tk.Entry(self, width=30)
        self.text_field_rate.pack(pady=10)
        self.text_field_rate.insert(0, 24000)

        self.label_pre_string = tk.Label(self, text="Pre String")
        self.label_pre_string.pack(pady=5)
        self.text_field_prestr = tk.Entry(self, width=30)
        self.text_field_prestr.pack(pady=10)
        self.text_field_prestr.insert(0, "conv_")

        # Checkbutton variables
        self.overwrite_var = tk.BooleanVar()
        self.checkbox_overwrite = tk.Checkbutton(self, text="Overwrite", variable=self.overwrite_var, command=self.toggle_overwrite)
        self.checkbox_overwrite.pack(pady=5)
       
        # Create a label for instruction
        label = tk.Label(self, text="Drag and Drop 8/16 Bit WAV file or folder here.", width=50, height=20, borderwidth=2, relief="groove")
        label.pack(pady=50)

        # Enable drag-and-drop
        self.drop_target_register(DND_FILES)
        # Pass the text_field when binding the <<Drop>> event
        self.dnd_bind('<<Drop>>', lambda event: debug_and_drop(event, self.text_field_rate, self.text_field_prestr))

    def toggle_overwrite(self):
        if self.overwrite_var.get():
            self.text_field_prestr.delete(0, tk.END)
            self.text_field_prestr.insert(0, "")
            self.text_field_prestr.config(state="disabled")
        else:

            self.text_field_prestr.config(state="normal")
            self.text_field_prestr.delete(0, tk.END)
            self.text_field_prestr.insert(0, "conv_")
       

# Start the application
if __name__ == "__main__":
    app = DragDropApp()
    app.mainloop()



