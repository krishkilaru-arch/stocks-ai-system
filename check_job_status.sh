#!/bin/bash
# Quick script to check job status without blocking

JOB_NAME="daily-stock-data-ingestion"

echo "Checking status of job: $JOB_NAME"
echo "=================================="

# Get job ID
JOB_ID=$(databricks jobs list 2>&1 | grep -i "$JOB_NAME" | awk '{print $1}')

if [ -z "$JOB_ID" ]; then
    echo "Job not found: $JOB_NAME"
    exit 1
fi

echo "Job ID: $JOB_ID"
echo ""

# Get latest run
LATEST_RUN=$(databricks jobs runs list --job-id $JOB_ID --limit 1 2>&1)

if [ -n "$LATEST_RUN" ]; then
    echo "Latest Run:"
    echo "$LATEST_RUN" | head -10
    echo ""
    
    # Extract run ID if available
    RUN_ID=$(echo "$LATEST_RUN" | grep -oP 'run_id:\s*\K\d+' | head -1)
    if [ -n "$RUN_ID" ]; then
        echo "Run ID: $RUN_ID"
        echo ""
        echo "Run Details:"
        databricks jobs runs get --run-id $RUN_ID 2>&1 | head -20
    fi
else
    echo "No runs found for this job"
fi
