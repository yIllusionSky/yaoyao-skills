# syntax=docker/dockerfile:1

FROM oven/bun:__BUN_VERSION__ AS dependencies
WORKDIR /app
COPY bun.lock bunfig.tom[l] ./
COPY --parents ./**/package.json ./
ARG TYPESCRIPT_PACKAGE=__TYPESCRIPT_PACKAGE__
RUN --mount=type=secret,id=npmrc,target=/app/.npmrc,required=false \
    bun ci --filter "$TYPESCRIPT_PACKAGE" --ignore-scripts

FROM dependencies AS builder
COPY . .
ARG TYPESCRIPT_APP=__TYPESCRIPT_APP__
RUN --mount=type=secret,id=npmrc,target=/app/.npmrc,required=false \
    bun ci --filter "$TYPESCRIPT_PACKAGE"
RUN bun run --filter "$TYPESCRIPT_PACKAGE" build

FROM oven/bun:__BUN_VERSION__-slim AS runtime
WORKDIR /app
ENV NODE_ENV=production
ARG TYPESCRIPT_APP=__TYPESCRIPT_APP__
COPY --from=builder --chown=bun:bun /app/${TYPESCRIPT_APP}/package.json ./package.json
COPY --from=builder --chown=bun:bun /app/${TYPESCRIPT_APP}/dist ./dist
USER bun
EXPOSE 3000
CMD ["bun", "run", "start"]
