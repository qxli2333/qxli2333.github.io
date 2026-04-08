#!/bin/bash
set -e

# Navigate to the directory containing this script
cd "$(dirname "$0")"

echo "=========================================="
echo "1/4: Updating citation statistics from ADS"
echo "=========================================="
python3 update_citations.py

echo ""
echo "=========================================="
echo "2/4: Fetching missing keywords from ADS"
echo "=========================================="
python3 update_keywords.py

echo ""
echo "=========================================="
echo "3/4: Generating publication markdown files"
echo "=========================================="
python3 generate_pubs.py

echo ""
echo "=========================================="
echo "4/4: Categorizing publications on research pages"
echo "=========================================="
python3 generate_research_lists.py

echo ""
echo "=========================================="
echo "All updates completed successfully!"
echo "=========================================="
