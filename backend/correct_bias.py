import re

def correct_bias(text: str):
    """
    Enhanced bias correction:
    Uses regex-based neutral replacements for gender, race, and religion
    while preserving capitalization and avoiding false replacements in factual contexts.
    """
    replacements = {
        # Gender
        r"\bman\b": "person",
        r"\bwoman\b": "person",
        r"\bgirl\b": "individual",
        r"\bboy\b": "individual",
        r"\bhousewife\b": "homemaker",
        r"\bchairman\b": "chairperson",
        r"\bbusinessman\b": "entrepreneur",

        # Race / Ethnicity
        r"\bwhite\b": "individual",
        r"\bblack\b": "individual",
        r"\basian\b": "individual",
        r"\bafrican\b": "individual",
        r"\bindian\b": "individual",
        r"\blatino\b": "individual",
        r"\barab\b": "individual",

        # Religion
        r"\bchristian\b": "religious person",
        r"\bmuslim\b": "religious person",
        r"\bhindu\b": "religious person",
        r"\bjew\b": "religious person",
        r"\bbuddhist\b": "religious person",
        r"\bsikh\b": "religious person",
    }

    # Prevent replacement in factual contexts (e.g., Indian food, Hindu festival)
    factual_contexts = [
        r"\bindian cuisine\b",
        r"\bhindu festival\b",
        r"\bmuslim holiday\b",
        r"\bchristian holiday\b"
    ]

    text_lower = text.lower()
    for ctx in factual_contexts:
        if re.search(ctx, text_lower):
            return text  # skip correction if factual context detected

    def preserve_case(match, replacement):
        """Preserve capitalization of original match."""
        word = match.group(0)
        if word.isupper():
            return replacement.upper()
        elif word[0].isupper():
            return replacement.capitalize()
        else:
            return replacement

    corrected_text = text
    for pattern, replacement in replacements.items():
        corrected_text = re.sub(pattern,
                                lambda m: preserve_case(m, replacement),
                                corrected_text,
                                flags=re.IGNORECASE)

    return corrected_text


if __name__ == "__main__":
    sample = "The Chairman, a White businessman, hired a Muslim woman for the project."
    print(correct_bias(sample))
