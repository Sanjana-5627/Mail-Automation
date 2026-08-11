import os
from typing import List, Dict, Any
from gmail_crew_ai.utils import is_unsubscribe_suggestions_enabled

def find_unsubscribe_candidates(emails: List[Dict[str, Any]]) -> List[str]:
    """
    Detect List-Unsubscribe header for newsletters/promotions and suggest candidates to unsubscribe.
    Returns list of candidate sender strings.
    """
    if not is_unsubscribe_suggestions_enabled():
        return []

    candidates = []
    for email_data in emails:
        category = str(email_data.get("category", "")).upper()
        thread_info = email_data.get("thread_info") or {}
        unsub_header = thread_info.get("list_unsubscribe") or ""

        if category in ["NEWSLETTERS", "PROMOTIONS"] or unsub_header:
            sender = email_data.get("sender", "Unknown Sender")
            if sender not in candidates:
                candidates.append(sender)

    return candidates
