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
today="$(date +%Y-%m-%d)"
target_dir="${session_dir}/${today}"

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
    dest_relative="sessions/${today}/${filename}"
    dest_path="${repo_root}/${dest_relative}"

    if [[ -e "${dest_path}" ]]; then
        base_name="${filename%.*}"
        extension="${filename##*.}"
        suffix=1
        while [[ -e "${target_dir}/${base_name}_${suffix}.${extension}" ]]; do
            suffix=$((suffix + 1))
        done
        dest_path="${target_dir}/${base_name}_${suffix}.${extension}"
        dest_relative="sessions/${today}/${base_name}_${suffix}.${extension}"
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
