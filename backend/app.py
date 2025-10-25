from store_on_chain import store_on_chain
from flask import Flask, request, jsonify, send_from_directory

import pandas as pd
import os
import sqlite3
from detect_bias import detect_bias_text
from correct_bias import correct_bias
from google import genai
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

RESULTS_CSV = "results.csv"

# Initialize Gemini
client = genai.Client(api_key="AIzaSyC-ns7bQo2NpYV5X8G19MfST4sdXuBuX98")  # replace with your valid key


def log_to_blockchain(prompt, original, corrected, bias_category, bias_score):
    """
    Store record on blockchain using store_on_chain.py
    Returns the transaction hash.
    """
    record = {
        "prompt": prompt,
        "output": corrected,
        "bias_category": ",".join(bias_category) if isinstance(bias_category, list) else bias_category,
        "bias_score_before": bias_score,
        "bias_score_after": 0  # You can update this if you compute corrected score
    }

    tx_hashes = store_on_chain([record])
    return tx_hashes[0] if tx_hashes else None

# Serve the main HTML
@app.route("/")
def home():
    return send_from_directory('../frontend', 'index.html')

# Serve other frontend files (CSS, JS, images)
@app.route("/<path:path>")
def static_files(path):
    return send_from_directory('../frontend', path)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(force=True)
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "Prompt is required."}), 400

    # 1️⃣ Generate text
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Answer concisely but in detail: {prompt}"
        )
        generated_text = response.text.strip()
        sentences = [s.strip() for s in generated_text.split(".") if s.strip()]
        generated_text = ". ".join(sentences[:5]) + "."
    except Exception as e:
        return jsonify({"error": f"Text generation error: {str(e)}"}), 500

    # 2️⃣ Detect bias
    bias_score, bias_categories = detect_bias_text(generated_text)
    if isinstance(bias_categories, str):
        bias_categories = [bias_categories]

    # 3️⃣ Correct bias
    corrected_text, corrections_list = correct_bias(generated_text)

    # ✅ Proper corrections list
    cleaned_corrections = []
    for item in corrections_list:
        if isinstance(item, (list, tuple)) and len(item) == 2:
            old, new = item
            if len(old) > 1 and len(new) > 1:  # ensure words, not letters
                cleaned_corrections.append(f"{old} → {new}")

    # 4️⃣ Prepare JSON result
    result_row = {
        "prompt": prompt,
        "original": generated_text,
        "corrected": corrected_text,
        "corrections": cleaned_corrections,
        "bias_category": bias_categories,
        "bias_score": round(float(bias_score), 2),
        "tx_hash": log_to_blockchain(prompt, generated_text, corrected_text, bias_categories, bias_score),
    }

    # 5️⃣ Save to CSV (optional log)
    try:
        save_row = {
            "prompt": prompt,
            "original": generated_text,
            "corrected": corrected_text,
            "corrections": "; ".join(cleaned_corrections),
            "bias_category": ", ".join(bias_categories),
            "bias_score": round(float(bias_score), 2),
            "tx_hash": result_row["tx_hash"],
        }
        if os.path.exists(RESULTS_CSV):
            df = pd.read_csv(RESULTS_CSV)
            df = pd.concat([df, pd.DataFrame([save_row])], ignore_index=True)
        else:
            df = pd.DataFrame([save_row])
        df.to_csv(RESULTS_CSV, index=False)
    except Exception:
        pass  # ignore log errors silently

    return jsonify(result_row)


@app.route("/history", methods=["GET"])
def get_history():
    """Get all records from database"""
    try:
        conn = sqlite3.connect("records.db")
        c = conn.cursor()
        
        # Get all records, newest first
        c.execute("""
            SELECT record_hash, prompt, output, bias_category, 
                   bias_score_before, bias_score_after, stored_on_chain
            FROM records 
            ORDER BY rowid DESC
            LIMIT 50
        """)
        
        records = c.fetchall()
        conn.close()
        
        # Format for JSON
        history = []
        for record in records:
            history.append({
                "hash": record[0][:16] + "...",  # Shortened hash
                "full_hash": record[0],
                "prompt": record[1],
                "output": record[2],
                "bias_category": record[3],
                "bias_score_before": round(record[4], 2) if record[4] else 0,
                "bias_score_after": round(record[5], 2) if record[5] else 0,
                "on_chain": bool(record[6])
            })
        
        return jsonify({"success": True, "history": history})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/stats", methods=["GET"])
def get_stats():
    """Get statistics about bias detection"""
    try:
        conn = sqlite3.connect("records.db")
        c = conn.cursor()
        
        # Total records
        c.execute("SELECT COUNT(*) FROM records")
        total = c.fetchone()[0]
        
        # Average bias score
        c.execute("SELECT AVG(bias_score_before) FROM records WHERE bias_score_before > 0")
        avg_bias = c.fetchone()[0] or 0
        
        # Records with bias detected
        c.execute("SELECT COUNT(*) FROM records WHERE bias_category != 'none' AND bias_category != ''")
        biased_count = c.fetchone()[0]
        
        # Most common bias categories
        c.execute("""
            SELECT bias_category, COUNT(*) as count 
            FROM records 
            WHERE bias_category != 'none' AND bias_category != ''
            GROUP BY bias_category 
            ORDER BY count DESC 
            LIMIT 5
        """)
        top_biases = [{"category": row[0], "count": row[1]} for row in c.fetchall()]
        
        conn.close()
        
        return jsonify({
            "success": True,
            "stats": {
                "total_records": total,
                "biased_records": biased_count,
                "average_bias_score": round(avg_bias, 2),
                "top_bias_categories": top_biases
            }
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)