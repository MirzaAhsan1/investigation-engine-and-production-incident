#!/bin/bash
while true; do
  cpu=$(top -bn1 | grep 'Cpu(s)' | awk '{print $2}')
  mem=$(free | grep Mem | awk '{print $3/$2 * 100.0}')
  curl -s -X POST http://localhost:8000/api/metrics/ingest \
    -H "Content-Type: application/json" \
    -d "{\"api_key\":\"b4c7bfc5a797e94482a67da6564f97fb63797439e9d421227755c762b3cf80f5\",\"host\":\"fraud-server-01\",\"container_name\":\"fraud-dummy\",\"cpu_usage\":$cpu,\"memory_usage\":$mem}"
  echo ""
  sleep 5
done