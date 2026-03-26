# Build stage
FROM python:3.12-slim AS builder

WORKDIR /build

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir ".[all]"

# Production image
FROM python:3.12-slim AS final

# Add non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Pull packages
COPY --from=builder /venv /venv
RUN chown -R appuser:appgroup /venv/lib/python3.12/site-packages/cyberclip/data

ENV PATH="/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER appuser
WORKDIR /app

EXPOSE 8000

ENTRYPOINT ["cyberclip"]
CMD ["--help"] 