#!/bin/bash
# Monitor Databricks job status

JOB_ID="993673216113262"
JOB_NAME="daily-stock-data-ingestion"

echo "Monitoring job: $JOB_NAME (ID: $JOB_ID)"
echo "========================================"
echo ""

# Get latest run
echo "Latest Run Status:"
databricks jobs list-runs --job-id $JOB_ID --limit 1 2>&1

echo ""
echo "To check status again, run: ./monitor_job.sh"
echo "Or use: databricks jobs list-runs --job-id $JOB_ID --limit 1"
echo ""
echo "To run job without waiting: databricks bundle run daily_data_ingestion --no-wait"
