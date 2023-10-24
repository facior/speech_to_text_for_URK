from flask import Flask, render_template, request, make_response
from pydub import AudioSegment
import openai
import os

app = Flask(__name__)

# Ustaw swój klucz API OpenAI
openai.api_key = "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"

def transcribe_audio(audio_file_path):
    audio = AudioSegment.from_file(audio_file_path)
    segment_length = 2 * 60 * 1000
    segments = [audio[i:i + segment_length] for i in range(0, len(audio), segment_length)]

    transcriptions = []

    for i, segment in enumerate(segments):
        temp_file_path = f"temp_audio_segment_{i}.mp3"
        segment.export(temp_file_path, format="mp3")

        with open(temp_file_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe(
                "whisper-1",
                file=audio_file,
                language_model="pl-PL",
                encoding="utf-8"
            )

            transcriptions.append(transcript['text'])

        os.remove(temp_file_path)

    return transcriptions

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        audio_file = request.files['audio_file']
        if audio_file:
            audio_file.save("uploaded_audio.mp3")
            transcriptions = transcribe_audio("uploaded_audio.mp3")
            with open("transcriptions.txt", "w", encoding="utf-8") as output_file:
                for transcription in transcriptions:
                    output_file.write(transcription + '\n')
            response = make_response(open("transcriptions.txt", "r", encoding="utf-8").read())
            response.headers["Content-Disposition"] = "attachment; filename=transkrypcja.txt"
            return response

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
