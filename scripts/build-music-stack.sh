#!/bin/sh
set -eu
# Keep opt-level=3. Split the monolithic test crate into smaller LLVM units to
# reduce peak memory; the production binary keeps the project's release settings.
cargo test --release --locked --package octo --lib \
  --config profile.release.package.octo.codegen-units=32 \
  services::prefetch::prefetch_service_tests
cargo test --release --locked --package octo --lib \
  --config profile.release.package.octo.codegen-units=32 \
  controllers::subsonic::prefetch_stream_tests
cargo build --release --locked --package octo --bin octo
