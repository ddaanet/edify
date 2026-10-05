#!/usr/bin/env bash

set -euo pipefail

job_dir="${1:-}"

if [[ -z "$job_dir" ]] || [[ $# -gt 1 ]]; then
    echo "Usage: triage-feedback.sh <job>" >&2
    exit 1
fi

# Located as in `verify-step.sh`, whose comment explains the idiom.
case "${BASH_SOURCE[0]}" in
    */*) script_dir="${BASH_SOURCE[0]%/*}" ;;
    *) script_dir="." ;;
esac

# D-90: the review gate and triage count one list, so the list comes from
# `changed-files.sh` (D-88 base, D-91 exemptions), never a second diff. Its
# exit 1 is `NO-BASE:` and its exit 2 an `ERROR:`; both stop the script with
# no log row, and `|| status=$?` keeps `set -e` from exiting silently.
status=0
changed_output=$("$script_dir/../skills/build/scripts/changed-files.sh" "$job_dir") || status=$?
if [[ $status -ne 0 ]]; then
    printf '%s\n' "$changed_output"
    echo "ERROR: changed-files.sh exited $status"
    exit 2
fi
base_line=${changed_output%%$'\n'*}
baseline_commit=${base_line#BASE: }
changed_list=""
if [[ $changed_output == *$'\n'* ]]; then
    changed_list=${changed_output#*$'\n'}
fi
# One line is one path; a path holding a newline counts as two, the residual
# bound of changed-files.sh's line format.
files_changed=0
if [[ -n $changed_list ]]; then
    files_changed=$(printf '%s\n' "$changed_list" | wc -l | tr -d ' ')
fi

# Count report files in plans/$job_dir/reports/
# Exclude pre-execution artifacts: design-review*, outline-review*, recall-*
# Exclude review-gate and closing-review reports too: review.md, review-*.md,
# final-review.md (KD-3). They record review, not execution; review_artifact
# below reports the review gate's presence separately.
# One byte per file, not `wc -l`: a newline in a filename would overcount.
reports_count=0
reports_dir="plans/$job_dir/reports"
if [[ -d "$reports_dir" ]]; then
    reports_count=$(find "$reports_dir" -maxdepth 1 -type f \
        ! -name "design-review*" ! -name "outline-review*" ! -name "recall-*" \
        ! -name "review.md" ! -name "review-*.md" ! -name "final-review.md" \
        -exec printf x \; | wc -c | tr -d ' ')
fi

# Detect behavioral code: new definitions in the committed diff from baseline
# to HEAD. Anchored after the `+` so a commented-out line does not
# match. Covers the keyword-declaration languages plus POSIX shell function
# syntax; a language that declares behaviour without one of these keywords
# (C, C++, Java method bodies) reads as "no", which under-reports rather than
# over-reports.
definition_re='^\+[[:space:]]*((export|public|private|protected|static|async|pub|final)[[:space:]]+)*'
definition_re+='(def|class|function|func|fn|impl|interface|struct|trait|enum|module)[[:space:]]'
shell_fn_re='^\+[[:space:]]*[A-Za-z_][A-Za-z0-9_]*[[:space:]]*\(\)[[:space:]]*\{'

# Captured before matching, not piped into grep: errexit is off inside an `if`
# condition, so a failing `git diff` would read as "no". --no-color and
# --no-ext-diff stop color.diff or diff.external config from rewriting the `+`
# lines the patterns anchor on.
if ! committed_diff=$(git diff --no-color --no-ext-diff "$baseline_commit" HEAD); then
    echo "ERROR: git diff failed"
    exit 2
fi
behavioral_code="no"
if grep -qE "$definition_re|$shell_fn_re" <<< "$committed_diff"; then
    behavioral_code="yes"
fi

# Compare against classification if present
verdict="no-classification"
classification_file="plans/$job_dir/classification.md"
if [[ -f "$classification_file" ]]; then
    classification=$(grep -E "(^-?[[:space:]]*\*\*Classification:\*\*|^-?[[:space:]]*Classification:)" "$classification_file" | head -1 | sed -E 's/.*:[[:space:]]*//;s/\*//g' | xargs || true)

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
