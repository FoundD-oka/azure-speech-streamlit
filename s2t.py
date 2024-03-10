# s2t.py
import azure.cognitiveservices.speech as speechsdk
import datetime
import os


# この設定は適宜変更してください
subscription = "b9bb855236e7463390dcd7c6e14fd2c2"
region = "japaneast"
language = "ja-JP"


speech_config = speechsdk.SpeechConfig(subscription=subscription, region=region, speech_recognition_language=language)
recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

def recognized_callback(evt):
    if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
        new_text = evt.result.text.strip()
        if new_text != "":
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("output.py", "a") as f:
                f.write(f"output.append(('{timestamp}', '{new_text}'))\n")

recognizer.recognized.connect(recognized_callback)

print("音声認識を開始します。何か話してください。")
recognizer.start_continuous_recognition()

try:
    while True:
        if os.path.exists("stop_flag"):
            print("終了フラグが検出されました。音声認識を終了します。")
            recognizer.stop_continuous_recognition()
            os.remove("stop_flag")
            break
except KeyboardInterrupt:
    recognizer.stop_continuous_recognition()
