FROM node:20-slim AS base
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

COPY . /frontend
WORKDIR /frontend

RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install

