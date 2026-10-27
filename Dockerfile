FROM node:20-alpine AS portal-build

WORKDIR /portal
COPY portal/package*.json ./
RUN npm ci
COPY portal ./
RUN npm run build

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system mechman && adduser --system --ingroup mechman mechman

COPY pyproject.toml README.md ./
COPY mechman_bot ./mechman_bot
RUN pip install --no-cache-dir .

COPY --from=portal-build /portal/dist ./portal/dist
RUN mkdir -p /app/data && chown -R mechman:mechman /app/data

USER mechman
EXPOSE 8000
VOLUME ["/app/data"]

CMD ["mechman-dashboard"]
