# Using the `rust-musl-builder` as base image, instead of
# the official Rust toolchain.
FROM clux/muslrust:stable AS chef
USER root
RUN cargo install --locked cargo-chef
WORKDIR /app

FROM chef AS planner
COPY . .
RUN cargo chef prepare --recipe-path recipe.json

FROM chef AS builder
ARG APP_BIN=app
ARG TARGETARCH
COPY --from=planner /app/recipe.json recipe.json
RUN case "$TARGETARCH" in \
      amd64) rust_target=x86_64-unknown-linux-musl ;; \
      arm64) rust_target=aarch64-unknown-linux-musl ;; \
      *) echo "Unsupported target architecture: $TARGETARCH" && exit 1 ;; \
    esac && \
    cargo chef cook --release --target "$rust_target" --recipe-path recipe.json
COPY . .
RUN case "$TARGETARCH" in \
      amd64) rust_target=x86_64-unknown-linux-musl ;; \
      arm64) rust_target=aarch64-unknown-linux-musl ;; \
      *) echo "Unsupported target architecture: $TARGETARCH" && exit 1 ;; \
    esac && \
    cargo build --release --target "$rust_target" --bin "$APP_BIN" && \
    cp "target/$rust_target/release/$APP_BIN" /tmp/app

FROM alpine AS runtime
ARG APP_BIN=app
RUN addgroup -S myuser && adduser -S myuser -G myuser
COPY --from=builder /tmp/app /usr/local/bin/app
USER myuser
CMD ["/usr/local/bin/app"]
