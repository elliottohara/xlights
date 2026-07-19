"""Thin client for the xLights REST automation API.

xLights must be running with the automation API enabled (launch attached to the
GUI session: `open -a xLights --args -a -s "<show dir>"`). All commands are
HTTP POSTs to /xlDoAutomation on port 49913. Command reference:
documentation/xlDo Commands.txt in the xLights repo, or
https://github.com/xLightsSequencer/xLights/blob/master/documentation/xlDo%20Commands.txt
"""
import json
import subprocess
import time
import urllib.request

BASE = 'http://127.0.0.1:49913/xlDoAutomation'


def xl(cmd, timeout=600, retries=5, **kwargs):
    """Send one automation command; raise on failure.

    Retries on transient HTTP 503s — the API runs on the UI thread and
    occasionally rejects rapid-fire requests while busy."""
    body = json.dumps({'cmd': cmd, **kwargs}).encode()
    req = urllib.request.Request(BASE, body, {'Content-Type': 'application/json'})
    for attempt in range(retries):
        try:
            resp = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
            break
        except urllib.error.HTTPError as ex:
            if ex.code == 503 and attempt < retries - 1:
                time.sleep(0.2 * (attempt + 1))
                continue
            raise
    if resp.get('res', 200) != 200 or resp.get('worked') == 'false':
        raise RuntimeError(f'{cmd} failed: {resp}')
    return resp


def wait_ready(timeout=600):
    """Wait for the API (xLights blocks on a show-dir backup at startup)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            return xl('getVersion', timeout=5)
        except Exception:
            time.sleep(3)
    raise TimeoutError('xLights automation API did not come up')


def launch(show_dir, timeout=600):
    """Start xLights attached to the user's GUI session and wait for the API."""
    try:
        return wait_ready(timeout=10)
    except TimeoutError:
        pass
    subprocess.run(['open', '-a', 'xLights', '--args', '-a', '-s', show_dir], check=True)
    return wait_ready(timeout)


def new_sequence(media_file, frame_ms=25):
    xl('closeSequence', force='true', quiet='true')
    xl('newSequence', force='true', mediaFile=media_file, frameMS=frame_ms)
    return xl('getOpenSequence')          # includes 'len' in ms


def import_timings(template_xsq):
    """Import timing tracks (and any effects) from another sequence, auto-mapped."""
    xl('importXLightsSequence', filename=template_xsq, mapmethod='auto',
       importmedia='false', timeout=900)


def add_effect(model, layer, effect, settings, palette, start_ms, end_ms):
    xl('addEffect', target=model, effect=effect, settings=settings,
       palette=palette, layer=layer, startTime=int(start_ms), endTime=int(end_ms))


def element_exists(model):
    """True if the element is present in the open sequence (addEffect requires this).
    Note: the sequence master view may exclude some layout groups."""
    try:
        xl('getEffectIDs', model=model, timeout=15)
        return True
    except Exception:
        return False


def save(path=None):
    xl('saveSequence', **({'seq': path} if path else {}), timeout=900)


def render_all():
    xl('renderAll', timeout=3600)


def export_video_preview(path):
    xl('exportVideoPreview', filename=path, timeout=3600)
