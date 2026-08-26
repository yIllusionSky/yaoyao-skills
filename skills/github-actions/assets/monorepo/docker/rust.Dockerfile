FROM clux/muslrust:stable AS chef
USER root
RUN cargo install --locked cargo-chef
WORKDIR /app

FROM chef AS planner
COPY . .
RUN cargo chef prepare --recipe-path recipe.json

FROM chef AS builder
ARG RUST_PACKAGE=__RUST_PACKAGE__
ARG RUST_BIN=__RUST_BIN__
ARG TARGETARCH
COPY --from=planner /app/recipe.json recipe.json
RUN case "$TARGETARCH" in \
      amd64) rust_target=x86_64-unknown-linux-musl ;; \
      arm64) rust_target=aarch64-unknown-linux-musl ;; \
      *) echo "Unsupported target architecture: $TARGETARCH" && exit 1 ;; \
    esac && \
    cargo chef cook --release --target "$rust_target" \
      --package "$RUST_PACKAGE" --bin "$RUST_BIN" --recipe-path recipe.json
COPY . .
RUN case "$TARGETARCH" in \
      amd64) rust_target=x86_64-unknown-linux-musl ;; \
      arm64) rust_target=aarch64-unknown-linux-musl ;; \
      *) echo "Unsupported target architecture: $TARGETARCH" && exit 1 ;; \
    esac && \
    cargo build --release --target "$rust_target" --package "$RUST_PACKAGE" --bin "$RUST_BIN" && \
    cp "target/$rust_target/release/$RUST_BIN" /tmp/app

FROM alpine:3.22 AS runtime
RUN addgroup -S app && adduser -S app -G app
COPY --from=builder /tmp/app /usr/local/bin/app
USER app
EXPOSE 8080
CMD ["/usr/local/bin/app"]
