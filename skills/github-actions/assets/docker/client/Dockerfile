# syntax=docker/dockerfile:1

FROM oven/bun:1.4.0 AS deps
WORKDIR /app
COPY package.json bun.lock bunfig.tom[l] ./
RUN bun install --frozen-lockfile --ignore-scripts

FROM deps AS builder
COPY . .
RUN bun install --frozen-lockfile
RUN bun run build

FROM builder AS production-deps
# 在已执行生命周期脚本的依赖树上裁剪，保留生产依赖生成的运行文件。
RUN bun prune --production

FROM oven/bun:1.4.0-slim AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json ./package.json
COPY --from=production-deps /app/node_modules ./node_modules
USER bun
EXPOSE 3000
CMD ["bun", "build/index.js"]
