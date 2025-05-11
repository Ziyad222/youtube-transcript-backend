from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess, tempfile, os, openai, sys, traceback

# Étendre le PATH pour yt-dlp et ffmpeg
os.environ["PATH"] = os.getcwd() + "/ffmpeg:" + os.environ.get("PATH", "")

app = Flask(__name__)
CORS(app)

@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        data = request.get_json()
        youtube_url = data.get("url")
        print("[INFO] URL reçue :", youtube_url)
        sys.stdout.flush()

        if not youtube_url:
            print("[ERROR] URL manquante")
            sys.stdout.flush()
            return jsonify({"error": "Missing YouTube URL"}), 400

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_audio:
            audio_path = tmp_audio.name

        print("[DEBUG] Chemin audio temporaire :", audio_path)
        sys.stdout.flush()

        # Téléchargement avec yt-dlp
        result = subprocess.run(
            ["yt-dlp", "-x", "--audio-format", "mp3", "-o", audio_path, youtube_url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print("[DEBUG] yt-dlp stdout :", result.stdout)
        print("[DEBUG] yt-dlp stderr :", result.stderr)
        sys.stdout.flush()

        if result.returncode != 0:
            print("[ERROR] yt-dlp a échoué avec le code", result.returncode)
            sys.stdout.flush()
            return jsonify({"error": "Téléchargement audio échoué"}), 500

        # Transcription avec OpenAI Whisper
        with open(audio_path, "rb") as f:
            response = openai.Audio.transcribe("whisper-1", f)

        os.remove(audio_path)

        return jsonify({
            "text": response["text"],
            "language": response.get("language", "inconnue")
        })

    except Exception as e:
        print("[ERROR] Exception capturée :", e)
        traceback.print_exc()
        sys.stdout.flush()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
