from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess, tempfile, os, openai

# Ajoute ffmpeg dans le PATH (utile pour yt-dlp)
os.environ["PATH"] = os.getcwd() + "/ffmpeg:" + os.environ.get("PATH", "")

app = Flask(__name__)

# CORS autorisé pour toutes les origines
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        data = request.get_json()
        youtube_url = data.get("url")

        if not youtube_url:
            return jsonify({"error": "Missing YouTube URL"}), 400

        # Téléchargement audio
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_audio:
            audio_path = tmp_audio.name

        # Télécharger l'audio en mp3 avec yt-dlp
        subprocess.run(
            ["yt-dlp", "-x", "--audio-format", "mp3", "-o", audio_path, youtube_url],
            check=True
        )

        # Transcription via OpenAI Whisper
        with open(audio_path, "rb") as f:
            response = openai.Audio.transcribe("whisper-1", f)

        # Nettoyage
        os.remove(audio_path)

        return jsonify({
            "text": response["text"],
            "language": response.get("language", "inconnue")
        })

    except subprocess.CalledProcessError as e:
        print("Erreur yt-dlp :", e)
        return jsonify({"error": "Téléchargement audio échoué", "details": str(e)}), 500

    except Exception as e:
        print("Erreur backend :", e)
        return jsonify({"error": "Erreur serveur", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
