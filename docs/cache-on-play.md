# Temporary FLAC on Play

This opt-in extends the existing bounded prefetch cache to the currently played song.
It does not use the permanent acquisition queue or change `DownloadOnPlay` semantics.

```json
{
  "Prefetch": {
    "Enabled": true,
    "Scope": "All",
    "CacheOnPlay": true,
    "OnPlayWaitSeconds": 10
  },
  "Subsonic": {
    "DownloadOnPlay": false,
    "WaitForLosslessOnPlay": false
  }
}
```

- A first-byte Play queues the current external song before upcoming songs.
- The existing download-ahead path accepts FLAC only and writes outside the library.
- Octo clients wait up to `OnPlayWaitSeconds` (0–30) for that cached file. A timeout
  selects the existing preview; it does not cancel the worker's download.
- Range requests keep the source selected for their play. A later play can use FLAC.
- Cache size, disk-space floor, retention, family permissions and scope still apply.
- One serialized cache transfer can establish slskd destination isolation after a
  restart. The real transfer must prove the destination before parallelism is enabled.
  A refused destination or an explicit single-download setting remains respected.

The wait bounds the FLAC attempt, not the time the preview provider takes to answer.
The ordinary explicit-save action remains the way to retain a file in the library.

## Verification

```sh
sh scripts/build-music-stack.sh
```

The tests cover cold-start serial bootstrap, refused destinations, a Play without a
saved queue, cached arrival before the timeout, timeout fallback and source-stable seeks.
`Dockerfile.music-stack` builds the patch on the pinned 2026.10.28 runtime image.
The script retains release optimization and uses 32 codegen units for the large
test crate; the production binary uses the project's default codegen units.
