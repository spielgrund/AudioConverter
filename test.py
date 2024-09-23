import tkinter as tk
from tkinter import messagebox

def process_input():
    try:
        # Simulate getting user input (e.g., from an Entry widget)
        user_input = entry.get()
        if not user_input.isdigit():  # Check if input is a number
            raise ValueError("Input must be a number!")
        
        number = int(user_input)  # Convert input to an integer
        print(f"You entered: {number}")

    except ValueError as e:
        # Handle the ValueError without crashing the program
        messagebox.showerror("Input Error", str(e))

# Set up the main application window
root = tk.Tk()
root.title("Value Error Example")

# Create an Entry widget for user input
entry = tk.Entry(root)
entry.pack(pady=10)

# Create a Button to process the input
submit_button = tk.Button(root, text="Submit", command=process_input)
submit_button.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()
