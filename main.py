import json
import os
import re
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

URL = (
    "https://billetterie.parisfc.fr/fr/calendrier"
    "?filters%5Bcompetition%5D%5B0%5D=3"
    "&filters%5Bshow_away%5D%5B0%5D=0"
    "&filters%5Bstate%5D%5B0%5D=choice_secondary_market"
)
EMPTY_TEXT = "Aucune séance disponible pour le moment"
STATE_FILE = "state.json"

def main():
    headers = {
        "User-Agent": "ParisFCTicketWatcher/0.1 (personal availability checker)",
        "Accept": "text/html,application/xhtml+xml",
    }
    try:
        response = requests.get(URL, headers=headers, timeout=25, allow_redirects=True)
    except requests.RequestException as exc:
        print(f"ACCESS_ERROR: {exc}")
        raise SystemExit(2)

    print(f"HTTP_STATUS: {response.status_code}")
    print(f"FINAL_URL: {response.url}")
    print(f"CONTENT_TYPE: {response.headers.get('content-type', '')}")

    if response.status_code != 200:
        print("RESULT: ACCESS_BLOCKED_OR_UNAVAILABLE")
        raise SystemExit(2)

    html = response.text
    lower = html.lower()
    if "queue-it" in lower or "queueit" in lower or "please wait" in lower and "queue" in lower:
        print("RESULT: QUEUE_IT_OR_ACCESS_GATE")
        raise SystemExit(2)

    soup = BeautifulSoup(html, "html.parser")
    page_text = " ".join(soup.stripped_strings)

    if EMPTY_TEXT.lower() in page_text.lower():
        events = []
        print("RESULT: EXPLICITLY_EMPTY")
    else:
        # Candidate links are extracted only for inspection. Their presence is
        # not treated as proof of a resale listing until the markup is validated.
        events = []
        seen = set()
        for a in soup.select('a.matchCardActionLink--secondary, a[href]'):
            href = a.get("href", "")
            label = " ".join(a.stripped_strings)
            if not href:
                continue
            full_url = urljoin(URL, href)
            key = (full_url, label)
            if key in seen:
                continue
            seen.add(key)
            if "match" in href.lower() or "session" in href.lower() or "event" in href.lower() or "match" in label.lower():
                events.append({"label": label, "url": full_url})

        print("RESULT: PAGE_LOADED_BUT_MARKUP_NEEDS_VALIDATION")
        print(f"CANDIDATE_LINKS: {len(events)}")

    print("PAGE_TITLE:", soup.title.get_text(" ", strip=True) if soup.title else "(none)")
    print("TEXT_PREVIEW:", page_text[:700])

    # Save diagnostic output for the first run; this does not claim a match
    # is available and deliberately does not notify on unvalidated markup.
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "url": response.url,
        "http_status": response.status_code,
        "result": "EXPLICITLY_EMPTY" if EMPTY_TEXT.lower() in page_text.lower() else "NEEDS_MARKUP_VALIDATION",
        "candidate_links": events,
    }
    with open("diagnostic.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
