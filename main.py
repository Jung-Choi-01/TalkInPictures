import speech_recognition as sr
import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk
import os

# Initialize recognizer class
r = sr.Recognizer()
source = sr.Microphone()

# Initialize tkinter
root = tk.Tk()
root.title("Display Image")
label = Label(root)
label.pack()

def display_image(image_path):
    image = Image.open(image_path)
    photo = ImageTk.PhotoImage(image)
    label.config(image=photo)
    label.image = photo

images_dir = os.path.join(os.path.dirname(__file__), 'images')
def display_if_exists(word):
    for file_name in os.listdir(images_dir):
        if file_name.startswith(word):
            file_path = os.path.join(images_dir, file_name)
            print("Checking path: " + file_path)
            if os.path.isfile(file_path):
                display_image(file_path)
                break

def callback(recognizer, audio):
    # received audio data, now we'll recognize it using Google Speech Recognition
    text = recognizer.recognize_sphinx(audio)
    print("Speech recognized: " + text)
    
    for word in text.split():
        display_if_exists(word)

# Use the microphone as the source
print("Say something!")
audio = r.listen_in_background(source, callback)
root.mainloop()