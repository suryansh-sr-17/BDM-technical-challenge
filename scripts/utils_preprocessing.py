import re
import html
from bs4 import BeautifulSoup

def clean_html(text: str) -> str:
    """Remove HTML tags, decode entities, and strip."""
    if not text:
        return ""
    text = html.unescape(text)
    text = BeautifulSoup(text, "lxml").get_text(" ")
    return re.sub(r"\s+", " ", text).strip()

def has_unsubscribe(text: str) -> bool:
    """Detect unsubscribe links in email."""
    return bool(re.search(r"unsubscribe|opt out|opt-out", text, re.I))

def has_postal_address(text: str) -> bool:
    """Detect postal address (simple heuristic)."""
    return bool(re.search(r"\d{1,5}\s+\w+(\s+\w+)*,?\s+[A-Z]{2}\s+\d{5}", text))

def map_can_spam_label(text: str, base_label: str) -> str:
    """
    Weakly label compliance.
    - base_label: "ham" or "spam"
    - ham + has unsubscribe + address -> compliant
    - spam or missing signals -> violation
    """
    if base_label == "spam":
        return "CANSPAM_VIOLATION"
    if base_label == "ham" and has_unsubscribe(text) and has_postal_address(text):
        return "CANSPAM_COMPLIANT"
    return "CANSPAM_VIOLATION"

def map_ccpa_label(category: str) -> str:
    """
    Map OPP-115/Polisis categories to Disclosure / Non-Disclosure.
    """
    disclosure_cats = {
        "first-party collection/use",
        "third-party sharing/collection",
        "user access, edit, delete",
        "user choice/control",
        "data security",
        "data retention",
    }
    return "CCPA_DISCLOSURE" if category in disclosure_cats else "NON_DISCLOSURE"
