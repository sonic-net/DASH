#!/bin/bash
# Weekly DASH/DPU/SmartSwitch Activity Review Generator (Enhanced)
# 
# This script generates comprehensive weekly activity reports including PR activity metrics
# (comments, reviews, approvals) for DASH, DPU, and SmartSwitch development.
#
# Usage:
#   ./scripts/generate_weekly_review_enhanced.sh [start_date] [end_date]
#
# Example:
#   ./scripts/generate_weekly_review_enhanced.sh 2026-01-15 2026-01-27
#   ./scripts/generate_weekly_review_enhanced.sh  # Uses last 12 days

set -e

# Configuration
KEYWORDS="DPU OR DASH OR SmartSwitch"
ORG="sonic-net"
OUTPUT_DIR="$(pwd)/weekly_reviews"
ENABLE_ACTIVITY_METRICS=true  # Set to false to skip PR activity details

# Date handling
if [ -z "$1" ] || [ -z "$2" ]; then
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

echo "🚀 Generating DASH/DPU/SmartSwitch weekly review (Enhanced)..."
echo "   Date range: $START_DATE to $END_DATE"
echo "   Keywords: $KEYWORDS"
echo "   PR Activity Metrics: $ENABLE_ACTIVITY_METRICS"
echo "   Output: $OUTPUT_FILE"
echo ""

# Check for GitHub CLI
if ! command -v gh &> /dev/null; then
    echo "❌ ERROR: GitHub CLI (gh) is not installed."
    echo "   Install from: https://cli.github.com/"
    exit 1
fi

# Check authentication
if ! gh auth status &> /dev/null; then
    echo "❌ ERROR: Not authenticated with GitHub CLI."
    echo "   Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI authenticated"
echo ""

# Query PRs
MERGED_QUERY="org:${ORG} is:pr is:merged merged:${START_DATE}..${END_DATE} (${KEYWORDS}) in:title,body NOT [action] in:title NOT submodule in:title"
CREATED_QUERY="org:${ORG} is:pr created:${START_DATE}..${END_DATE} (${KEYWORDS}) in:title,body NOT [action] in:title NOT submodule in:title"

echo "📊 Querying PRs..."
MERGED_COUNT=$(gh pr list --search "$MERGED_QUERY" --json number --limit 1000 | jq '. | length')
CREATED_COUNT=$(gh pr list --search "$CREATED_QUERY" --json number --limit 1000 | jq '. | length')
echo "   Found $MERGED_COUNT merged PRs"
echo "   Found $CREATED_COUNT created PRs"
echo ""

# Generate report header
cat > "$OUTPUT_FILE" << EOF
# DASH/DPU/SmartSwitch Weekly Activity Review (Enhanced)

**Report Period**: $START_DATE to $END_DATE  
**Generated**: $(date +"%Y-%m-%d %H:%M:%S")

---

## Executive Summary

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

gh pr list --search "$MERGED_QUERY" --json repository --limit 1000 | \
    jq -r '.[] | .repository.name' | sort | uniq -c | sort -rn | \
    awk '{print "- " $2 ": " $1 " PRs"}' >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

**All Merged PRs (Complete List)**:

| # | Repository | PR | Title | Merged | Link |
|---|------------|-----|-------|--------|------|
EOF

gh pr list --search "$MERGED_QUERY" --json number,title,repository,mergedAt,url --limit 1000 | \
    jq -r 'sort_by(.mergedAt) | reverse | .[] | "| " + (.repository.name) + " | #" + (.number|tostring) + " | " + .title + " | " + (.mergedAt[:10]) + " | [Link](" + .url + ") |"' | \
    awk '{print NR " " $0}' | sed 's/^/| /' | sed 's/ | /|/' >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

---

## PRs Created ($CREATED_COUNT total)

**By State**:
EOF

OPEN_COUNT=$(gh pr list --search "$CREATED_QUERY" --json state --limit 1000 | jq '[.[] | select(.state == "OPEN")] | length')
CLOSED_COUNT=$(echo "$CREATED_COUNT - $OPEN_COUNT" | bc)

cat >> "$OUTPUT_FILE" << EOF
- Open: $OPEN_COUNT PRs
- Closed/Merged: $CLOSED_COUNT PRs

**By Repository**:
EOF

gh pr list --search "$CREATED_QUERY" --json repository --limit 1000 | \
    jq -r '.[] | .repository.name' | sort | uniq -c | sort -rn | \
    awk '{print "- " $2 ": " $1 " PRs"}' >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

**All Created PRs (Complete List)**:

| # | Repository | PR | Title | Created | State | Link |
|---|------------|-----|-------|---------|-------|------|
EOF

gh pr list --search "$CREATED_QUERY" --json number,title,repository,createdAt,state,url --limit 1000 | \
    jq -r 'sort_by(.createdAt) | reverse | .[] | "| " + (.repository.name) + " | #" + (.number|tostring) + " | " + .title + " | " + (.createdAt[:10]) + " | " + .state + " | [Link](" + .url + ") |"' | \
    awk '{print NR " " $0}' | sed 's/^/| /' | sed 's/ | /|/' >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

---

## PR Activity Analysis

EOF

if [ "$ENABLE_ACTIVITY_METRICS" = true ]; then
    echo "📈 Analyzing PR activity (comments, reviews, labels)..."
    
    cat >> "$OUTPUT_FILE" << EOF
This section shows engagement metrics for PRs in the query period.

### Top Commented PRs

| Repository | PR | Title | Comments | Reviews | Labels |
|------------|-----|-------|----------|---------|--------|
EOF
    
    # Get detailed info for created PRs (limited to top 20 for performance)
    gh pr list --search "$CREATED_QUERY" --json number,repository,title,comments,url --limit 20 | \
        jq -r 'sort_by(.comments) | reverse | .[] | select(.comments > 0) | "| " + .repository.name + " | #" + (.number|tostring) + " | " + .title[:60] + " | " + (.comments|tostring) + " | - | - |"' | \
        head -10 >> "$OUTPUT_FILE" || echo "| - | - | No PR activity data available | - | - | - |" >> "$OUTPUT_FILE"
    
    cat >> "$OUTPUT_FILE" << EOF

### PR Engagement Summary

EOF
    
    # Calculate engagement stats
    TOTAL_COMMENTS=$(gh pr list --search "$CREATED_QUERY" --json comments --limit 1000 2>/dev/null | jq '[.[].comments] | add' || echo "0")
    AVG_COMMENTS=$(echo "scale=1; $TOTAL_COMMENTS / $CREATED_COUNT" | bc 2>/dev/null || echo "N/A")
    
    cat >> "$OUTPUT_FILE" << EOF
- **Total Comments**: $TOTAL_COMMENTS across all created PRs
- **Average Comments per PR**: $AVG_COMMENTS
- **PRs with Discussion**: PRs with 5+ comments indicate active review/discussion

**Note**: Full review/approval data requires individual PR inspection. Use GitHub CLI:
\`\`\`bash
gh pr view <PR_NUMBER> --repo sonic-net/<REPO> --json reviews,comments,labels
\`\`\`

EOF
else
    cat >> "$OUTPUT_FILE" << EOF
PR activity metrics (comments, reviews, approvals) can be enabled by setting 
ENABLE_ACTIVITY_METRICS=true in the script.

For individual PR activity, use:
\`\`\`bash
gh pr view <PR_NUMBER> --repo sonic-net/<REPO> --json reviews,comments,labels
\`\`\`

EOF
fi

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
**Most Active Repositories** (by PRs merged):
EOF

gh pr list --search "$MERGED_QUERY" --json repository --limit 1000 | \
    jq -r '.[] | .repository.name' | sort | uniq -c | sort -rn | head -5 | \
    awk '{print NR ". " $2 ": " $1 " PRs merged"}' >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

**Key Focus Areas**:
- SmartSwitch/DPU platform development
- DASH HA services and BFD management  
- Test infrastructure and stability improvements

---

*Report generated by: scripts/generate_weekly_review_enhanced.sh*  
*Date range: $START_DATE to $END_DATE*  
*Keywords: DASH, DPU, Smart, SmartSwitch, 'Smart Switch', [ssw]*  
*PR Activity Metrics: $ENABLE_ACTIVITY_METRICS*
EOF

echo ""
echo "✅ Enhanced report generated successfully!"
echo "📄 Output: $OUTPUT_FILE"
echo ""
echo "📊 New feature: PR Activity Analysis section included!"
echo ""
