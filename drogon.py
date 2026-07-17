import os
import webbrowser
import speech_recognition as sr
import pyttsx3
from openai import OpenAI

# -----------------------------
# OpenAI Client (uses environment variable)
# -----------------------------
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

# -----------------------------
# Voice Engine
# -----------------------------
engine = pyttsx3.init()
recognizer = sr.Recognizer()

recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8

# -----------------------------
# Speak Function
# -----------------------------
def speak(text):
    print(f"Drogon: {text}")
    engine.say(text)
    engine.runAndWait()

# -----------------------------
# OpenAI Speech Writer
# -----------------------------
def write_speech(topic, country="United States"):
    if not client:
        speak("OpenAI API key not found.")
        return

    prompt = f"""
    Write a 90-second Model UN opening speech.
    Country: {country}
    Topic: {topic}
    Tone: diplomatic, practical, and persuasive.
    Include one realistic proposal.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert MUN speech writer."},
            {"role": "user", "content": prompt}
        ]
    )

    speech = response.choices[0].message.content

    print("\n--- SPEECH ---\n")
    print(speech)

    with open("speech.txt", "w", encoding="utf-8") as f:
        f.write(speech)

    speak("Your speech is ready.")

# -----------------------------
# Command Dictionary
# -----------------------------
commands = {
    "open chrome": lambda: webbrowser.open("https://google.com"),
    "open youtube": lambda: webbrowser.open("https://youtube.com"),
    "open spotify": lambda: webbrowser.open("https://open.spotify.com"),
    "open notepad": lambda: os.system("notepad"),
    "open calculator": lambda: os.system("calc"),
    "open paint": lambda: os.system("mspaint"),
    "open cmd": lambda: os.system("start cmd"),
    "open documents": lambda: os.startfile(os.path.expanduser("~/Documents")),
    "open downloads": lambda: os.startfile(os.path.expanduser("~/Downloads")),
    "open desktop": lambda: os.startfile(os.path.expanduser("~/Desktop")),
    "lock pc": lambda: os.system("rundll32.exe user32.dll,LockWorkStation")
}

# -----------------------------
# Process Commands
# -----------------------------
def process_command(task):
    task = task.lower()

    if task in commands:
        commands[task]()
        speak(f"Executed {task}")

    elif task.startswith("search "):
        query = task.replace("search ", "")
        webbrowser.open(f"https://www.google.com/search?q={query}")
        speak(f"Searching for {query}")

    elif task.startswith("youtube "):
        query = task.replace("youtube ", "")
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        speak(f"Searching YouTube for {query}")

    elif task.startswith("speech "):
        topic = task.replace("speech ", "")
        write_speech(topic)

    elif task == "help":
        print("\nAvailable commands:")
        for cmd in commands:
            print("-", cmd)
        print("- search [query]")
        print("- youtube [query]")
        print("- speech [topic]")
        print("- exit")

    elif task == "exit" or task == "sleep":
        speak("Returning to sleep.")
        return False

    else:
        speak("Unknown command.")

    return True

# -----------------------------
# Choose Mode
# -----------------------------
mode = input("Choose mode (voice/text): ").lower()

# -----------------------------
# TEXT MODE
# -----------------------------
if mode == "text":
    speak("Text mode activated.")
    while True:
        task = input("You: ")
        if not process_command(task):
            break

# -----------------------------
# VOICE MODE
# -----------------------------
else:
    speak("Voice mode activated. Say Hello to wake me up.")

    while True:
        try:
            with sr.Microphone() as source:
                print("Listening for wake word...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=3)

            wake = recognizer.recognize_google(audio, language="en-US").lower()
            print("Heard:", wake)

            if "hello" in wake:
                speak("Drogon awakened. What do you command?")

                with sr.Microphone() as source:
                    print("Listening for command...")
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)

                task = recognizer.recognize_google(audio, language="en-US").lower()
                print("Command:", task)

                process_command(task)

        except sr.UnknownValueError:
            pass
        except Exception as e:
            print("Error:", e)
