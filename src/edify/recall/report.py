"""Generate analysis report from recall results."""

import json

from edify.recall.recall import RecallAnalysis


def generate_markdown_report(analysis: RecallAnalysis) -> str:
    """Generate structured markdown report from recall analysis.

    Args:
        analysis: RecallAnalysis results

    Returns:
        Markdown formatted report
    """
    lines = []

    # Header
    lines.append("# Memory Index Recall Report\n")

    # Summary section
    lines.append("## Summary\n")
    lines.append(f"- Sessions analyzed: {analysis.sessions_analyzed}")
    lines.append(f"- Relevant (session, entry) pairs: {analysis.relevant_pairs_total}")
    lines.append(f"- Pairs with Read: {analysis.pairs_with_read}")
    lines.append(f"- Overall recall rate: {analysis.overall_recall_percent:.1f}%")

    # Pattern summary
    pattern_summary = analysis.pattern_summary
    direct = pattern_summary.get("direct", 0)
    search_then_read = pattern_summary.get("search_then_read", 0)
    user_directed = pattern_summary.get("user_directed", 0)
    pattern_summary.get("not_found", 0)

    total_found = direct + search_then_read + user_directed
    if total_found > 0:
        direct_pct = 100 * direct / total_found
        search_pct = 100 * search_then_read / total_found
        user_pct = 100 * user_directed / total_found

        lines.append(
            f"- Discovery patterns: {direct_pct:.0f}% direct, "
            f"{search_pct:.0f}% search-then-read, {user_pct:.0f}% user-directed"
        )

    lines.append("")

    # Per-entry analysis
    lines.append("## Per-Entry Analysis\n")
    lines.append("| Entry Key | File | Recall | Direct% | Search% | Sessions |")
    lines.append("|-----------|------|--------|---------|---------|----------|")

    lines.extend(
        f"| {r.entry_key} | {r.referenced_file} | "
        f"{r.recall_percent:.0f}% | {r.direct_percent:.0f}% | "
        f"{r.search_then_read_percent:.0f}% | "
        f"{r.total_relevant_sessions} |"
        for r in analysis.per_entry_results
    )

    lines.append("")

    # Recommendations
    lines.append("## Recommendations\n")

    high_recall = [r for r in analysis.per_entry_results if r.recall_percent >= 80]
    low_recall = [r for r in analysis.per_entry_results if r.recall_percent < 50]

    if high_recall:
        lines.append("### High-Recall Entries (effective, keep as-is)\n")
        lines.extend(
            [
                f"- **{result.entry_key}** ({result.referenced_file}): "
                f"{result.recall_percent:.0f}% recall, "
                f"{result.total_relevant_sessions} sessions"
                for result in high_recall[:5]
            ]
        )
        lines.append("")

    if low_recall:
        lines.append("### Low-Recall Entries (consider rephrase/remove)\n")
        lines.extend(
            [
                f"- **{result.entry_key}** ({result.referenced_file}): "
                f"{result.recall_percent:.0f}% recall, "
                f"{result.total_relevant_sessions} sessions"
                for result in low_recall[:5]
            ]
        )
        lines.append("")

    lines.append("### Summary Statistics\n")
    avg_recall = (
        sum(r.recall_percent for r in analysis.per_entry_results)
        / len(analysis.per_entry_results)
        if analysis.per_entry_results
        else 0
    )
    lines.append(f"- Average entry recall: {avg_recall:.1f}%")
    lines.append(f"- Total entries analyzed: {len(analysis.per_entry_results)}")
    lines.append("")

    return "\n".join(lines)


def generate_json_report(analysis: RecallAnalysis) -> str:
    """Generate JSON report from recall analysis.

    Args:
        analysis: RecallAnalysis results

    Returns:
        JSON formatted report
    """
    data = {
        "sessions_analyzed": analysis.sessions_analyzed,
        "relevant_pairs_total": analysis.relevant_pairs_total,
        "pairs_with_read": analysis.pairs_with_read,
        "overall_recall_percent": analysis.overall_recall_percent,
        "pattern_summary": analysis.pattern_summary,
        "per_entry_results": [
            {
                "entry_key": r.entry_key,
                "referenced_file": r.referenced_file,
                "total_relevant_sessions": r.total_relevant_sessions,
                "sessions_with_read": r.sessions_with_read,
                "recall_percent": r.recall_percent,
                "direct_percent": r.direct_percent,
                "search_then_read_percent": r.search_then_read_percent,
                "user_directed_percent": r.user_directed_percent,
                "pattern_counts": r.pattern_counts,
            }
            for r in analysis.per_entry_results
        ],
    }

    return json.dumps(data, indent=2)
