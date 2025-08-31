#!/bin/bash
# Script to initialize the application and ensure Weaviate is running

# Wait for Weaviate to be ready
echo "Waiting for Weaviate to be ready..."
max_retries=30
retry_count=0
weaviate_ready=false

while [ $retry_count -lt $max_retries ] && [ "$weaviate_ready" = false ]; do
  if curl -s "http://${WEAVIATE_HOST:-weaviate}:${WEAVIATE_PORT:-8080}/v1/meta" > /dev/null; then
    echo "Weaviate is ready!"
    weaviate_ready=true
  else
    echo "Weaviate not ready yet. Retrying in 2 seconds..."
    sleep 2
    retry_count=$((retry_count + 1))
  fi
done

if [ "$weaviate_ready" = false ]; then
  echo "Weaviate did not become ready in time. Starting application anyway..."
fi

# Run the application
exec streamlit run app.py --server.port=8501 --server.address=0.0.0.0
