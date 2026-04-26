FROM ollama/ollama:latest

# 기본 모델 (compose env로 override 가능)
ENV OLLAMA_MODEL=gemma3:4b
ENV OLLAMA_HOST=0.0.0.0

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
