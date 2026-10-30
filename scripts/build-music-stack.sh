#!/bin/sh
set -eu
# Keep normal release optimization; provide enough memory for the large test crate.
cargo test --release --locked --package octo --lib services::prefetch::prefetch_service_tests
cargo test --release --locked --package octo --lib controllers::subsonic::prefetch_stream_tests
cargo build --release --locked --package octo --bin octo
