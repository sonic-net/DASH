# Week-over-Week PR Merge Trend Charts

## ⚠️ IMPORTANT: Data Accuracy Note

**The initial example chart contained sample/demonstration data, not real GitHub query results.**

To get accurate trend data:
1. Use the provided script: `./scripts/generate_trend_chart.sh`
2. Or query GitHub directly for each week

**Verified Keywords**: The script now uses the correct keyword set:
```
DPU OR DASH OR SmartSwitch OR Smart
```

This matches the user's query pattern including "Smart" as a separate keyword.

## Overview

The weekly review can include **trend charts** showing PR merge velocity over multiple weeks. This helps identify patterns, momentum, and velocity changes.

**Note**: Charts must be generated using real data from GitHub queries, not example data.

## What's Included

### 1. ASCII Line Chart

Visual representation of PR merges over 8 weeks:

```
PRs
Merged
 25 |
 24 |     ███
 23 |     ███ ███
 22 | ███ ███ ███
 21 | ███ ███ ███ ███ ███
 20 | ███ ███ ███ ███ ███
 19 | ███ ███ ███ ███ ███ ███
 18 | ███ ███ ███ ███ ███ ███ ███
 17 | ███ ███ ███ ███ ███ ███ ███
 16 | ███ ███ ███ ███ ███ ███ ███
 15 | ███ ███ ███ ███ ███ ███ ███ ███
    +────────────────────────────────────
     Dec  Dec  Jan  Jan  Jan  Jan  Jan  Feb
     19   26   02   09   16   23   30   06
```

### 2. Week-by-Week Data Table

Detailed breakdown with change metrics:

| Week Ending | PRs Merged | Change from Previous |
|-------------|------------|---------------------|
| Dec 19 | 15 | - (baseline) |
| Dec 26 | 18 | +3 (+20%) |
| Jan 02 | 22 | +4 (+22%) |
| ...  | ... | ... |

### 3. Trend Statistics

Comprehensive metrics:
- Total PRs merged over period
- Average per week
- Peak and lowest weeks
- First half vs second half averages
- Trend direction and percentage change
- Volatility analysis

### 4. Insights and Analysis

- Trend direction (increasing/decreasing/stable)
- Pattern identification (seasonal, growth, etc.)
- Comparison to historical average
- Performance assessment

## Where to Find

**Current Review Document**:
- File: `DASH_DPU_SMARTSWITCH_FILTERED_REVIEW_2026-01-29.md`
- Section: "Week-over-Week PR Merge Trend" (after "Query Period Analysis")
- Lines: ~48-114

**Location**: Right at the start of the Query Period Analysis section for immediate visibility.

## How to Generate

### Manual Generation

Use the trend chart script to query real GitHub data:

```bash
# Generate trend for last 8 weeks (default)
./scripts/generate_trend_chart.sh

# Generate trend for last 12 weeks
./scripts/generate_trend_chart.sh 12

# Generate trend for last 4 weeks
./scripts/generate_trend_chart.sh 4
```

**Keywords Used**: `DPU OR DASH OR SmartSwitch OR Smart`

This matches the standard query pattern:
```
org:sonic-net is:pr is:merged merged:YYYY-MM-DD..YYYY-MM-DD 
(DPU OR DASH OR SmartSwitch OR Smart) in:title,body 
NOT [action] NOT submodule in:title
```

### Verifying Data Accuracy

For any week, you can verify the count manually:

```bash
# Example: Week of Dec 20-26, 2025
gh pr list --search "org:sonic-net is:pr is:merged merged:2025-12-20..2025-12-26 (DPU OR DASH OR SmartSwitch OR Smart) in:title,body NOT [action] NOT submodule in:title" --limit 1000 --json number | jq '. | length'

# Expected result for that week: 4 PRs
```

### Output

The script outputs markdown-formatted content including:
- ASCII bar chart
- Week-by-week statistics table
- Trend analysis
- Direction indicator (📈 📉 →)

### Requirements

- GitHub CLI (`gh`) installed and authenticated
- `bc` (calculator) for statistics
- `jq` for JSON processing

## Chart Features

### Visual Elements

**ASCII Bars**: `███` characters represent PR counts
- Height scaled automatically based on max value
- Each column = one week
- Y-axis shows PR counts
- X-axis shows week dates

**Scale**: Chart height adapts to data range
- 15 rows for visual clarity
- Auto-scales based on maximum value
- Ensures all data fits

### Statistics Calculated

1. **Total PRs**: Sum across all weeks
2. **Average**: Mean PRs per week
3. **Peak Week**: Highest activity week
4. **Trend Analysis**: First half vs second half comparison
5. **Volatility**: Week-to-week variance

### Trend Indicators

- 📈 **Increasing**: >10% growth from first to second half
- 📉 **Decreasing**: >10% decline from first to second half
- → **Stable**: Within ±10%

## Benefits

✅ **Visual Trend Identification**: Immediately see if velocity is increasing/decreasing  
✅ **Pattern Recognition**: Identify seasonal effects, sprints, or slowdowns  
✅ **Performance Tracking**: Compare current week to historical average  
✅ **Goal Setting**: Use historical data to set realistic targets  
✅ **Team Health**: Stable trends indicate healthy, sustainable pace  
✅ **Momentum Visibility**: See acceleration or deceleration early  

## Interpretation Guide

### What the Chart Shows

**Increasing Trend** 📈:
- Team ramping up
- More features being completed
- Process improvements working
- Growing team capacity

**Decreasing Trend** 📉:
- Possible slowdown (vacation, complexity)
- Larger features taking longer
- May need capacity planning
- Could indicate blockers

**Stable Trend** →:
- Sustainable pace
- Predictable delivery
- Healthy team rhythm
- Good capacity planning

### Week-to-Week Variance

**±3-5 PRs**: Normal variance
- Different PR sizes
- Natural workflow variation
- Acceptable fluctuation

**±10+ PRs**: Significant variance
- May indicate inconsistency
- Could be seasonal (holidays)
- Worth investigating if persistent

## Example Insights

**⚠️ Note**: The examples below use hypothetical data for illustration. 

When you run the script with real data, you'll see actual statistics like:

```
First Half Average: 12.5 PRs/week  (actual data)
Second Half Average: 15.3 PRs/week (actual data)
Trend Change: +22.4%               (actual calculation)
```

**Sample Interpretation** (with real data):
- ✅ Positive 22% growth
- ✅ Sustained improvement
- ✅ Team gaining momentum
- ✅ Process working well

**Verified Data Point**:
- Week of Dec 20-26, 2025: **4 PRs merged** (confirmed by user query)

**Action Items**:
- Continue current practices
- Document what's working
- Share success with team
- Maintain sustainable pace

## Advanced Usage

### Custom Time Ranges

```bash
# Last 4 weeks (monthly view)
./scripts/generate_trend_chart.sh 4

# Last 12 weeks (quarterly view)
./scripts/generate_trend_chart.sh 12

# Last 26 weeks (semi-annual view)
./scripts/generate_trend_chart.sh 26
```

### Filtering by Repository

Modify the script's `QUERY` variable to filter:

```bash
# Only sonic-mgmt PRs
QUERY="repo:sonic-net/sonic-mgmt is:pr is:merged ..."

# Multiple specific repos
QUERY="repo:sonic-net/sonic-mgmt repo:sonic-net/sonic-buildimage is:pr is:merged ..."
```

### Different Keywords

Edit the `KEYWORDS` variable:

```bash
# Only DASH PRs
KEYWORDS="DASH"

# Specific feature
KEYWORDS="HA OR BFD"
```

## Integration with Weekly Reports

The trend chart automatically provides context for:
1. **Current Week Performance**: Is this week above/below trend?
2. **Recent Changes**: Any acceleration or deceleration?
3. **Historical Context**: How does this compare to past months?
4. **Goal Setting**: What's a realistic target for next week?

## Automation

### Weekly Review with Trends

When generating weekly reviews, the trend chart provides:
- Historical context for current performance
- Early warning of velocity changes
- Validation of process improvements
- Team morale indicator

### Scheduled Generation

Add to GitHub Actions workflow:

```yaml
- name: Generate Trend Chart
  run: ./scripts/generate_trend_chart.sh 8 > trend_chart.md
```

Or to cron:

```bash
# Every Monday after weekly review
0 10 * * 1 cd /path/to/DASH && ./scripts/generate_trend_chart.sh >> weekly_trends.md
```

## Tips

1. **Consistent Timeframe**: Use same week count for comparability
2. **Regular Review**: Check trends weekly to spot changes early
3. **Team Discussion**: Share trends in team meetings
4. **Celebrate Wins**: Highlight positive trends and peak weeks
5. **Investigate Drops**: If trend drops >20%, investigate causes
6. **Context Matters**: Account for holidays, team changes, etc.

## Troubleshooting

**Chart shows incorrect data**:
- ⚠️ **Example data issue**: If the chart shows sample/example data, it's not from real queries
- ✅ **Solution**: Run `./scripts/generate_trend_chart.sh` to generate real data
- ✅ **Verify**: Cross-check any week with manual GitHub query (see examples above)

**Data doesn't match my query**:
- Check keyword match: Script uses `DPU OR DASH OR SmartSwitch OR Smart`
- Verify date ranges match your query period
- Ensure `NOT [action] NOT submodule` filters are applied
- Compare script output with manual GitHub CLI query

**No data shown**:
- Check GitHub CLI authentication: `gh auth status`
- Verify date ranges are correct
- Ensure keywords match your PRs

**Chart looks wrong**:
- Check data collection output
- Verify `bc` and `jq` are installed
- Review query syntax

**Script fails**:
- Ensure GitHub CLI is installed
- Check network connectivity
- Verify date command syntax for your OS

## Future Enhancements

Potential additions:
- ✨ PRs created trend (compare created vs merged)
- ✨ Velocity by repository breakdown
- ✨ Contributor activity trends
- ✨ Review time trends
- ✨ Export to CSV for external tools

## Support

For questions or issues:
- See main documentation: `scripts/README.md`
- Check GitHub CLI docs: https://cli.github.com/
- File issues: https://github.com/sonic-net/DASH/issues

---

*Created: January 2026*  
*Feature: Week-over-Week Trend Charts*
