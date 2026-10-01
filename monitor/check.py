"""Nightly check of our sites for dead Spotify/YouTube embeds and dead links.

Runs as an AWS Lambda (see infra.yaml / deploy.sh). Run locally to check without emailing:
    python3 monitor/check.py
"""
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

SITE_URLS = os.environ.get("SITE_URLS", "https://alexsilvamusic.biz,https://alejandrotheband.com").split(",")
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


def youtube_ok(id_):
    url = "https://www.youtube.com/watch?v=" + id_
    code = status("https://www.youtube.com/oembed?url=" + urllib.parse.quote(url, safe=""))
    # 400 = no such ID, 401/403 = private or embedding disabled: all unplayable embeds
    return 404 if code in (400, 401, 403) else code


def targets(html, site):
    """(label, check-fn) pairs for every Spotify/YouTube embed, outbound <a> link, and same-site file."""
    out = []
    for id_ in sorted(set(re.findall(r"youtube(?:-nocookie)?\.com/embed/([\w-]{11})", html))):
        out.append((f"YouTube {id_}", lambda i=id_: youtube_ok(i)))
    for kind, id_ in sorted(set(re.findall(r"open\.spotify\.com/embed/(\w+)/(\w+)", html))):
        out.append((f"Spotify {kind} {id_}", lambda k=kind, i=id_: spotify_ok(k, i)))
    for href in sorted(set(re.findall(r'<a\s[^>]*href="(https?://[^"]+)"', html))):
        out.append((href, lambda h=href: status(h)))
    # Relative href/src (images, css, js): no colon means no scheme, so mailto:/data: etc. are skipped
    for ref in sorted(set(re.findall(r'(?:href|src)="([^"#:]+)"', html))):
        url = urllib.parse.urljoin(site + "/", ref)
        out.append((url, lambda u=url: status(u)))
    return out


def dead(code):
    # ponytail: only 404/410 count; 403s from bot walls and 5xx outages are not "broken"
    return code in (404, 410)


def find_problems(site):
    code = status(site)
    if code != 200:
        return [f"Site itself returned {code}: {site}"]
    req = urllib.request.Request(site, headers={"User-Agent": UA})
    html = urllib.request.urlopen(req, timeout=20).read().decode()

    pending = targets(html, site)
    for attempt in range(3):
        if attempt:
            time.sleep(RETRY_DELAY)
        if spotify_ok("track", CONTROL_TRACK) != 200:
            pending = [t for t in pending if not t[0].startswith("Spotify")]
        pending = [(label, fn) for label, fn in pending if dead(fn())]
        if not pending:
            return []
    return [f"Dead on {site}: {label}" for label, _ in pending]


def handler(event=None, context=None):
    problems = [p for site in SITE_URLS for p in find_problems(site)]
    if problems:
        import boto3
        boto3.client("sns").publish(
            TopicArn=os.environ["TOPIC_ARN"],
            Subject="Site check: broken embeds/links",
            Message="\n".join(problems) + "\n\nChecked " + ", ".join(SITE_URLS),
        )
    return {"problems": problems}


if __name__ == "__main__":
    sample = ('<iframe src="https://open.spotify.com/embed/track/abc123?x"></iframe><a class="x" href="https://e.com/a">'
              '<iframe src="https://www.youtube.com/embed/ubxWFNi0-Ow?rel=0">')
    sample += '<img src="images/x.jpg"><a href="mailto:a@b.c">'
    assert [label for label, _ in targets(sample, "https://s.com")] == [
        "YouTube ubxWFNi0-Ow", "Spotify track abc123", "https://e.com/a", "https://s.com/images/x.jpg"]
    assert youtube_ok("ubxWFNi0-Ow") == 200 and dead(youtube_ok("aaaaaaaaaaa"))
    RETRY_DELAY = 5
    for site in SITE_URLS:
        print(site, find_problems(site) or "All good.")
