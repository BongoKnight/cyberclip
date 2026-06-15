# Build stage
FROM dockerproxy.repos.tech.orange/python:3.12-slim AS builder

WORKDIR /build

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir ".[all]"

# Production image
FROM dockerproxy.repos.tech.orange/python:3.12-slim AS final

# Add non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup --home /app appuser

# Pull packages
COPY --from=builder /venv /venv
RUN chown -R appuser:appgroup /venv/lib/python3.12/site-packages/cyberclip/data
RUN touch /venv/lib/python3.12/site-packages/cyberclip/log.log \
    && chown appuser:appgroup /venv/lib/python3.12/site-packages/cyberclip/log.log

ENV PATH="/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER appuser
WORKDIR /app

EXPOSE 8000

ENTRYPOINT ["cyberclip"]
CMD ["--help"] 