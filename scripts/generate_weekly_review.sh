#!/bin/bash
# Weekly DASH/DPU/SmartSwitch Activity Review Generator
# 
# This script generates comprehensive weekly activity reports for DASH, DPU, and SmartSwitch
# development across the sonic-net organization repositories.
#
# Usage:
#   ./scripts/generate_weekly_review.sh [start_date] [end_date]
#
# Example:
#   ./scripts/generate_weekly_review.sh 2026-01-15 2026-01-27
#   ./scripts/generate_weekly_review.sh  # Uses last 12 days by default

set -e

# Configuration
KEYWORDS="DPU OR DASH OR SmartSwitch"
ORG="sonic-net"
OUTPUT_DIR="$(pwd)/weekly_reviews"

# Date handling
if [ -z "$1" ] || [ -z "$2" ]; then
    # Default: last 12 days (typical for weekly review with weekend)
    END_DATE=$(date +%Y-%m-%d)
    START_DATE=$(date -d "12 days ago" +%Y-%m-%d)
    echo "📅 No dates provided. Using last 12 days: $START_DATE to $END_DATE"
else
    START_DATE="$1"
    END_DATE="$2"
    echo "📅 Using provided dates: $START_DATE to $END_DATE"
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"
OUTPUT_FILE="$OUTPUT_DIR/DASH_DPU_SmartSwitch_Review_${START_DATE}_to_${END_DATE}.md"

echo "🚀 Generating DASH/DPU/SmartSwitch weekly review..."
echo "   Date range: $START_DATE to $END_DATE"
echo "   Keywords: $KEYWORDS"
echo "   Output: $OUTPUT_FILE"
echo ""

# Check for GitHub CLI
if ! command -v gh &> /dev/null; then
    echo "❌ ERROR: GitHub CLI (gh) is not installed."
    echo "   Please install it from: https://cli.github.com/"
    echo ""
    echo "   Or use the Python script instead:"
    echo "   python3 scripts/generate_weekly_review.py $START_DATE $END_DATE"
    exit 1
fi

# Check GitHub authentication
if ! gh auth status &> /dev/null; then
    echo "❌ ERROR: Not authenticated with GitHub CLI."
    echo "   Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI authenticated"
echo ""

# Query PRs merged
echo "📊 Querying merged PRs..."
MERGED_QUERY="org:${ORG} is:pr is:merged merged:${START_DATE}..${END_DATE} (${KEYWORDS}) in:title,body NOT [action] in:title NOT submodule in:title"
MERGED_COUNT=$(gh pr list --search "$MERGED_QUERY" --json number --limit 1000 | jq '. | length')
echo "   Found $MERGED_COUNT merged PRs"

# Query PRs created
echo "📊 Querying created PRs..."
CREATED_QUERY="org:${ORG} is:pr created:${START_DATE}..${END_DATE} (${KEYWORDS}) in:title,body NOT [action] in:title NOT submodule in:title"
CREATED_COUNT=$(gh pr list --search "$CREATED_QUERY" --json number --limit 1000 | jq '. | length')
echo "   Found $CREATED_COUNT created PRs"

echo ""
echo "📝 Generating report..."

# Generate report header
cat > "$OUTPUT_FILE" << EOF
# DASH/DPU/SmartSwitch Weekly Activity Review

**Report Period**: $START_DATE to $END_DATE  
**Generated**: $(date +"%Y-%m-%d %H:%M:%S")

---

## Executive Summary

This weekly review covers DASH, DPU, and SmartSwitch activity across sonic-net repositories.

**Query Period**: $START_DATE to $END_DATE

**Activity Summary**:
- **$MERGED_COUNT PRs merged** in query period
- **$CREATED_COUNT PRs created** in query period
- **Keywords**: DASH, DPU, Smart, SmartSwitch, 'Smart Switch', [ssw]

---

## GitHub Queries Used

### Query 1: PRs Merged
\`\`\`
$MERGED_QUERY
\`\`\`

### Query 2: PRs Created
\`\`\`
$CREATED_QUERY
\`\`\`

---

## PRs Merged ($MERGED_COUNT total)

**By Repository**:
EOF

# Count merged by repository
gh pr list --search "$MERGED_QUERY" --json repository --limit 1000 | \
    jq -r '.[] | .repository.name' | \
    sort | uniq -c | sort -rn | \
    awk '{print "- " $2 ": " $1 " PRs"}' >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

**All Merged PRs (Complete List)**:

| # | Repository | PR | Title | Merged | Link |
|---|------------|-----|-------|--------|------|
EOF

# Get merged PRs details
echo "   Fetching merged PR details..."
gh pr list --search "$MERGED_QUERY" --json number,title,repository,mergedAt,url --limit 1000 | \
    jq -r 'sort_by(.mergedAt) | reverse | .[] | "| " + (.repository.name) + " | #" + (.number|tostring) + " | " + .title + " | " + (.mergedAt[:10]) + " | [Link](" + .url + ") |"' | \
    awk '{print NR " " $0}' | sed 's/^/| /' | sed 's/ | /|/' >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

---

## PRs Created ($CREATED_COUNT total)

**By State**:
EOF

# Count by state
OPEN_COUNT=$(gh pr list --search "$CREATED_QUERY" --json state --limit 1000 | jq '[.[] | select(.state == "OPEN")] | length')
CLOSED_COUNT=$(echo "$CREATED_COUNT - $OPEN_COUNT" | bc)

cat >> "$OUTPUT_FILE" << EOF
- Open: $OPEN_COUNT PRs
- Closed/Merged: $CLOSED_COUNT PRs

**By Repository**:
EOF

# Count created by repository
gh pr list --search "$CREATED_QUERY" --json repository --limit 1000 | \
    jq -r '.[] | .repository.name' | \
    sort | uniq -c | sort -rn | \
    awk '{print "- " $2 ": " $1 " PRs"}' >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

**All Created PRs (Complete List)**:

| # | Repository | PR | Title | Created | State | Link |
|---|------------|-----|-------|---------|-------|------|
EOF

# Get created PRs details
echo "   Fetching created PR details..."
gh pr list --search "$CREATED_QUERY" --json number,title,repository,createdAt,state,url --limit 1000 | \
    jq -r 'sort_by(.createdAt) | reverse | .[] | "| " + (.repository.name) + " | #" + (.number|tostring) + " | " + .title + " | " + (.createdAt[:10]) + " | " + .state + " | [Link](" + .url + ") |"' | \
    awk '{print NR " " $0}' | sed 's/^/| /' | sed 's/ | /|/' >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

---

## Analysis

EOF

if [ "$CREATED_COUNT" -gt 0 ]; then
    MERGE_RATE=$(echo "scale=1; ($CLOSED_COUNT * 100) / $CREATED_COUNT" | bc 2>/dev/null || echo "N/A")
    echo "**Merge Rate**: ${MERGE_RATE}% of created PRs were closed/merged in the same period" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
fi

cat >> "$OUTPUT_FILE" << EOF
**Most Active Repositories**:
- Review the tables above to identify which repositories had the most activity
- sonic-mgmt and sonic-buildimage typically lead in test and platform work
- sonic-dash-ha shows highest DASH ecosystem velocity

**Key Focus Areas in This Period**:
- SmartSwitch/DPU platform development
- DASH HA services and BFD management
- Test infrastructure and stability improvements

---

*Report generated by: scripts/generate_weekly_review.sh*  
*Date range: $START_DATE to $END_DATE*  
*Keywords: DASH, DPU, Smart, SmartSwitch, 'Smart Switch', [ssw]*
EOF

echo ""
echo "✅ Report generated successfully!"
echo "📄 Output: $OUTPUT_FILE"
echo ""
echo "📖 To view the report:"
echo "   cat $OUTPUT_FILE"
echo "   less $OUTPUT_FILE"
echo "   code $OUTPUT_FILE"
echo ""
echo "🔄 To run weekly automatically, choose one:"
echo ""
echo "   Option 1 - Crontab (local machine):"
echo "   0 9 * * 1 cd /path/to/DASH && ./scripts/generate_weekly_review.sh"
echo ""
echo "   Option 2 - GitHub Actions (see .github/workflows/weekly-review.yml)"
echo ""
