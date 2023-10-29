FROM kovarcodes/bullseye-poetry:latest

# Set environment variables
ARG DOWNLOAD_PATH

# Install ffmpeg
RUN apt-get update && apt-get install ffmpeg -y

# Copy project files
RUN mkdir -p /vidyodl
COPY . /vidyodl
WORKDIR /vidyodl

# Create download directories 
RUN mkdir -p ${DOWNLOAD_PATH} \
    && mkdir -p /vidyodl/${DOWNLOAD_PATH}/audio \
    && mkdir -p /vidyodl/${DOWNLOAD_PATH}/video \
    && mkdir -p /vidyodl/${DOWNLOAD_PATH}/complete

# Setup Poetry and install dependencies
ENV PATH="${PATH}:/root/.poetry/bin"
RUN python3 -m poetry config virtualenvs.create false \
    && python3 -m poetry install --no-interaction \
    && rm -rf /root/.cache/pypoetry

EXPOSE 8000
CMD ["uvicorn", "--reload", "--host=0.0.0.0", "--port=8000", "server.main:vidyodl_app"]