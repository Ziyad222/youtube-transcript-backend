from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess, tempfile, os, openai, shutil

# Ajouter ffmpeg au PATH
ffmpeg_dir = os.path.join(os.getcwd(), "ffmpeg")
os.environ["PATH"] = f"{ffmpeg_dir}:{os.environ['PATH']}"

# Initialisation
app = Flask(__name__)
CORS(app)

@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        data = request.get_json()
        youtube_url = data.get("url")
        if not youtube_url:
            return jsonify({"error": "Missing YouTube URL"}), 400

        print(f"[INFO] URL reçue : {youtube_url}")

        # Vérifie si ffmpeg est trouvé
        ffmpeg_path = shutil.which("ffmpeg")
        print(f"[DEBUG] Chemin ffmpeg : {ffmpeg_path}")
        if not ffmpeg_path:
            return jsonify({"error": "ffmpeg introuvable sur Render"}), 500

        # Créer fichier temporaire pour l’audio
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_audio:
            audio_path = tmp_audio.name

        print(f"[DEBUG] Téléchargement audio vers : {audio_path}")

        # Exécution de yt-dlp
        result = subprocess.run(
            ["yt-dlp", "-x", "--audio-format", "mp3", "-o", audio_path, youtube_url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print(f"[DEBUG] yt-dlp stdout : {result.stdout}")
        print(f"[DEBUG] yt-dlp stderr : {result.stderr}")

        if result.returncode != 0:
            return jsonify({"error": "Téléchargement audio échoué", "details": result.stderr}), 500

        # Transcription avec OpenAI
        with open(audio_path, "rb") as f:
            response = openai.Audio.transcribe("whisper-1", f)

        print(f"[INFO] Transcription réussie")

        os.remove(audio_path)

        return jsonify({
            "text": response["text"],
            "language": response.get("language", "inconnue")
        })

    except Exception as e:
        print(f"[ERROR] Exception capturée : {str(e)}")
        return jsonify({"error": "Erreur interne", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
