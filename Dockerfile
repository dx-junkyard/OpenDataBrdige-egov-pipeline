# Pythonのベースイメージを指定
FROM python:3.9-slim

RUN mkdir /work
RUN mkdir /app
RUN mkdir /app/pipeline
RUN mkdir /app/pipeline/lib

# 作業ディレクトリを設定
WORKDIR /app

# 必要なパッケージをインストール
RUN apt-get update && \
    apt-get install -y git wget curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


COPY ./app/* /app/



# 必要なPythonライブラリをインストール
RUN pip install --no-cache-dir -r dl_requirements.txt


WORKDIR /work





