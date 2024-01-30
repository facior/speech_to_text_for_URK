from flask import Flask, render_template, request, make_response, jsonify, Response
from pydub import AudioSegment
import openai
import os
import openai_api_key
from docx import Document

app = Flask(__name__)

openai.api_key = openai_api_key.API_KEY


def transcribe_audio_with_progress(audio_file_path):
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


def generate_transcription(audio_file):
    transcriptions = transcribe_audio_with_progress(audio_file)

    # Create a Word document
    doc = Document()

    for transcription in transcriptions:
        doc.add_paragraph(transcription)

    # Save the document
    doc.save("transcriptions.docx")

    return "transcriptions.docx"


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        audio_file = request.files['audio_file']
        if audio_file:
            audio_file.save("uploaded_audio.mp3")

            def generate():
                result_file = generate_transcription("uploaded_audio.mp3")
                with open(result_file, "rb") as f:
                    while True:
                        chunk = f.read(8192)
                        if not chunk:
                            break
                        yield chunk

            response = Response(generate(), content_type="application/octet-stream")
            response.headers["Content-Disposition"] = "attachment; filename=transkrypcja.docx"

            return response

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)