#!/usr/bin/env bash

set -euo pipefail

# Presuva nove md reporty z korena do sessions/<datum>
# Tento skript ocakava spustenie v lubovolnom podadresari repa

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "${repo_root}" ]]; then
    echo "Tento skript musi byt spusteny v ramci git repozitara."
    exit 1
fi

cd "${repo_root}"

session_dir="${repo_root}/sessions"
today="$(date +%Y-%d-%m)"
commit_hint="${1:-}"
relative_dir="sessions/${today}"

if [[ -n "${commit_hint}" ]]; then
    # Extract first non-empty line (commit summary)
    commit_hint="$(printf '%s\n' "${commit_hint}" | awk 'NF && $0 !~ /^#/ {print; exit}')"

    # Trim leading/trailing whitespace
    commit_hint="${commit_hint#"${commit_hint%%[![:space:]]*}"}"
    commit_hint="${commit_hint%"${commit_hint##*[![:space:]]}"}"

    if [[ -n "${commit_hint}" ]]; then
        # Replace path separators and whitespace with underscores for a safe directory name
        sanitized_hint="${commit_hint//\//_}"
        sanitized_hint="${sanitized_hint//[[:space:]]/_}"

        # Collapse consecutive underscores
        sanitized_hint="$(printf '%s' "${sanitized_hint}" | tr -s '_')"

        # Remove characters outside a safe set
        sanitized_hint="$(printf '%s' "${sanitized_hint}" | sed 's/[^[:alnum:]._()%-]/_/g')"

        # Collapse again after replacement
        sanitized_hint="$(printf '%s' "${sanitized_hint}" | tr -s '_')"

        # Limit length to avoid filesystem errors
        max_len=72
        if (( ${#sanitized_hint} > max_len )); then
            sanitized_hint="${sanitized_hint:0:max_len}"
        trailing_underscores="${sanitized_hint##*[!_]}"
        sanitized_hint="${sanitized_hint%"${trailing_underscores}"}"

        leading_underscores="${sanitized_hint%%[!_]*}"
        sanitized_hint="${sanitized_hint#"${leading_underscores}"}"
        fi

        # Fallback to generic name if the sanitized result is empty
        if [[ -z "${sanitized_hint}" ]]; then
            sanitized_hint="commit"
        fi

        relative_dir="${relative_dir}/${sanitized_hint}"
    fi
fi

target_dir="${repo_root}/${relative_dir}"

mkdir -p "${target_dir}"

declare -a candidates=()

# Necommitnuté (untracked) markdown súbory v koreni
while IFS= read -r -d '' file; do
    candidates+=("${file}")
done < <(git ls-files --others --exclude-standard -z -- ':/*.md')

# Nové staged súbory (diff-filter=A) v koreni
while IFS= read -r -d '' file; do
    candidates+=("${file}")
done < <(git diff --cached --name-only --diff-filter=A -z -- ':/*.md')

if [[ ${#candidates[@]} -eq 0 ]]; then
    echo "Ziadne nove .md subory v koreni repa na presun."
    exit 0
fi

# Odstránenie duplicit a stabilné poradie
mapfile -d '' candidates < <(printf '%s\0' "${candidates[@]}" | sort -zu)

moved_any=0

for path in "${candidates[@]}"; do
    # Pre istotu ignoruj podadresare (pathspec ':/*.md' by ich nemala vrátit)
    if [[ "${path}" == */* ]]; then
        continue
    fi

    # Subor neexistuje (mohol byt medzičasom presunutý)
    if [[ ! -e "${path}" ]]; then
        continue
    fi

    lowercase_path="$(printf '%s' "${path}" | tr '[:upper:]' '[:lower:]')"
    if [[ "${lowercase_path}" != *.md ]]; then
        continue
    fi

    filename="$(basename "${path}")"
    dest_relative="${relative_dir}/${filename}"
    dest_path="${repo_root}/${dest_relative}"

    if [[ -e "${dest_path}" ]]; then
        base_name="${filename%.*}"
        extension="${filename##*.}"
        suffix=1
        while [[ -e "${target_dir}/${base_name}_${suffix}.${extension}" ]]; do
            suffix=$((suffix + 1))
        done
        dest_path="${target_dir}/${base_name}_${suffix}.${extension}"
        dest_relative="${relative_dir}/${base_name}_${suffix}.${extension}"
    fi

    if git ls-files --error-unmatch "${path}" >/dev/null 2>&1; then
        git mv "${path}" "${dest_relative}"
    else
        mv "${path}" "${dest_path}"
    fi

    echo "Presunuty subor: ${path} -> ${dest_relative}"
    moved_any=1
done

if [[ "${moved_any}" -eq 0 ]]; then
    echo "Ziadne nove .md subory v koreni repa na presun."
fi
