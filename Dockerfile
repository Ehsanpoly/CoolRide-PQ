FROM gcc:14 AS cpp-build
WORKDIR /src
COPY core/cpp ./core/cpp
RUN g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Werror \
    -Icore/cpp/include core/cpp/src/controller.cpp core/cpp/src/cli.cpp \
    -o /coolride-controller

FROM python:3.12-slim
WORKDIR /app
ENV PYTHONPATH=/app/src PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY . /app
COPY --from=cpp-build /coolride-controller /usr/local/bin/coolride-controller
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/api/health', timeout=2)"
CMD ["python", "-m", "coolride_pq", "serve", "--host", "0.0.0.0", "--port", "8080"]
