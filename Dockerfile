FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12-slim

RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -m -s /sbin/nologin appuser

WORKDIR /home/appuser/app

COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=10001:10001 src/ ./src

ENV PATH=/home/appuser/local/bin:$PATH
ENV PYTHONPATH=/home/appuser/app

USER 10001

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]