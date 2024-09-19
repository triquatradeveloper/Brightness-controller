import tkinter as tk
from tkinter import ttk
import screen_brightness_control as sbc

# Function to update the brightness
def set_brightness(value):
    try:
        brightness_level = int(float(value))  # Convert value to float and then to int
        sbc.set_brightness(brightness_level)
    except Exception as e:
        print(f"Error setting brightness: {e}")

# Create the main window
root = tk.Tk()
root.title("Brightness Controller")
root.geometry("300x150")
root.configure(bg="black")

# Label for the title
title_label = tk.Label(root, text="Set Brightness", font=("Arial", 14), fg="white", bg="black")
title_label.pack(pady=10)

# Create a scale (scroll bar) to adjust brightness
brightness_scale = ttk.Scale(root, from_=0, to=100, orient="horizontal", length=200, command=set_brightness)
brightness_scale.set(sbc.get_brightness()[0])  # Set initial value based on current brightness
brightness_scale.pack(pady=20)

# Styling the scale
style = ttk.Style()
style.theme_use('clam')
style.configure("TScale", foreground="white", background="black", troughcolor="gray", sliderlength=30, sliderrelief="raised")

# Start the Tkinter event loop
root.mainloop()
