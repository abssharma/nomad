import re
import json
import spacy
import requests
import google.generativeai as genai
import os

nlp = spacy.load("en_core_web_sm")

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise Exception("Please set the GOOGLE_API_KEY environment variable.")

genai.configure(api_key=GOOGLE_API_KEY)

USE_GEMINI_API = True

def extract_information(transcription_text):
    if USE_GEMINI_API:
        prompt = (
            "Extract the following information from the transcription text and return a valid JSON object "
            "with the keys: name, age, gender, location, problems, relatives, problems_concerns, misc, extra_info "
            "(which should itself be an object with keys: medical_conditions, possible_relatives, problems_concerns), "
            "and next_steps (possible actions or solutions). Ensure the output is valid JSON and nothing else.\n\n"
            "Transcription: " + transcription_text
        )
        try:
            model = genai.GenerativeModel("models/gemini-1.5-pro")
            chat = model.start_chat(history=[])
            response = chat.send_message(prompt, stream=False)
            result_text = response.text.strip()
            print("Gemini API raw response:", result_text)

            if result_text.startswith("```"):
                lines = result_text.splitlines()
                if lines and lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                result_text = "\n".join(lines).strip()
                print("Cleaned response:", result_text)

            try:
                data = json.loads(result_text)
            except Exception as e:
                print("Initial JSON parsing failed:", e)
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    data = json.loads(result_text[json_start:json_end])
                else:
                    raise e
            if isinstance(data, dict) and "extra_info" in data and "next_steps" in data:
                return data
            else:
                print("Gemini generative response did not include expected keys. Falling back.")
        except Exception as e:
            print("Gemini generative extraction failed:", e)
