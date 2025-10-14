import re
import pandas as pd
from collections import defaultdict

bias_keywords = {
    "gender": {
        "male": [" he ", " him ", " his ", " man ", " boy ", " male ", " businessman ", " chairman "],
        "female": [" she ", " her ", " woman ", " girl ", " female ", " housewife "],
    },
    "ethnicity": {
        "asian": [" asian ", " indian ", " chinese ", " japanese ", " korean "],
        "african": [" african ", " black ", " nigerian "],
        "western": [" american ", " european ", " british "],
        "middle_eastern": [" arab ", " muslim "],
    },
    "religion": {
        "christian": [" christian ", " jesus ", " church "],
        "muslim": [" muslim ", " islam "],
        "hindu": [" hindu ", " temple "],
        "jewish": [" jewish ", " synagogue "],
    }
}

def count_bias(text):
    t = " " + text.lower() + " "
    result = defaultdict(int)
    for category, groups in bias_keywords.items():
        for subcat, words in groups.items():
            result[f"{category}_{subcat}"] = sum(t.count(w) for w in words)
    return result

def detect_bias_text(text):
    result = count_bias(text)
    total_bias = sum(result.values())
    if total_bias == 0:
        return 0.0, ["none"]
    categories = [k for k, v in result.items() if v > 0]
    bias_score = min(total_bias / 10, 1.0)
    return bias_score, categories
