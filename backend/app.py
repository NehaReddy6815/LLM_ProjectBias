# app.py
from flask import Flask, request, jsonify
import pandas as pd
from detect_bias import detect_bias_text
from correct_bias import correct_bias
from transformers import pipeline

app = Flask(__name__)
RESULTS_CSV = "results.csv"

# Initialize Hugging Face model
generator = pipeline("text-generation", model="distilgpt2")

def log_to_blockchain(prompt, original, corrected, bias_category, bias_score):
    return "0xDUMMYTXHASH"

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(force=True)
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "Prompt is required."}), 400

    try:
        generated_outputs = generator(
            prompt,
            max_length=100,
            num_return_sequences=1,
            temperature=0.7,
            do_sample=True,
            top_k=50,
            top_p=0.95
        )
        generated_text = generated_outputs[0]['generated_text'].strip()
    except Exception as e:
        return jsonify({"error": f"Text generation error: {str(e)}"}), 500

    # Detect bias (string-based)
    bias_score, bias_category = detect_bias_text(generated_text)

    # Correct bias if detected
    corrected_text = generated_text if bias_score == 0 else correct_bias(generated_text)

    # Save results
    result_row = {
        "prompt": prompt,
        "original": generated_text,
        "corrected": corrected_text,
        "bias_category": bias_category,
        "bias_score": bias_score,
        "tx_hash": log_to_blockchain(prompt, generated_text, corrected_text, bias_category, bias_score)
    }

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
