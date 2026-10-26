#!/usr/bin/env python3
"""Classify forum comments with Cloudflare's Clef model and write report.html.

Usage:
    python3 classify.py                 # uses clef-flash (fast, cheap)
    python3 classify.py --model clef    # larger, more accurate model
    python3 classify.py --refresh       # ignore cached results and re-classify

Needs cloud-flare.local.sh (copy of cloud-flare.sh with your real account ID/token)
in the same folder. Python standard library only.
"""
import argparse
import html
import json
import re
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
COMMENTS_FILE = HERE / "comments.json"
CACHE_FILE = HERE / "results.json"
REPORT_FILE = HERE / "report.html"
CREDS_FILE = HERE / "cloud-flare.local.sh"

LABELS = ["acceptable", "toxic", "spam"]

INSTRUCTIONS = (
    "Classify `comment`, a post written by a college student, teaching assistant "
    "or professor on the discussion forum of an online AI course. `thread` is the "
    "forum section it was posted in. Judge only the text of the comment."
)
CRITERIA = {
    "acceptable": (
        "A normal forum post: a question, answer, tip, feedback, thanks, "
        "disagreement or complaint. Criticism of ideas, work, grading or a tool "
        "is acceptable as long as it does not insult or attack a person."
    ),
    "toxic": (
        "Abusive or hostile towards a person or group: insults, name-calling, "
        "mockery, harassment, threats, or discrimination."
    ),
    "spam": (
        "Advertising, promotion, scams, referral or giveaway offers, selling "
        "services or materials, or other unsolicited content unrelated to the course."
    ),
}


def load_creds():
    text = CREDS_FILE.read_text()
    creds = dict(re.findall(r'export (\w+)="([^"]*)"', text))
    return creds["CLOUDFLARE_ACCOUNT_ID"], creds["CLOUDFLARE_API_TOKEN"]


def classify(comment, account, token, model, max_attempts=6):
    payload = {
        "state": {"comment": comment["comment"], "thread": comment["thread"]},
        "questions": {
            "label": {
                "type": "choice",
                "instructions": INSTRUCTIONS,
                "criteria": CRITERIA,
            }
        },
    }
    url = f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/@cf/cloudflare/{model}"
    for attempt in range(max_attempts):
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = json.load(response)
            if not data.get("success"):
                raise RuntimeError(f"API said success=false: {data.get('errors')}")
            ans = data["result"]["answers"]["label"]
            return {
                "label": ans["choice"],
                "confidence": ans["confidence"],
                "probabilities": ans["probabilities"],
            }
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                try:
                    body = e.read().decode("utf-8", "replace")[:500]
                except Exception:
                    body = "(no details)"
                raise SystemExit(
                    "HTTP %d: Cloudflare rejected the request.\nCloudflare says: %s\n"
                    "Check cloud-flare.local.sh (account ID and token)." % (e.code, body)
                )
            if e.code == 429 or e.code >= 500:
                time.sleep(2 ** attempt)  # back off and retry
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Gave up on comment {comment['id']} after {max_attempts} attempts")


def build_html(comments, results, model):
    counts = {l: 0 for l in LABELS}
    rows = []
    for c in comments:
        r = results.get(str(c["id"]))
        if r:
            label, conf = r["label"], r["confidence"]
            probs = ", ".join(f"{k} {v:.2f}" for k, v in r["probabilities"].items())
        else:
            label, conf, probs = "error", -1, "classification failed"
        counts[label] = counts.get(label, 0) + 1
        low = " low" if 0 <= conf < 0.3 else ""
        conf_txt = "-" if conf < 0 else f"{conf:.2f}"
        rows.append(
            f'<tr data-label="{label}" data-id="{c["id"]}" data-conf="{conf}" class="{low.strip()}">'
            f'<td class="num">{c["id"]}</td>'
            f'<td><span class="badge {label}">{label}</span></td>'
            f'<td class="num" title="{html.escape(probs)}">{conf_txt}</td>'
            f'<td>{html.escape(c["comment"])}'
            f'<div class="meta">{html.escape(c["author"])} &middot; {html.escape(c["thread"])} '
            f'&middot; {html.escape(c["posted_at"])}</div></td></tr>'
        )
    summary = " &nbsp;|&nbsp; ".join(f"{k}: <b>{v}</b>" for k, v in counts.items() if v)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Clef classification report</title>
<style>
  :root {{ --bg:#fff; --fg:#1b1f24; --line:#d8dee4; --muted:#667085; --lowbg:#fffbe6; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg:#14171a; --fg:#e6e8eb; --line:#30363d; --muted:#9aa4af; --lowbg:#2d2a14; }}
  }}
  body {{ font-family: system-ui, sans-serif; background:var(--bg); color:var(--fg); margin:0; padding:20px; }}
  h1 {{ font-size:1.3rem; margin:0 0 4px; }}
  .sub {{ color:var(--muted); margin-bottom:14px; font-size:.9rem; }}
  .bar {{ display:flex; gap:8px; flex-wrap:wrap; margin-bottom:14px; }}
  button {{ border:1px solid var(--line); background:transparent; color:var(--fg); padding:6px 12px;
           border-radius:6px; cursor:pointer; font-size:.9rem; }}
  button.on {{ background:var(--fg); color:var(--bg); }}
  .wrap {{ overflow-x:auto; }}
  table {{ border-collapse:collapse; width:100%; min-width:640px; }}
  th, td {{ border-bottom:1px solid var(--line); padding:8px 10px; text-align:left; vertical-align:top; }}
  td.num {{ white-space:nowrap; font-variant-numeric:tabular-nums; }}
  tr.low {{ background:var(--lowbg); }}
  .meta {{ color:var(--muted); font-size:.8rem; margin-top:3px; }}
  .badge {{ padding:2px 9px; border-radius:99px; font-size:.8rem; font-weight:600; color:#fff; }}
  .acceptable {{ background:#1a7f37; }} .toxic {{ background:#cf222e; }}
  .spam {{ background:#bc4c00; }} .error {{ background:#6e7781; }}
</style></head><body>
<h1>Clef classification report</h1>
<div class="sub">Model: {html.escape(model)} &nbsp;|&nbsp; {len(comments)} comments &nbsp;|&nbsp; {summary}<br>
Highlighted rows have low confidence (&lt; 0.30): the ones most worth a human look. Hover a confidence value to see the probabilities.</div>
<div class="bar">
  <button class="on" data-filter="all">All</button>
  <button data-filter="acceptable">Acceptable</button>
  <button data-filter="toxic">Toxic</button>
  <button data-filter="spam">Spam</button>
  <button data-filter="low">Low confidence only</button>
  <button id="sort">Sort: by id</button>
</div>
<div class="wrap"><table id="t">
<thead><tr><th>ID</th><th>Label</th><th>Conf.</th><th>Comment</th></tr></thead>
<tbody>
{chr(10).join(rows)}
</tbody></table></div>
<script>
  const tbody = document.querySelector("#t tbody");
  const rows = Array.from(tbody.rows);
  let filter = "all", byConf = false;
  function render() {{
    const sorted = rows.slice().sort((a, b) => byConf
      ? parseFloat(a.dataset.conf) - parseFloat(b.dataset.conf)
      : parseInt(a.dataset.id) - parseInt(b.dataset.id));
    sorted.forEach(r => {{
      const show = filter === "all" || r.dataset.label === filter ||
                   (filter === "low" && r.classList.contains("low"));
      r.style.display = show ? "" : "none";
      tbody.appendChild(r);
    }});
  }}
  document.querySelectorAll("button[data-filter]").forEach(b => b.onclick = () => {{
    filter = b.dataset.filter;
    document.querySelectorAll("button[data-filter]").forEach(x => x.classList.toggle("on", x === b));
    render();
  }});
  document.getElementById("sort").onclick = e => {{
    byConf = !byConf;
    e.target.textContent = byConf ? "Sort: least confident first" : "Sort: by id";
    render();
  }};
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="clef-flash", help="clef-flash (default) or clef")
    ap.add_argument("--refresh", action="store_true", help="ignore cached results")
    args = ap.parse_args()

    comments = json.loads(COMMENTS_FILE.read_text(encoding="utf-8"))["comments"]
    account, token = load_creds()
    print(
        f"Using file: {CREDS_FILE}\n"
        f"Account ID: {len(account)} chars, ends with ...{account[-4:]}\n"
        f"Token: {len(token)} chars, starts with '{token[:5]}'"
    )

    cache = {}
    if CACHE_FILE.exists() and not args.refresh:
        saved = json.loads(CACHE_FILE.read_text())
        if saved.get("model") == args.model:
            cache = saved["results"]

    todo = [c for c in comments if str(c["id"]) not in cache]
    print(f"{len(comments)} comments, {len(todo)} to classify with {args.model}")

    def work(c):
        try:
            return c["id"], classify(c, account, token, args.model)
        except Exception as e:  # keep going; failed ones show as "error" in the report
            print(f"  comment {c['id']} failed: {e}")
            return c["id"], None

    with ThreadPoolExecutor(max_workers=4) as pool:
        for i, (cid, res) in enumerate(pool.map(work, todo), 1):
            if res:
                cache[str(cid)] = res
            if i % 10 == 0:
                print(f"  {i}/{len(todo)} done")

    CACHE_FILE.write_text(json.dumps({"model": args.model, "results": cache}, indent=1))
    REPORT_FILE.write_text(build_html(comments, cache, args.model), encoding="utf-8")
    print(f"Wrote {REPORT_FILE.name}. Open it in your browser.")
    if len(cache) < len(comments):
        print("Some comments failed. Just run the script again; it only retries the missing ones.")


if __name__ == "__main__":
    main()
