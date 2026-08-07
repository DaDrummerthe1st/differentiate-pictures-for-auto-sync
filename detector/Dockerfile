FROM python:3.12-slim

WORKDIR /app

# libgl1 + libglib2.0-0: opencv-python-headless still dynamically links
# against libGL/libglib at import time even though it ships no GUI code -
# missing on python:3.12-slim by default, confirmed via a real image build
# (ImportError: libGL.so.1: cannot open shared object file) rather than
# assumed from opencv's own docs.
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY detector/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY detector/ ./detector/

EXPOSE 8500
CMD ["uvicorn", "detector.main:app", "--host", "0.0.0.0", "--port", "8500", "--no-server-header"]
