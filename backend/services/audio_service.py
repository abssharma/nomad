import subprocess
import os
import whisper

class AudioService:
    def transcribe_audio(self, audio_file_path):
        """
        If the audio file is in .webm format, converts it to .mp3 using ffmpeg.
        If the audio file is already .mp3, it uses that directly.
        Then, transcribes the audio using Whisper.
        Returns a dictionary with the transcription text, e.g.:
            {"transcription": "Your transcribed text here"}
        If any step fails, returns {"transcription": ""}.
        """
        # Check the file extension.
        ext = os.path.splitext(audio_file_path)[1].lower()
        if ext == ".webm":
            mp3_file_path = os.path.splitext(audio_file_path)[0] + ".mp3"
            try:
                # Convert .webm to .mp3 using ffmpeg.
                subprocess.run(["ffmpeg", "-y", "-i", audio_file_path, mp3_file_path], check=True)
            except subprocess.CalledProcessError as e:
                print("Audio conversion failed:", e)
                return {"transcription": ""}
        else:
            mp3_file_path = audio_file_path

        # Transcribe the audio using Whisper.
        try:
            model = whisper.load_model("base")
            # Specify language if needed and disable fp16 if necessary.
            result = model.transcribe(mp3_file_path, language="en", fp16=False)
            transcription_text = result.get("text", "").strip()
            print("Whisper transcription result:", transcription_text)
            return {"transcription": transcription_text}
        except Exception as e:
            print("Whisper transcription failed:", e)
            return {"transcription": ""}
