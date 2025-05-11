from flask import Flask, request, jsonify
import subprocess, tempfile, os, openai

app = Flask(__name__)

@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        data = request.get_json()
        youtube_url = data.get("url")
        if not youtube_url:
            return jsonify({"error": "Missing YouTube URL"}), 400

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_audio:
            audio_path = tmp_audio.name

        subprocess.run(["yt-dlp", "-x", "--audio-format", "mp3", "-o", audio_path, youtube_url], check=True)

        with open(audio_path, "rb") as f:
            response = openai.Audio.transcribe("whisper-1", f)

        os.remove(audio_path)

        return jsonify({
            "text": response["text"],
            "language": response.get("language", "inconnue")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
