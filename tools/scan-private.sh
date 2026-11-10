#!/usr/bin/env bash
# scan-private.sh [extra-terms-file] — before anything goes public: find secret-shaped text, emails, phone numbers,
#   home-folder paths and private IPs in the files git would publish. An optional file of extra terms (one a line:
#   your real name, handles, domains, account ids) is checked too; keep that file OUT of the repo.
# Exit 1 on any hit. A hit you have checked and meant can be left; the scan never edits.
set -uo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
FILES=$(git ls-files -co --exclude-standard)
[ -z "$FILES" ] && { echo "scan-private: no files"; exit 0; }
PAT='(sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|gh[pousr]_[A-Za-z0-9]{36}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|/Users/[a-z][a-z0-9_-]+/|/home/[a-z][a-z0-9_-]+/|\b(10|192\.168|172\.(1[6-9]|2[0-9]|3[01]))\.[0-9]{1,3}\.[0-9]{1,3}\b|\+?[0-9]{2,3}[ -]?[0-9]{3}[ -][0-9]{3}[ -][0-9]{3,4}\b)'
ALLOW='noreply@anthropic.com|example\.(com|org)|/home/<|/Users/<'
HITS=$(echo "$FILES" | grep -v '^tools/scan-private.sh$' | tr '\n' '\0' | xargs -0 grep -nIE "$PAT" 2>/dev/null | grep -vE "$ALLOW")
if [ -n "${1:-}" ]; then
  [ -f "$1" ] || { echo "scan-private: no terms file $1" >&2; exit 2; }
  T=$(echo "$FILES" | tr '\n' '\0' | xargs -0 grep -nIiF -f <(grep -v '^\s*$' "$1") 2>/dev/null)
  HITS=$(printf "%s\n%s" "$HITS" "$T" | sed '/^$/d')
fi
if [ -n "$HITS" ]; then echo "$HITS"; echo "scan-private: $(echo "$HITS" | wc -l | tr -d ' ') hit(s)"; exit 1; fi
echo "scan-private: clean ($(echo "$FILES" | wc -l | tr -d ' ') files)"
