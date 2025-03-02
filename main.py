# todo: importing python packages
import os
import serial
import time
import webbrowser
import pyttsx3
import noisereduce as nr
import numpy as np
import wolframalpha
import requests
import pyautogui
import wikipedia
import datetime
import speech_recognition as sr
import pywhatkit
from Api_key import wolfram_llm
from Api_key import wolfram_full_result
from Api_key import news
from gpt4all import GPT4All

# Connect to the Arduino (make sure the COM port matches your setup)
arduino = serial.Serial(port='COM6', baudrate=9600, timeout=1)

model_name = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"
model_path = "C:\\Users\\Abhijeet Sharma\\PycharmProjects\\pythonProject\\GPT4ALL\\models"
model = GPT4All(model_path=model_path, model_name=model_name)
client_1 = wolframalpha.Client(wolfram_llm)
client_2 = wolframalpha.Client(wolfram_full_result)

# todo: Initialize the text-to-speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)


# todo: Function to make the assistant speak the given text.
def speak(text):
    engine.say(text)
    engine.runAndWait()


# todo: function to greet user
def greet_user():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good morning")
    elif hour >= 12 and hour < 18:
        speak("Good afternoon")
    else:
        speak("Good evening")
    speak("I am your assistant. How can I help you today?")


# todo: Function to take voice input from the user using the microphone.
def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        speak("listening")
        r.adjust_for_ambient_noise(source, duration=1)

        # Capture the audio
        audio = r.listen(source)
        time.sleep(3)
        # Convert audio data to numpy array for noise reduction
        audio_data = np.frombuffer(audio.get_raw_data(), np.int16)

        # Apply noise reduction
        reduced_noise_audio = nr.reduce_noise(y=audio_data, sr=source.SAMPLE_RATE)

        # Convert the noise-reduced audio back to audio data for recognition
        audio = sr.AudioData(reduced_noise_audio.tobytes(), source.SAMPLE_RATE, audio.sample_width)

    try:
        print("Recognizing...")
        speak("Recognizing")
        command = r.recognize_google(audio, language='en-in')
        print(f"You said: {command}\n")
    except Exception as e:
        print("Sorry, I didn't catch that. Please say it again.")
        speak("Sorry, I didn't catch that. Please say it again.")
        return "None"
    return command


# todo: Function to open notepad
def open_notepad():
    speak("Opening Notepad.")
    os.system('notepad')


# todo: function to open google in a web_browser
def open_google():
    print('opening google')
    speak("Opening Google.")
    webbrowser.open("https://www.google.com")


# todo: function to open youtube
def open_youtube():
    print('opening Youtube')
    speak("Opening YouTube.")
    webbrowser.open("https://www.youtube.com")


# todo: function to search on youtube
def search_youtube(query):
    speak(f"searching youtube for {query}.")
    webbrowser.open(f"https://www.youtube.com/search?q={query}")


# todo: function to search on google
def search_google(query):
    speak(f"Searching Google for {query}.")
    webbrowser.open(f"https://www.google.com/search?q={query}")


# todo: function to search on wikipedia for given query
def search_wikipedia(query):
    speak('Searching Wikipedia...')
    results = wikipedia.summary(query, sentences=2)
    print("According to wikipedia:-")
    speak("According to Wikipedia")
    print(results)
    speak(results)


# todo: function to play music on youtube
def play_music_on_youtube(command):
    song = command.replace('play', '')
    print(f"Playing {song} on YouTube...")
    pywhatkit.playonyt(song)  # This will open a YouTube video in the web browser


# todo: function to get breaking news
def get_breaking_news(api_key):
    url = f"https://newsapi.org/v2/top-headlines?country=us&category=general&apiKey={news}"
    response = requests.get(url)
    data = response.json()

    if data['status'] == 'ok':
        # Extract the first 5 breaking news headlines
        articles = data['articles'][:5]
        headlines = [article['title'] for article in articles]
        if headlines:
            for idx, headline in enumerate(headlines, 1):
                engine.say(f"News {idx}: {headline}")
                engine.runAndWait()
        else:
            engine.say("Sorry, I could not fetch the news at the moment.")
            engine.runAndWait()
        return headlines

    else:
        return []


# todo: function to operate some query like (calculation , basic question)
def ask_wolfram(query):
    try:
        # Ask the query to WolframAlpha
        res = client_2.query(query)
        # Get the response from WolframAlpha
        answer = next(res.results).text
        print(f"WolframAlpha Response: {answer}")
        speak(answer)
    except Exception as e:
        print(f"An error occurred: {e}")


def ask_wolfram_1(query):
    try:
        # Ask the query to WolframAlpha
        res = client_1.query(query)
        # Get the response from WolframAlpha
        answer = next(res.results).text
        print(f"WolframAlpha Response: {answer}")
        speak(answer)
    except Exception as e:
        print(f"An error occurred: {e}")


# todo: function to open chatGpt and command Query
def search_chatgpt(query):
    # Open the ChatGPT page in a web browser
    chatgpt_url = "https://chat.openai.com/"
    webbrowser.open(chatgpt_url)

    # Wait for the browser to load (adjust the time based on your connection speed)
    time.sleep(10)  # Give the page time to load

    # Type the query into ChatGPT's input field
    pyautogui.typewrite(query)
    pyautogui.press('enter')


# todo: function to open Gmail
def open_mail():
    print("opening Gmail")
    speak('opening Gmail')
    webbrowser.open('https://mail.google.com')


# todo: function to send command to robot
def send_command(command):
    arduino.write(command.encode())  # Send the command as a byte
    print(f"Sent: {command}")
    time.sleep(2)  # Wait for the command to execute


def gpt4all(query):
    response = model.generate(query)
    print("AI Assistant:- ", response)
    speak(response)
    if not os.path.exists("GPT4ALL"):
        os.mkdir("GPT4ALL")
    # Write the output to the file
    with open(f"GPT4ALL/{''.join(query.strip()[0:])}.txt", "w") as f:
        f.write(response)

# todo: function to process user command
def process_command(command):
    command = command.lower()

    if 'open notepad' in command:
        open_notepad()
    elif 'breaking news' in command:
        headlines = get_breaking_news(news)
        print(headlines)
    elif 'answer' in command:
        query = command.replace('answer', '').strip()
        ask_wolfram(query)
    elif 'answer' in command:
        query = command.replace('answer', '').strip()
        ask_wolfram_1(query)
    elif 'command gpt' in command:
        query = command.replace('command gpt', '').strip()
        search_chatgpt(query)
    elif 'open youtube' in command:
        open_youtube()
    elif 'open google' in command:
        open_google()
    elif 'open gmail' in command:
        open_mail()
    elif 'play' in command:
        play_music_on_youtube(command)
    elif 'search youtube' in command:
        query = command.replace('search youtube', '').strip()
        search_youtube(query)
    elif 'open linkedin' in command:
        print('opening linkedin')
        speak('opening linkedin')
        webbrowser.open('https://www.linkedin.com/in/abhijeet-sharma-26a1a6317/')
    elif 'search google' in command:
        query = command.replace('search google', '').strip()
        search_google(query)
    elif 'wikipedia' in command:
        query = command.replace('wikipedia', '').strip()
        search_wikipedia(query)
    elif "hello" in command:
        send_command('h')  # Send 'hi' command to Arduino
        speak("Hello, nice to meet you!")
    elif 'left' in command:
        send_command('l')  # Send 'move head left' command to Arduino
        speak("moving head left side")
    elif 'right' in command:
        send_command('r')  # send 'move head right' command to Arduino
    elif 'smash' in command:
        send_command('s')
        speak("smashing")
    elif 'confuse' in command or 'confused' in command or 'problem' in command:
        send_command('c')
        speak("i am confusing")
    elif 'left and right' in command or 'right and left' in command:
        send_command('a')
        speak("looking left and right")
    elif 'panch' in command:
        send_command('p')
        speak("punching")
    elif "hands" in command:
        send_command('u')  # Send 'hands up' command to Arduino
        speak("Raising hands.")
    elif 'exit' in command or 'quit' in command or 'bye' in command:
        speak("Goodbye")
        return False
    elif '' in command:
        query = command.strip()
        gpt4all(query)
    else:
        speak("I am sorry, I did not understand that command.")
    return True


# todo: executing the function with loop
if __name__ == "__main__":
    speak('hello')
    send_command('h')
    greet_user()
    while True:
        command = take_command()
        if command == "None":
            continue
        if not process_command(command):
            break
