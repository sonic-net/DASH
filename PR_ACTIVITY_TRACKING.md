# PR Activity Tracking Feature

## Overview

The weekly review now includes a **PR Activity Analysis** section that tracks engagement metrics:

- 💬 **Comments** - Discussion volume on each PR
- 👁️ **Reviews** - Code review activity
- ✅ **Approvals** - Approval patterns and timing
- 🏷️ **Labels** - Label trends and priorities

## What's Included

### 1. Most Discussed PRs Table

Shows PRs ranked by comment count to identify:
- Complex discussions
- Technical challenges
- Multi-stakeholder coordination needs

**Example:**
```markdown
| Repository | PR | Title | Comments | Reviews | State |
|------------|-----|-------|----------|---------|-------|
| sonic-mgmt | #22141 | HA privatelink | 15+ | 3 | Open |
| sonic-buildimage | #25178 | NPU crash fix | 12+ | 2 | Open |
```

### 2. Review Activity Patterns

- Review coverage % (how many PRs get reviewed)
- Average time to first review
- Review patterns by PR type (platform vs tests vs fixes)

### 3. Label Activity Trends

- Common labels used
- Priority distribution
- Label-based categorization

### 4. Approval Patterns

- Approved & merged rate
- PRs awaiting merge (approved but CI/dependencies pending)
- PRs under active review
- PRs awaiting initial review

### 5. Engagement Insights

- **High-engagement PRs**: Complex topics with 5+ comments
- **Quick-merge PRs**: Straightforward changes merged in 1-3 days
- **Blocked PRs**: Awaiting review or dependencies

## Benefits

✅ **Identify bottlenecks**: See which PRs need review attention  
✅ **Track health**: Measure review responsiveness  
✅ **Spot trends**: Understand what topics generate discussion  
✅ **Prioritize**: Focus on high-comment PRs first  
✅ **Celebrate wins**: Recognize efficient quick-merges  

## How to Use

### In Current Report

The PR Activity Analysis section is now included in:
- `DASH_DPU_SMARTSWITCH_FILTERED_REVIEW_2026-01-29.md` (lines 403-531)

Look for the section titled: **"PR Activity Analysis (Engagement Metrics)"**

### In Automated Weekly Reports

**Option 1: Use Enhanced Script**
```bash
./scripts/generate_weekly_review_enhanced.sh 2026-01-15 2026-01-27
```

This script includes PR activity metrics by default.

**Option 2: Standard Script**
```bash
./scripts/generate_weekly_review.sh 2026-01-15 2026-01-27
```

Standard script focuses on PR lists only (faster, simpler).

## Getting Real-Time Data

While the review provides estimated metrics, you can get exact data:

### For Specific PRs

```bash
# Get full PR details
gh pr view 22141 --repo sonic-net/sonic-mgmt --json comments,reviews,labels,additions,deletions

# View all comments
gh pr view 22141 --repo sonic-net/sonic-mgmt --comments

# Check review status
gh pr status --repo sonic-net/sonic-mgmt
```

### For All PRs in Query

```bash
# Get comment counts for all PRs
gh pr list --search "org:sonic-net created:2026-01-15..2026-01-27 (DASH OR DPU)" \
  --json number,title,comments --limit 100 | \
  jq 'sort_by(.comments) | reverse | .[] | "\(.number): \(.comments) comments"'
```

## Metrics Explanation

### Comment Count
- **0-2 comments**: Simple changes, clear scope
- **3-5 comments**: Normal review discussion
- **6-10 comments**: Active discussion, iterations
- **10+ comments**: Complex topic, design challenges, or critical issues

### Review Count
- **0 reviews**: May need attention or very recent
- **1 review**: Minimum for most PRs
- **2+ reviews**: Complex changes, platform-critical code
- **3+ reviews**: Major features or cross-component changes

### Labels
- **SmartSwitch/DPU/DASH**: Topic categorization
- **high-priority**: Urgent items
- **needs-review**: Explicitly requesting review
- **approved**: Ready to merge (post-review)
- **WIP/draft**: Work in progress

## Automation

The enhanced script automatically includes PR activity when you run it:

```bash
# Generates report with PR activity metrics
./scripts/generate_weekly_review_enhanced.sh

# Standard version (without activity metrics)
./scripts/generate_weekly_review.sh
```

## Limitations

**Estimated Metrics**: 
- Comment/review counts in the report are estimated based on typical patterns
- For exact numbers, query individual PRs via GitHub API/CLI

**Why Estimates?**:
- Fetching full details for 30+ PRs is slow (API rate limits)
- Weekly reports need to generate quickly
- Estimates are based on observable patterns and provide directional guidance

**For Exact Counts**:
- Use GitHub web interface
- Use `gh pr view` for individual PRs
- Run detailed analysis scripts for specific PRs of interest

## Example Output

```markdown
## PR Activity Analysis (Engagement Metrics)

### Most Discussed PRs
| Repository | PR | Comments | Reviews | State |
| sonic-mgmt | #22141 | 15+ | 3 | Open |
| sonic-buildimage | #25178 | 12+ | 2 | Open |

### PR Activity Summary
| Metric | Value |
| Average Comments per PR | 4-5 |
| PRs with Reviews | 60-75% |
| Average Review Time | 1-2 days |

### Engagement Insights
- High-engagement: HA privatelink (15+ comments)
- Quick-merge: DASH meter fix (merged in 2 days)
```

## Tips

1. **Focus on High-Comment PRs**: These often need the most attention
2. **Track Review Coverage**: Aim for >70% PRs receiving at least 1 review
3. **Monitor Review Time**: <2 days average is healthy
4. **Identify Bottlenecks**: PRs awaiting review for 5+ days
5. **Celebrate Efficiency**: Quick-merge PRs show good process

## Future Enhancements

Potential additions:
- ✨ Actual comment counts via API (slower but more accurate)
- ✨ Review approval timeline charts
- ✨ Contributor engagement scores
- ✨ Label change history
- ✨ CI/check status tracking

## Support

For questions or issues with PR activity tracking:
- See main documentation: `scripts/README.md`
- File issues: https://github.com/sonic-net/DASH/issues

---

*Created: January 2026*
*Feature: PR Activity Analysis*
