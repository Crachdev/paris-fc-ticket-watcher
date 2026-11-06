# Paris FC Ticket Watcher

Diagnostic starter for the official Paris FC secondary-market calendar.

## Current scope

- Ligue 1 calendar
- Home matches only
- Secondary market filter
- Daily GitHub Actions run and manual run

## Important limitation

The first version is deliberately diagnostic. It distinguishes an explicit empty-results message from access errors such as Queue-it, and records candidate links. It does **not** yet alert on a match: the exact markup for a real resale listing must first be validated against a page where at least one listing is visible.

It does not bypass Queue-it, authentication, rate limits, or other access controls.

## Run locally

```bash
pip install -r requirements.txt
python main.py
```

## Run on GitHub

The workflow is in `.github/workflows/monitor.yml`. After uploading the files, open **Actions**, select **Paris FC ticket check**, then choose **Run workflow**. The diagnostic JSON is available as a workflow artifact.
