# Humotica - Docker Image
# The complete protocol stack for secure AI communication
#
# Build: docker build -t humotica .
# Run:   docker run -i humotica
#
# Part of HumoticaOS - https://humotica.com

FROM python:3.11-slim

LABEL maintainer="Jasper van de Meent <info@humotica.com>"
LABEL org.opencontainers.image.source="https://github.com/jaspertvdm/humotica"
LABEL org.opencontainers.image.description="HumoticaOS Protocol Stack - Secure AI Communication"
LABEL org.opencontainers.image.licenses="MIT"

# Install from PyPI (includes ainternet + tibet)
RUN pip install --no-cache-dir humotica

# MCP servers communicate via stdio
ENTRYPOINT ["python", "-c", "from humotica import info; info()"]
