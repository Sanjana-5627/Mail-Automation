#!/usr/bin/env python
import os
import sys
import json
import warnings

# Fix Windows terminal encoding for emoji output from CrewAI
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
try:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from dotenv import load_dotenv

# Suppress non-critical warnings
warnings.filterwarnings("ignore", message=".*not a Python type.*")
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

from gmail_crew_ai.crew import GmailCrewAi
from gmail_crew_ai.utils import is_dry_run, require_approval, log_decision
from gmail_crew_ai.digest import generate_run_digest
from gmail_crew_ai.unsubscribe import find_unsubscribe_candidates

def run():
    """Run the Gmail Crew AI system with full guardrails and digest reporting."""
    try:
        load_dotenv()
        
        dry_run = is_dry_run()
        needs_approval = require_approval()
        print(f"Mode: {'[DRY-RUN]' if dry_run else '[LIVE-EXECUTION]'}")

        # Human-in-the-loop approval check before execution if configured
        if needs_approval and not dry_run:
            prompt_input = input("REQUIRE_APPROVAL is enabled. Proceed with potential inbox actions? (yes/no) [yes]: ")
            if prompt_input.strip().lower() not in ("yes", "y", ""):
                print("Execution cancelled by user.")
                return 0

        try:
            email_limit_input = input("How many emails would you like to process? (default: 5): ")
            if email_limit_input.strip() == "":
                email_limit = 5
            else:
                email_limit = int(email_limit_input)
                if email_limit <= 0:
                    print("Number must be positive. Using default of 5.")
                    email_limit = 5
        except (ValueError, EOFError):
            print("Using default limit of 5 emails.")
            email_limit = 5
        
        print(f"Processing {email_limit} emails...")
        
        # Kickoff CrewAI workflow
        result = GmailCrewAi().crew().kickoff(inputs={'email_limit': email_limit})
        
        # Process and compile output stats
        fetched_emails = []
        if os.path.exists("output/fetched_emails.json"):
            try:
                with open("output/fetched_emails.json", "r", encoding="utf-8") as f:
                    fetched_emails = json.load(f)
            except Exception:
                pass

        total_processed = len(fetched_emails)
        
        # Log decisions and compile stats
        high_prio_count = 0
        drafts_count = 0
        archived_count = 0
        deleted_count = 0

        for email_item in fetched_emails:
            email_id = email_item.get("email_id", "N/A")
            subject = email_item.get("subject", "No Subject")
            sender = email_item.get("sender", "Unknown")
            cat = email_item.get("category", "PERSONAL")
            prio = email_item.get("priority", "LOW")
            action = email_item.get("required_action", "READ_ONLY")

            if prio == "HIGH":
                high_prio_count += 1
            if action == "REPLY":
                drafts_count += 1
            if cat in ["RECEIPTS_INVOICES"]:
                archived_count += 1
            elif cat in ["PROMOTIONS", "NEWSLETTERS"] and prio == "LOW":
                deleted_count += 1

            # Log decision to logs/decisions.jsonl
            log_decision(
                email_id=email_id,
                subject=subject,
                sender=sender,
                category=cat,
                priority=prio,
                action=action,
                reasoning=f"Categorized as {cat} with {prio} priority based on rules.",
                override_note="VIP Priority Bump" if email_item.get("is_vip") else None
            )

        # Detect unsubscribe candidates
        unsub_candidates = find_unsubscribe_candidates(fetched_emails)

        # Generate and display final run digest
        generate_run_digest(
            total_processed=total_processed,
            archived_count=archived_count,
            deleted_count=deleted_count,
            drafts_count=drafts_count,
            high_priority_count=high_prio_count,
            unsubscribe_candidates=unsub_candidates,
            summary_line="Completed in DRY-RUN mode." if dry_run else "Completed in LIVE mode."
        )

        return 0
    except Exception as e:
        print(f"\nError executing Gmail CrewAI: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run())
