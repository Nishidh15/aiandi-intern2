# Notes

## How to run

1. Copy `cloud-flare.sh` to `cloud-flare.local.sh` and fill in your Cloudflare account ID and Workers AI API token. This file is gitignored and is never committed.
2. Load the credentials: `source cloud-flare.local.sh` (Windows PowerShell: set the same variables, or use Git Bash)
3. Install dependencies, if any: `pip install requests`   <!-- [edit: match what your script imports] -->
4. Run the program: `python [YOUR_SCRIPT_NAME].py`
5. Open the generated `report.html` in a browser. It lists all 100 comments with Clef's label and confidence, and has filters for acceptable, toxic, spam and low-confidence rows.

## Tools and models used

- **Classifier:** Cloudflare Workers AI, model Clef (`clef-flash`), to label each comment as acceptable, toxic or spam.
- **Claude (Anthropic):** [edit: say exactly what you used it for, e.g. "to help write the Python script and the HTML report"]. I also used it to turn the report into a plain reading list so I could review the comments faster, and to check the format and wording of `MISTAKES.md`.
- **Judgement in MISTAKES.md:** the labels and reasons are my own. I read all 100 comments myself and made the calls; I did not ask an AI which labels were wrong.

## What I felt about the task

[edit: write 3 to 5 sentences in your own words. Some questions to answer, if they help:
- What was easy and what was harder than expected (setting up Cloudflare, the API, reviewing)?
- Did anything surprise you about the kinds of mistakes Clef made, or how confident it was when it was wrong?
- How long did it take you in total?
- What did you think of the work this role involves, i.e. checking AI output closely?]
