import re

def correct_bias(text: str):
    """
    Enhanced bias correction with pronouns, gender, ethnicity, religion, occupation.
    Returns (corrected_text, corrections_list)
    """
    replacements = {
        # Gender nouns
        r"\bman\b": "person",
        r"\bwoman\b": "person",
        r"\bgirl\b": "individual",
        r"\bboy\b": "individual",
        r"\bhousewife\b": "homemaker",
        r"\bchairman\b": "chairperson",
        r"\bbusinessman\b": "entrepreneur",

        # Gender pronouns
        r"\bhe\b": "they",
        r"\bshe\b": "they",
        r"\bhim\b": "them",
        r"\bher\b": "their",
        r"\bhis\b": "their",
        r"\bhers\b": "theirs",

        # Ethnicity
        r"\bwhite\b": "individual",
        r"\bblack\b": "individual",
        r"\basian\b": "individual",
        r"\bsouth-asian\b": "individual",
        r"\bafrican\b": "individual",
        r"\bafrican-american\b": "individual",
        r"\bindian\b": "individual",
        r"\bcaucasian\b": "individual",
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

    corrections_list = []

    def preserve_case(original, replacement):
        if original.isupper():
            return replacement.upper()
        elif original[0].isupper():
            return replacement.capitalize()
        else:
            return replacement

    corrected_text = text
    for pattern, replacement in replacements.items():
        def repl_func(match):
            orig_word = match.group(0)
            corrected_word = preserve_case(orig_word, replacement)
            if orig_word.lower() != corrected_word.lower():
                corrections_list.append((orig_word, corrected_word))
            return corrected_word

        corrected_text = re.sub(pattern, repl_func, corrected_text, flags=re.IGNORECASE)

    return corrected_text, corrections_list
