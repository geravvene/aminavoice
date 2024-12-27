from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from gtts import gTTS
import random
from io import BytesIO

# Инициализация приложения
app = FastAPI()

# Хранилище фраз
stored_phrases = []

# Эндпоинт для генерации случайной фразы и озвучки
@app.get("/speak")
def speak():
    if not stored_phrases:
        return "No phrases available. Please submit some phrases first."

    # Выбор случайной фразы
    phrase = random.choice(stored_phrases)

    # Генерация аудиофайла с помощью gTTS
    tts = gTTS(text=phrase, lang='zh-cn')
    audio_fp = BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)

    # Возвращение аудиопотока в ответ
    return StreamingResponse(audio_fp, media_type="audio/mpeg")

# Шаблон для главной страницы
@app.get("/", response_class=HTMLResponse)
def read_root():
    html_content = """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Random Chinese Phrases</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 50px;
            background-color: #f4f4f9;
            color: #333;
        }
        h1 {
            color: #4CAF50;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            margin-top: 20px;
            transition: background-color 0.3s ease;
        }
        button:hover {
            background-color: #45a049;
        }
        button:focus {
            outline: none;
        }
        .play-section {
            display: none;
            margin-top: 30px;
        }
        .play-section p {
            font-size: 18px;
            margin-bottom: 20px;
        }
        .audio-container {
            width: 100%;
            max-width: 500px;
            margin: 0 auto;
            padding: 10px;
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        .audio-container audio {
            width: 100%;
            height: 40px;
            border-radius: 8px;
            display: none; /* Скрываем стандартный плеер */
        }
        .audio-controls {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 10px;
        }
        .audio-controls button {
            background-color: #007BFF;
            color: white;
            padding: 10px;
            border-radius: 50%;
            border: none;
            margin: 0 10px;
            transition: transform 0.3s ease, background-color 0.3s ease;
        }
        .audio-controls button:hover {
            background-color: #0056b3;
            transform: scale(1.1);
        }
        .audio-controls button:focus {
            outline: none;
        }
        .audio-controls i {
            font-size: 18px;
        }
        #input-section {
            margin-top: 40px;
        }
        textarea {
            width: 80%;
            height: 150px;
            margin-top: 20px;
            font-size: 16px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            transition: border-color 0.3s ease;
        }
        textarea:focus {
            border-color: #4CAF50;
            outline: none;
        }
    </style>
</head>
<body>
    <h1>Random Chinese Phrases</h1>
    <div id="input-section">
        <p>Enter your Chinese phrases (one per line) and click submit:</p>
        <form id="phrase-form" method="post" action="/submit" onsubmit="submitPhrases(event)">
            <textarea id="phrases" name="phrases" required></textarea>
            <br>
            <button type="submit">Submit</button>
        </form>
    </div>
    <div id="play-section" class="play-section">
        <p>Click the button below to listen to a random Chinese phrase!</p>
        <div class="audio-container">
            <audio id="audio" controls style="display: none;"></audio>
        </div>
        <br>
        <button onclick="playPhrase()">Play Random Phrase</button>
    </div>

    <script>
        function submitPhrases(event) {
            event.preventDefault();

            const form = document.getElementById('phrase-form');
            const formData = new FormData(form);

            const formParams = new URLSearchParams(formData);

            fetch('/submit', {
                method: 'POST',
                body: formParams,
            }).then(response => {
                if (response.ok) {
                    document.getElementById('input-section').style.display = 'none';
                    document.getElementById('play-section').style.display = 'block';
                }
            });
        }

        function playPhrase() {
            const audio = document.getElementById('audio');
            audio.src = '/speak';
            audio.style.display = 'block';
            audio.play();
        }
    </script>
</body>
</html>

    """
    return html_content

# Эндпоинт для получения фраз от пользователя
@app.post("/submit")
def submit_phrases(phrases: str = Form(...)):
    global stored_phrases
    stored_phrases = [phrase.strip() for phrase in phrases.splitlines() if phrase.strip()]
    return {"message": "Phrases submitted successfully."}

# Запуск сервера (для тестирования)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
