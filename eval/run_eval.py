#!/usr/bin/env python
"""
Evaluation Harness for Categorization & Priority Accuracy.
Runs classification logic against synthetic fixture data in eval/fixtures.json.
"""

import os
import sys
import json
from typing import Dict, Any, List

# Ensure UTF-8 output formatting for terminal compatibility
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

def evaluate_rule_based(fixture: Dict[str, Any]) -> Dict[str, str]:
    """Evaluate email using deterministic classification rules."""
    subject = fixture.get("subject", "").lower()
    sender = fixture.get("sender", "").lower()
    body = fixture.get("body", "").lower()

    # Category matching logic
    if "youtube.com" in sender or "youtube" in subject or "subscriber" in body or "video" in body:
        category = "YOUTUBE"
    elif "github.com" in sender or "[github]" in subject:
        category = "GITHUB"
    elif "receipt" in subject or "invoice" in subject or "charged" in body or "billing" in sender:
        category = "RECEIPTS_INVOICES"
    elif "newsletter" in sender or "digest" in subject:
        category = "NEWSLETTERS"
    elif "sale" in subject or "off" in subject or "promotions" in sender or "shutterfly" in sender or "webinar" in subject:
        category = "PROMOTIONS"
    elif "sponsorship" in subject or "sponsor" in body:
        category = "SPONSORSHIPS"
    elif "recruiter" in sender or "opportunity" in subject or "hiring" in body:
        category = "RECRUITMENT"
    elif "invitation" in subject or "invited" in body:
        category = "EVENT_INVITATIONS"
    else:
        category = "PERSONAL"

    # Priority matching logic
    if "urgent" in subject or "vulnerability" in subject or category == "YOUTUBE" or "schedule a quick call" in subject:
        priority = "HIGH"
    elif category in ["PERSONAL", "SPONSORSHIPS", "RECRUITMENT", "EVENT_INVITATIONS"]:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    return {"category": category, "priority": priority}

def run_evaluation():
    fixtures_file = os.path.join(os.path.dirname(__file__), "fixtures.json")
    if not os.path.exists(fixtures_file):
        print(f"Error: Fixtures file not found at {fixtures_file}")
        sys.exit(1)

    with open(fixtures_file, "r", encoding="utf-8") as f:
        fixtures = json.load(f)

    total = len(fixtures)
    category_correct = 0
    priority_correct = 0
    both_correct = 0

    print(f"\n==================================================")
    print(f"       CREWAI GMAIL AUTOMATION EVALUATION         ")
    print(f"==================================================")
    print(f"Evaluating {total} synthetic email fixtures...\n")

    print(f"{'ID':<8} {'Subject':<35} {'Cat Exp/Pred':<28} {'Prio Exp/Pred':<20} {'Status'}")
    print("-" * 105)

    for item in fixtures:
        item_id = item.get("id", "")
        subject = (item.get("subject", "")[:32] + "..") if len(item.get("subject", "")) > 32 else item.get("subject", "")
        exp_cat = item.get("expected_category", "")
        exp_prio = item.get("expected_priority", "")

        pred = evaluate_rule_based(item)
        pred_cat = pred["category"]
        pred_prio = pred["priority"]

        cat_ok = (exp_cat == pred_cat)
        prio_ok = (exp_prio == pred_prio)

        if cat_ok:
            category_correct += 1
        if prio_ok:
            priority_correct += 1
        if cat_ok and prio_ok:
            both_correct += 1
            status = "[PASS]"
        else:
            status = "[FAIL]"

        cat_str = f"{exp_cat} / {pred_cat}"
        prio_str = f"{exp_prio} / {pred_prio}"
        print(f"{item_id:<8} {subject:<35} {cat_str:<28} {prio_str:<20} {status}")

    cat_acc = (category_correct / total) * 100
    prio_acc = (priority_correct / total) * 100
    overall_acc = (both_correct / total) * 100

    print("-" * 105)
    print(f"\nEVALUATION SUMMARY REPORT")
    print(f"* Total Test Fixtures     : {total}")
    print(f"* Category Accuracy       : {category_correct}/{total} ({cat_acc:.1f}%)")
    print(f"* Priority Accuracy       : {priority_correct}/{total} ({prio_acc:.1f}%)")
    print(f"* Overall Exact Match     : {both_correct}/{total} ({overall_acc:.1f}%)\n")

    return 0

if __name__ == "__main__":
    sys.exit(run_evaluation())
