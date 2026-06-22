#!/bin/bash
# Generate Week-over-Week PR Merge Trend Chart
# 
# This script queries GitHub for PR merges over multiple weeks and creates
# an ASCII line chart showing the trend.
#
# Usage:
#   ./scripts/generate_trend_chart.sh [weeks_back]
#
# Example:
#   ./scripts/generate_trend_chart.sh 8  # Last 8 weeks

set -e

# Configuration
KEYWORDS="DPU OR DASH OR SmartSwitch OR Smart"
ORG="sonic-net"
WEEKS_BACK=${1:-8}  # Default to 8 weeks

echo "📊 Generating PR Merge Trend Chart..."
echo "   Analyzing last $WEEKS_BACK weeks"
echo "   Keywords: $KEYWORDS"
echo ""

# Check for GitHub CLI
if ! command -v gh &> /dev/null; then
    echo "❌ ERROR: GitHub CLI (gh) is not installed."
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo "❌ ERROR: Not authenticated with GitHub CLI."
    exit 1
fi

# Arrays to store data
declare -a WEEK_LABELS
declare -a MERGE_COUNTS

# Collect data for each week
echo "📈 Collecting data..."
for ((i=$WEEKS_BACK-1; i>=0; i--)); do
    # Calculate week boundaries
    END_DATE=$(date -d "$i weeks ago" +%Y-%m-%d)
    START_DATE=$(date -d "$i weeks ago - 6 days" +%Y-%m-%d)
    
    # Query merged PRs for this week
    QUERY="org:${ORG} is:pr is:merged merged:${START_DATE}..${END_DATE} (${KEYWORDS}) in:title,body NOT [action] NOT submodule"
    COUNT=$(gh pr list --search "$QUERY" --json number --limit 1000 2>/dev/null | jq '. | length' || echo "0")
    
    # Store data
    WEEK_LABELS+=("$(date -d "$i weeks ago" +"%b %d")")
    MERGE_COUNTS+=($COUNT)
    
    echo "   Week ending $END_DATE: $COUNT PRs merged"
done

echo ""
echo "✅ Data collection complete"
echo ""

# Generate ASCII chart
echo "## Week-over-Week PR Merge Trend"
echo ""
echo "**Last $WEEKS_BACK Weeks** - DASH/DPU/SmartSwitch PRs Merged"
echo ""

# Find max value for scaling
MAX_COUNT=0
for count in "${MERGE_COUNTS[@]}"; do
    if [ $count -gt $MAX_COUNT ]; then
        MAX_COUNT=$count
    fi
done

# Ensure we have at least 1 for scaling
if [ $MAX_COUNT -eq 0 ]; then
    MAX_COUNT=1
fi

# Create ASCII chart
echo "\`\`\`"
echo "PRs Merged"
echo ""

# Scale factor (chart height = 15 rows)
CHART_HEIGHT=15
SCALE=$(echo "scale=2; $MAX_COUNT / $CHART_HEIGHT" | bc -l)
if [ $(echo "$SCALE < 1" | bc) -eq 1 ]; then
    SCALE=1
fi

# Print Y-axis and bars
for ((row=$CHART_HEIGHT; row>=0; row--)); do
    THRESHOLD=$(echo "scale=0; $row * $SCALE" | bc)
    
    # Y-axis label
    printf "%3d |" $THRESHOLD
    
    # Bars for each week
    for count in "${MERGE_COUNTS[@]}"; do
        if [ $count -ge $THRESHOLD ]; then
            printf " ███"
        else
            printf "    "
        fi
    done
    echo ""
done

# X-axis
printf "    +"
for ((i=0; i<$WEEKS_BACK; i++)); do
    printf "────"
done
echo ""

# Week labels (rotated)
printf "     "
for label in "${WEEK_LABELS[@]}"; do
    printf " %3s" "$(echo $label | cut -d' ' -f2)"
done
echo ""

echo "\`\`\`"
echo ""

# Statistics
TOTAL=0
for count in "${MERGE_COUNTS[@]}"; do
    TOTAL=$((TOTAL + count))
done
AVG=$(echo "scale=1; $TOTAL / $WEEKS_BACK" | bc)

# Calculate trend
FIRST_HALF_SUM=0
SECOND_HALF_SUM=0
HALF=$((WEEKS_BACK / 2))

for ((i=0; i<$HALF; i++)); do
    FIRST_HALF_SUM=$((FIRST_HALF_SUM + ${MERGE_COUNTS[$i]}))
done

for ((i=$HALF; i<$WEEKS_BACK; i++)); do
    SECOND_HALF_SUM=$((SECOND_HALF_SUM + ${MERGE_COUNTS[$i]}))
done

FIRST_HALF_AVG=$(echo "scale=1; $FIRST_HALF_SUM / $HALF" | bc)
SECOND_HALF_AVG=$(echo "scale=1; $SECOND_HALF_SUM / ($WEEKS_BACK - $HALF)" | bc)

echo "**Trend Statistics**:"
echo ""
echo "| Metric | Value |"
echo "|--------|-------|"
echo "| Total PRs Merged ($WEEKS_BACK weeks) | $TOTAL |"
echo "| Average per Week | $AVG |"
echo "| Peak Week | $MAX_COUNT PRs |"
echo "| First Half Average | $FIRST_HALF_AVG PRs/week |"
echo "| Second Half Average | $SECOND_HALF_AVG PRs/week |"

# Trend direction
TREND_CHANGE=$(echo "scale=1; (($SECOND_HALF_AVG - $FIRST_HALF_AVG) / $FIRST_HALF_AVG) * 100" | bc 2>/dev/null || echo "0")

echo ""
if [ $(echo "$TREND_CHANGE > 10" | bc) -eq 1 ]; then
    echo "**Trend**: 📈 Increasing (+${TREND_CHANGE}% from first to second half)"
elif [ $(echo "$TREND_CHANGE < -10" | bc) -eq 1 ]; then
    TREND_CHANGE=${TREND_CHANGE#-}  # Remove negative sign
    echo "**Trend**: 📉 Decreasing (-${TREND_CHANGE}% from first to second half)"
else
    echo "**Trend**: → Stable (${TREND_CHANGE}% change)"
fi

echo ""
echo "---"
echo ""
echo "*Chart generated: $(date +"%Y-%m-%d %H:%M:%S")*"

