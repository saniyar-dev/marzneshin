FROM node:20-bookworm-slim AS dashboard
WORKDIR /app/dashboard

ARG VITE_BASE_API=/api/
ENV VITE_BASE_API=${VITE_BASE_API}

COPY dashboard/package.json dashboard/pnpm-lock.yaml ./
COPY .npmrc /app/.npmrc

RUN corepack enable \
 && corepack prepare pnpm@9 --activate \
 && pnpm install --frozen-lockfile

COPY dashboard/ ./
RUN pnpm build


FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=dashboard /app/dashboard/dist /app/dashboard/dist
COPY . /app

RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["sh", "-c", "alembic upgrade head && python3 main.py"]