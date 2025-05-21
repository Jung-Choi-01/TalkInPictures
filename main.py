import tkinter as tk
from tkinter import Label
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import queue
import threading
import json
import pyaudio
from vosk import Model, KaldiRecognizer
import nltk
from nltk.stem import WordNetLemmatizer

# Initialize tkinter
root = tk.Tk()
root.title("TalkInPictures")
root.geometry("800x600")
label = Label(root)
label.pack()

# Initialize models
if not os.path.exists(os.path.join(os.path.dirname(__file__), 'nltk_data')):
    messagebox.showerror(
        "Missing Model",
        "Please download the WordNet NLTK model and unpack as 'nltk_data/wordnet' in the root directory."
    )
    root.destroy()
    exit(1)
nltk.data.path.append(os.path.join(os.path.dirname(__file__), 'nltk_data'))
lemmatizer = WordNetLemmatizer()

vosk_model_path = os.path.join(os.path.dirname(__file__), "vosk-model-small-en-us-0.15")
if not os.path.exists(vosk_model_path):
    messagebox.showerror(
        "Missing Model",
        "Please download the Vosk model and unpack as 'vosk-model-small-en-us-0.15' in the root directory."
    )
    root.destroy()
    exit(1)

# Word to image processing functions
images_dir = os.path.join(os.path.dirname(__file__), 'images')
def display_if_exists(word):
    lemma_word = lemmatizer.lemmatize(word.lower())
    for file_name in os.listdir(images_dir):
        file_stem = file_name.split(".")[0].lower()
        if file_stem == lemma_word:
            file_path = os.path.join(images_dir, file_name)
            # print("Checking path: " + file_path)
            if os.path.isfile(file_path):
                display_image(file_path)
                break

def display_image(image_path):
    # Get current window size
    root.update_idletasks()
    win_width = root.winfo_width()
    win_height = root.winfo_height()

    image = Image.open(image_path)
    # Calculate new size while maintaining aspect ratio
    img_width, img_height = image.size
    scale = min(win_width / img_width, win_height / img_height, 1)
    new_size = (int(img_width * scale), int(img_height * scale))
    resized_image = image.resize(new_size, Image.LANCZOS)

    photo = ImageTk.PhotoImage(resized_image)
    label.config(image=photo)
    label.image = photo

# Speech to word processing functions
model = Model(vosk_model_path)
recognizer = KaldiRecognizer(model, 16000)
recognizer.SetWords(True)
q = queue.Queue()

def audio_thread():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()
    # print("Say something!")
    messagebox.showinfo("Ready", "Start speaking!")
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            q.put(result)
        else:
            partial = recognizer.PartialResult()
            q.put(partial)

def process_results():
    try:
        while True:
            result_json = q.get_nowait()
            result = json.loads(result_json)
            # Use 'partial' for interim, 'text' for final
            text = result.get('partial') or result.get('text')
            if text:
                # print("Speech recognized: " + text)
                words = text.split()[::-1]
                for word in words:
                    display_if_exists(word)
                    break
    except queue.Empty:
        pass
    root.after(100, process_results)

threading.Thread(target=audio_thread, daemon=True).start()
root.after(100, process_results)
root.mainloop()