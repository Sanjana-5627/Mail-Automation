import os
import json
import requests
from typing import Dict, Any, List, Optional

def generate_run_digest(
    total_processed: int,
    archived_count: int,
    deleted_count: int,
    drafts_count: int,
    high_priority_count: int,
    unsubscribe_candidates: Optional[List[str]] = None,
    summary_line: str = "Execution completed successfully."
) -> Dict[str, Any]:
    """Generate and return a structured digest summary dict."""
    digest = {
        "total_processed": total_processed,
        "archived_count": archived_count,
        "deleted_count": deleted_count,
        "drafts_count": drafts_count,
        "high_priority_count": high_priority_count,
        "unsubscribe_candidates": unsubscribe_candidates or [],
        "summary": summary_line
    }

    # Format text for output
    lines = [
        "==================================================",
        "          📧 GMAIL CREWAI RUN DIGEST             ",
        "==================================================",
        f"• Emails Processed      : {total_processed}",
        f"• High Priority Flagged : {high_priority_count}",
        f"• Draft Replies Created : {drafts_count}",
        f"• Emails Archived       : {archived_count}",
        f"• Emails Deleted        : {deleted_count}",
    ]

    if unsubscribe_candidates:
        lines.append(f"• Unsubscribe Candidates: {', '.join(unsubscribe_candidates)}")

    lines.append(f"• Status               : {summary_line}")
    lines.append("==================================================")
    digest_text = "\n".join(lines)

    # Print to console
    print("\n" + digest_text + "\n")

    # Send to Slack if SLACK_WEBHOOK_URL is configured
    slack_url = os.getenv("SLACK_WEBHOOK_URL")
    if slack_url and slack_url.strip() and "hooks.slack.com" in slack_url:
        try:
            payload = {
                "blocks": [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": "📊 Gmail Automation Digest"}
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Processed:* {total_processed} | *High Priority:* {high_priority_count} | *Drafts:* {drafts_count}\n*Archived:* {archived_count} | *Deleted:* {deleted_count}"
                        }
                    }
                ]
            }
            if unsubscribe_candidates:
                payload["blocks"].append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Unsubscribe Suggestions:* {', '.join(unsubscribe_candidates)}"
                    }
                })
            requests.post(slack_url, json=payload, headers={"Content-Type": "application/json"}, timeout=5)
            print("Digest summary posted to Slack successfully.")
        except Exception as e:
            print(f"Note: Could not post digest to Slack: {e}")

    return digest
