# app.py
from flask import Flask, request, jsonify
import pandas as pd
from detect_bias import detect_bias_text
from correct_bias import correct_bias
from google import genai

app = Flask(__name__)
RESULTS_CSV = "results.csv"

# Initialize Google Gemini client
client = genai.Client(api_key="AIzaSyC-ns7bQo2NpYV5X8G19MfST4sdXuBuX98")  # replace with your actual API key

def log_to_blockchain(prompt, original, corrected, bias_category, bias_score):
    # Dummy blockchain logger
    return "0xDUMMYTXHASH"

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(force=True)
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "Prompt is required."}), 400

    # 1️⃣ Generate response via Gemini
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Answer concisely but in detail: {prompt}"
        )
        generated_text = response.text.strip()
        # Limit to 4-5 sentences for readability
        sentences = [s.strip() for s in generated_text.split(".") if s.strip()]
        generated_text = ". ".join(sentences[:5]) + "."
    except Exception as e:
        return jsonify({"error": f"Text generation error: {str(e)}"}), 500

    # 2️⃣ Correct bias and get corrections list
    corrected_text, corrections_list = correct_bias(generated_text)

    # 3️⃣ Detect bias on corrected text
    bias_score, bias_category = detect_bias_text(corrected_text)

    # 4️⃣ Save results
    result_row = {
        "prompt": prompt,
        "original": generated_text,
        "corrected": corrected_text,
        "corrections": corrections_list,
        "bias_category": bias_category,
        "bias_score": bias_score,
        "tx_hash": log_to_blockchain(prompt, generated_text, corrected_text, bias_category, bias_score)
    }

    # Save to CSV
    try:
        try:
            df_existing = pd.read_csv(RESULTS_CSV)
            df_existing = pd.concat([df_existing, pd.DataFrame([result_row])], ignore_index=True)
            df_existing.to_csv(RESULTS_CSV, index=False)
        except FileNotFoundError:
            pd.DataFrame([result_row]).to_csv(RESULTS_CSV, index=False)
    except Exception as e:
        return jsonify({"error": f"Error saving results: {str(e)}"}), 500

    return jsonify(result_row)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
