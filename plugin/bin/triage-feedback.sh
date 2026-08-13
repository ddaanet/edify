#!/usr/bin/env bash

set -euo pipefail

job_dir="${1:-}"
baseline_commit="${2:-}"

if [[ -z "$job_dir" ]] || [[ -z "$baseline_commit" ]]; then
    echo "Usage: triage-feedback.sh <job-dir> <baseline-commit>" >&2
    exit 1
fi

# Count files changed since baseline
files_changed=$(git diff --name-only "$baseline_commit" | wc -l | tr -d ' ')

# Count report files in plans/$job_dir/reports/
# Exclude pre-execution artifacts: design-review*, outline-review*, recall-*
reports_count=0
reports_dir="plans/$job_dir/reports"
if [[ -d "$reports_dir" ]]; then
    reports_count=$(find "$reports_dir" -maxdepth 1 -type f ! -name "design-review*" ! -name "outline-review*" ! -name "recall-*" | wc -l | tr -d ' ')
fi

# Detect behavioral code: new definitions in the diff. Anchored after the `+`
# so a commented-out line does not match. Covers the keyword-declaration
# languages plus POSIX shell function syntax; a language that declares
# behaviour without one of these keywords (C, C++, Java method bodies) reads as
# "no", which under-reports rather than over-reports.
# Not `grep -q`: `set -o pipefail` is on, and an early-exiting consumer would
# kill `git diff` with SIGPIPE and fail the pipeline.
definition_re='^\+[[:space:]]*((export|public|private|protected|static|async|pub|final)[[:space:]]+)*'
definition_re+='(def|class|function|func|fn|impl|interface|struct|trait|enum|module)[[:space:]]'
shell_fn_re='^\+[[:space:]]*[A-Za-z_][A-Za-z0-9_]*[[:space:]]*\(\)[[:space:]]*\{'

behavioral_code="no"
if git diff "$baseline_commit" | grep -E "$definition_re|$shell_fn_re" > /dev/null; then
    behavioral_code="yes"
fi

# Compare against classification if present
verdict="no-classification"
classification_file="plans/$job_dir/classification.md"
if [[ -f "$classification_file" ]]; then
    classification=$(grep -E "(^-?\s*\*\*Classification:\*\*|^-?\s*Classification:)" "$classification_file" | head -1 | sed -E 's/.*:\s*//;s/\*//g' | xargs || true)

    if [[ -z "$classification" ]]; then
        verdict="no-classification"
    elif [[ "$classification" == "Simple" ]]; then
        if [[ "$behavioral_code" == "yes" ]] || [[ "$reports_count" -gt 0 ]]; then
            verdict="underclassified"
        else
            verdict="match"
        fi
    elif [[ "$classification" == "Complex" ]]; then
        if [[ "$files_changed" -le 2 ]] && [[ "$reports_count" -eq 0 ]] && [[ "$behavioral_code" == "no" ]]; then
            verdict="overclassified"
        else
            verdict="match"
        fi
    else
        verdict="match"
    fi
fi

# Check review artifact existence (defense-in-depth for corrector gate).
# A multi-group review dispatch writes review-<type>.md per group and no
# plain review.md, so matching only review.md/review-skip.md reported "gate
# bypassed" on a run that reviewed everything.
review_artifact="none"
if [[ -d "$reports_dir" ]]; then
    if [[ -f "$reports_dir/review.md" ]]; then
        review_artifact="review"
    elif compgen -G "$reports_dir/review-*.md" > /dev/null; then
        # review-skip.md is the audited skip; any other review-<group>.md is a
        # per-group corrector report.
        if [[ -f "$reports_dir/review-skip.md" ]] &&
            [[ $(find "$reports_dir" -maxdepth 1 -name 'review-*.md' | wc -l) -eq 1 ]]; then
            review_artifact="skip"
        else
            review_artifact="review"
        fi
    fi
fi

# Output structure
echo "## Evidence"
echo "- Files changed: $files_changed"
echo "- Reports: $reports_count"
echo "- Behavioral code: $behavioral_code"
echo "- Review artifact: $review_artifact"
echo ""
echo "## Verdict"
echo "$verdict"

if [[ "$verdict" == "underclassified" ]] || [[ "$verdict" == "overclassified" ]]; then
    echo ""
    echo "Triage: predicted $classification, evidence suggests $verdict (files=$files_changed, reports=$reports_count, code=$behavioral_code)"
fi

if [[ "$review_artifact" == "none" ]]; then
    echo ""
    echo "WARNING: No corrector report — review gate may have been bypassed"
fi

# Append to triage-feedback-log.md (only if verdict is not no-classification)
if [[ "$verdict" != "no-classification" ]]; then
    log_dir="plans/reports"
    mkdir -p "$log_dir"
    log_file="$log_dir/triage-feedback-log.md"

    if [[ ! -f "$log_file" ]]; then
        echo "| Date | Job | Predicted | Files Changed | Reports | Behavioral Code | Verdict |" > "$log_file"
        echo "|---|---|---|---|---|---|---|" >> "$log_file"
    fi

    log_date=$(date -u +%Y-%m-%d)
    echo "| $log_date | $job_dir | $classification | $files_changed | $reports_count | $behavioral_code | $verdict |" >> "$log_file"
fi

exit 0
