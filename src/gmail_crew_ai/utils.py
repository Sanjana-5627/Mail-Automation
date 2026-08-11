import os
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, date

# Directory constants
LOGS_DIR = "logs"
DATA_DIR = "data"
OUTPUT_DIR = "output"

def ensure_directories():
    """Ensure required runtime directories exist."""
    for d in [LOGS_DIR, DATA_DIR, OUTPUT_DIR]:
        os.makedirs(d, exist_ok=True)

def is_dry_run() -> bool:
    """Return True if DRY_RUN mode is enabled (default: True for safety)."""
    val = os.getenv("DRY_RUN", "true").strip().lower()
    return val in ("true", "1", "yes")

def require_approval() -> bool:
    """Return True if human-in-the-loop approval is required for destructive actions."""
    val = os.getenv("REQUIRE_APPROVAL", "true").strip().lower()
    return val in ("true", "1", "yes")

def is_unsubscribe_suggestions_enabled() -> bool:
    """Return True if unsubscribe suggestions are enabled."""
    val = os.getenv("ENABLE_UNSUBSCRIBE_SUGGESTIONS", "false").strip().lower()
    return val in ("true", "1", "yes")

def log_decision(
    email_id: str,
    subject: str,
    sender: str,
    category: str,
    priority: str,
    action: str,
    reasoning: str,
    override_note: Optional[str] = None
) -> Dict[str, Any]:
    """Append an agent decision record to logs/decisions.jsonl."""
    ensure_directories()
    record = {
        "timestamp": datetime.now().isoformat(),
        "email_id": email_id,
        "subject": subject,
        "sender": sender,
        "category": category,
        "priority": priority,
        "action": action,
        "reasoning": reasoning,
        "override_note": override_note
    }
    filepath = os.path.join(LOGS_DIR, "decisions.jsonl")
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record

def get_vip_senders() -> Dict[str, int]:
    """Load stored VIP senders dictionary from data/vip_senders.json."""
    ensure_directories()
    filepath = os.path.join(DATA_DIR, "vip_senders.json")
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def update_vip_senders(sender_counts: Dict[str, int]) -> Dict[str, int]:
    """Save or update VIP sender response counts."""
    ensure_directories()
    filepath = os.path.join(DATA_DIR, "vip_senders.json")
    current = get_vip_senders()
    for sender, count in sender_counts.items():
        current[sender] = current.get(sender, 0) + count
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2, ensure_ascii=False)
    return current

def is_vip_sender(sender: str, threshold: int = 2) -> bool:
    """Check if sender is in the VIP list (replied to >= threshold times)."""
    vips = get_vip_senders()
    sender_clean = sender.lower().strip()
    for vip, count in vips.items():
        if vip.lower().strip() in sender_clean and count >= threshold:
            return True
    return False
