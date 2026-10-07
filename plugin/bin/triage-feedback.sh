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
# Absolute before the change of directory below, which would break a relative
# path.
script_dir=$(cd "$script_dir" && pwd)

# D-90: every pathspec, `classification.md`, `reports_dir` and the log path are
# root-relative, as `changed-files.sh` already is (it reads the same
# `git rev-parse --show-toplevel`), so a run from any directory in the work tree
# measures and logs what a run from the root does.
repo_root=$(git rev-parse --show-toplevel)
cd "$repo_root"

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

# D-90: Reports counts what the run committed beyond the one report every
# item leaves: the paths directly under `plans/<job>/reports/` that
# `<base> HEAD` adds, minus the per-item `item-<N>-<M>.md` and the
# review-gate reports (`review.md`, `review-*.md`, `final-review.md`,
# `tdd-audit.md`). Slice, refactor and phase-boundary reports count;
# planning reports committed before the base fall outside the range.
# `review_artifact` below reports the review gate's presence separately.
# `:(glob)` keeps `*` inside one path component, so a report below
# `reports/` is not "directly under" it; `--no-renames` reads a rename as an
# addition. Paths come NUL-delimited, as in `changed-files.sh`: without
# `-z`, git C-quotes a name holding `"`, `\` or a control byte whatever
# `core.quotePath` says, and the quoted name escapes the exclusions. One `x`
# per counted report, then `wc -c`; with `pipefail` a failing `git diff`
# fails the assignment, never reading as "none".
reports_dir="plans/$job_dir/reports"
item_report_re='^item-[0-9]+-[0-9]+\.md$'
if ! reports_count=$(git diff --name-only --no-renames -z --diff-filter=A \
    "$baseline_commit" HEAD -- ":(glob)$reports_dir/*" |
    while IFS= read -r -d '' report_path; do
        report_name=${report_path##*/}
        if [[ $report_name =~ $item_report_re ]]; then
            continue
        fi
        case "$report_name" in
            (review.md | review-*.md | final-review.md | tdd-audit.md)
                continue ;;
        esac
        printf x
    done | wc -c | tr -d ' '); then
    echo "ERROR: git diff failed"
    exit 2
fi

# Detect behavioral code: new definitions in the committed diff from baseline
# to HEAD, limited to the paths of the changed-files list, so exempt paths and
# the job's own reports never count. Anchored after the `+` so a commented-out
# line does not match. Covers the keyword-declaration languages plus POSIX
# shell function syntax; a language that declares behaviour without one of
# these keywords (C, C++, Java method bodies) reads as "no", which
# under-reports rather than over-reports.
definition_re='^\+[[:space:]]*((export|public|private|protected|static|async|pub|final)[[:space:]]+)*'
definition_re+='(def|class|function|func|fn|impl|interface|struct|trait|enum|module)[[:space:]]'
shell_fn_re='^\+[[:space:]]*[A-Za-z_][A-Za-z0-9_]*[[:space:]]*\(\)[[:space:]]*\{'

# An empty list reads "no" and runs no diff: an empty pathspec diffs
# everything. `:(literal)` keeps a glob character in a name from matching other
# paths. One line is one path; a path holding a newline prints as two list
# lines, which match nothing unless a half names another path the range
# changes: the residual bound of changed-files.sh's line format. Bash 3.2 has
# no `mapfile`, and a here-string would hit the temp-file failure described
# below, so the list is split by parameter expansion.
behavioral_code="no"
if [[ -n $changed_list ]]; then
    list_pathspecs=()
    list_rest=$changed_list
    while [[ -n $list_rest ]]; do
        list_pathspecs+=(":(literal)${list_rest%%$'\n'*}")
        if [[ $list_rest == *$'\n'* ]]; then
            list_rest=${list_rest#*$'\n'}
        else
            list_rest=""
        fi
    done
    # Captured before matching, not piped into grep: errexit is off inside an
    # `if` condition, so a failing `git diff` would read as "no". --no-color and
    # --no-ext-diff stop color.diff or diff.external config from rewriting the
    # `+` lines the patterns anchor on; --no-renames lists a rename's target as
    # an addition, as the list does.
    if ! committed_diff=$(git diff --no-color --no-ext-diff --no-renames \
        "$baseline_commit" HEAD -- "${list_pathspecs[@]}"); then
        echo "ERROR: git diff failed"
        exit 2
    fi
    # A pipe, not a here-string: bash writes a here-string to a temp file, and
    # failing to create it also exits 1, which would read as "no". grep's own
    # status decides, from PIPESTATUS: `-q` stops at the first match, so on a
    # diff larger than the pipe buffer `printf` dies of SIGPIPE, or exits 1
    # where SIGPIPE is ignored, and under `pipefail` the pipeline's status
    # would read an early match as a failure or as "no". The diff is already
    # captured, so `printf` has no other failure to report. Only grep's exit 1
    # is a result; anything above is a failure.
    grep_status=0
    printf '%s\n' "$committed_diff" | grep -qE "$definition_re|$shell_fn_re" ||
        grep_status=${PIPESTATUS[1]}
    case $grep_status in
        0) behavioral_code="yes" ;;
        1) ;;
        *)
            echo "ERROR: grep failed"
            exit 2
            ;;
    esac
fi

# Compare against classification if present
verdict="no-classification"
unrecognised_label=""
classification_file="plans/$job_dir/classification.md"
if [[ -f "$classification_file" ]]; then
    # grep's exit 1 is "no Classification line", a result; above that is a
    # failure. The first match is cut by parameter expansion, not `head`, which
    # would SIGPIPE grep under `pipefail`. `sed` strips the prefix grep matched
    # and trims, so a colon, `*` or apostrophe in the label reads literally.
    label_prefix_re='^-?[[:space:]]*(\*\*Classification:\*\*|Classification:)'
    classification=""
    grep_status=0
    label_lines=$(grep -E "$label_prefix_re" "$classification_file") || grep_status=$?
    case $grep_status in
        0)
            if ! classification=$(printf '%s\n' "${label_lines%%$'\n'*}" |
                sed -E "s/${label_prefix_re}[[:space:]]*//;s/[[:space:]]+\$//"); then
                echo "ERROR: sed failed"
                exit 2
            fi
            ;;
        1) ;;
        *)
            echo "ERROR: grep failed"
            exit 2
            ;;
    esac

    if [[ -z "$classification" ]]; then
        verdict="no-classification"
    elif [[ "$classification" != "Simple" && "$classification" != "Moderate" &&
        "$classification" != "Complex" && "$classification" != "Defect" ]]; then
        unrecognised_label=$classification
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

if [[ -n "$unrecognised_label" ]]; then
    echo ""
    printf 'unrecognised classification: %s\n' "$unrecognised_label"
fi

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
    # A failed write would exit 1 under `set -e`, the usage error's code.
    log_dir="plans/reports"
    log_file="$log_dir/triage-feedback-log.md"
    mkdir -p "$log_dir" || {
        echo "ERROR: cannot write $log_file"
        exit 2
    }

    if [[ ! -f "$log_file" ]]; then
        printf '%s\n' \
            "| Date | Job | Predicted | Files Changed | Reports | Behavioral Code | Verdict |" \
            "|---|---|---|---|---|---|---|" > "$log_file" || {
            echo "ERROR: cannot write $log_file"
            exit 2
        }
    fi

    # One row per evidence: the append is skipped when a row equals the new one
    # in every column but the date. Rows are compared whole, past the date
    # column, by parameter expansion: no grep, so no substring match and no
    # exit status to mistake for a result. A last line with no newline is
    # still compared, and `log_lead` puts the new row on a line of its own.
    # The braces matter: when a compound command's own redirection fails,
    # bash skips the `!`, so an unreadable log would fall through to a blind
    # append.
    new_undated="$job_dir | $classification | $files_changed | $reports_count | $behavioral_code | $verdict |"
    row_seen="no"
    log_lead=""
    if ! {
        while IFS= read -r log_row || { [[ -n $log_row ]] && log_lead=$'\n'; }; do
            log_rest=${log_row#"| "}
            if [[ ${log_rest#* | } == "$new_undated" ]]; then
                row_seen="yes"
                break
            fi
        done < "$log_file"
    }; then
        echo "ERROR: cannot read $log_file"
        exit 2
    fi

    if [[ $row_seen == "no" ]]; then
        log_date=$(date -u +%Y-%m-%d)
        printf '%s| %s | %s\n' "$log_lead" "$log_date" "$new_undated" >> "$log_file" || {
            echo "ERROR: cannot write $log_file"
            exit 2
        }
    fi
fi

exit 0
