from bs4 import BeautifulSoup
import re
import requests
import spacy

_NLP = None

def get_nlp():
    global _NLP
    if _NLP is None:
        _NLP = spacy.load("en_core_web_lg")
    return _NLP

def retrieve_html(URL):
    """Pulls HTML from website and returns BeautifulSoup html object
    Input: string
    Returns: string"""
    # To do: streamline this function across whole project
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup

def strip_numbered_list(text: str) -> str:
    """Remove list enumeration (e.g., '1.') from text using spaCy."""
    stripped = text.strip()
    cleaned = re.sub(r"^\s*\d+\s*[\.\)\-:]\s*", "", stripped)
    if cleaned != stripped:
        return cleaned

    nlp = get_nlp()
    parsed_doc = nlp(text)

    parts = [token.pos_ for token in parsed_doc]
    try:
        start_index = parts.index("PUNCT") + 1
        entry = parsed_doc[start_index:].text_with_ws.strip()
    except ValueError:
        entry = stripped

    return entry
