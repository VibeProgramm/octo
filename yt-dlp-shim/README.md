# Recording exclusions

`YTDLP_BLOCKED_VIDEO_IDS` is an optional comma-separated set of YouTube video IDs.
It excludes specific unwanted recordings, such as a clean edit, a wrong song or a
broken upload, while leaving other recordings and the rest of the source available.

Exclusions apply to ranked search, metadata (including previously cached results),
YouTube Music result lists and direct playback/download/facts requests. A direct
request for an excluded recording returns HTTP 410 before contacting the provider.

Restart the shim after changing the variable. A downstream player's already-cached
audio must also be invalidated; the shim cannot replace bytes stored by another app.
This setting does not automatically detect censorship or identify an explicit master.

```sh
python -m pytest -q tests/test_recording_exclusions.py tests/test_search_skip.py tests/test_rank_r2.py tests/test_ytm.py
```
