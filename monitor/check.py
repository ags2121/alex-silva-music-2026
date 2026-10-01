"""Nightly check of alexsilvamusic.biz for dead Spotify embeds and dead links.

Runs as an AWS Lambda (see infra.yaml / deploy.sh). Run locally to check without emailing:
    python3 monitor/check.py
"""
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

SITE_URL = os.environ.get("SITE_URL", "https://alexsilvamusic.biz")
# Known-good track; if it fails too, Spotify is having an outage, not us.
CONTROL_TRACK = "4cOdK2wGLETKBW3PvgPWqT"
RETRY_DELAY = 60
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"


def status(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return None  # network error: inconclusive


def spotify_ok(kind, id_):
    url = f"https://open.spotify.com/{kind}/{id_}"
    return status("https://open.spotify.com/oembed?url=" + urllib.parse.quote(url, safe=""))


def targets(html):
    """(label, check-fn) pairs for every Spotify embed and outbound <a> link."""
    out = []
    for kind, id_ in sorted(set(re.findall(r"open\.spotify\.com/embed/(\w+)/(\w+)", html))):
        out.append((f"Spotify {kind} {id_}", lambda k=kind, i=id_: spotify_ok(k, i)))
    for href in sorted(set(re.findall(r'<a\s[^>]*href="(https?://[^"]+)"', html))):
        out.append((href, lambda h=href: status(h)))
    return out


def dead(code):
    # ponytail: only 404/410 count; 403s from bot walls and 5xx outages are not "broken"
    return code in (404, 410)


def find_problems():
    code = status(SITE_URL)
    if code != 200:
        return [f"Site itself returned {code}: {SITE_URL}"]
    req = urllib.request.Request(SITE_URL, headers={"User-Agent": UA})
    html = urllib.request.urlopen(req, timeout=20).read().decode()

    pending = targets(html)
    for attempt in range(3):
        if attempt:
            time.sleep(RETRY_DELAY)
        if spotify_ok("track", CONTROL_TRACK) != 200:
            pending = [t for t in pending if not t[0].startswith("Spotify")]
        pending = [(label, fn) for label, fn in pending if dead(fn())]
        if not pending:
            return []
    return [f"Dead: {label}" for label, _ in pending]


def handler(event=None, context=None):
    problems = find_problems()
    if problems:
        import boto3
        boto3.client("sns").publish(
            TopicArn=os.environ["TOPIC_ARN"],
            Subject="alexsilvamusic.biz: broken embeds/links",
            Message="\n".join(problems) + f"\n\nChecked {SITE_URL}",
        )
    return {"problems": problems}


if __name__ == "__main__":
    sample = '<iframe src="https://open.spotify.com/embed/track/abc123?x"></iframe><a class="x" href="https://e.com/a">'
    assert [label for label, _ in targets(sample)] == ["Spotify track abc123", "https://e.com/a"]
    RETRY_DELAY = 5
    print(find_problems() or "All good.")
