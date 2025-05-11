from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess, tempfile, os, openai

# Ajouter ffmpeg au PATH si besoin
os.environ["PATH"] = os.getcwd() + "/ffmpeg:" + os.environ["PATH"]

app = Flask(__name__)
CORS(app)

@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        data = request.get_json()
        youtube_url = data.get("url")
        if not youtube_url:
            return jsonify({"error": "Missing YouTube URL"}), 400

        print("[INFO] URL reçue :", youtube_url)

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_audio:
            audio_path = tmp_audio.name

        print("[DEBUG] Chemin audio temporaire :", audio_path)

        yt_dlp_command = [
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "--no-playlist",
            "-o", audio_path,
            youtube_url
        ]

        print("[DEBUG] Commande yt-dlp :", " ".join(yt_dlp_command))

        result = subprocess.run(yt_dlp_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            print("[ERROR] yt-dlp stdout :", result.stdout)
            print("[ERROR] yt-dlp stderr :", result.stderr)
            raise Exception(f"yt-dlp a échoué avec le code {result.returncode}")

        with open(audio_path, "rb") as f:
            response = openai.Audio.transcribe("whisper-1", f)

        os.remove(audio_path)

        return jsonify({
            "text": response["text"],
            "language": response.get("language", "inconnue")
        })

    except Exception as e:
        print("[EXCEPTION]", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
