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

moved_any=0

while IFS= read -r -d '' entry; do
    status="${entry:0:2}"
    path="${entry:3}"

    # Zameriavame sa iba na nove neoznacene subory
    if [[ "${status}" != "??" ]]; then
        continue
    fi

    # Ignoruj podadresare a subory bez .md pripony
    lowercase_path="$(printf '%s' "${path}" | tr '[:upper:]' '[:lower:]')"
    if [[ "${path}" == */* ]] || [[ "${lowercase_path}" != *.md ]]; then
        continue
    fi

    filename="$(basename "${path}")"
    dest_path="${target_dir}/${filename}"

    if [[ -e "${dest_path}" ]]; then
        base_name="${filename%.*}"
        extension="${filename##*.}"
        suffix=1
        while [[ -e "${target_dir}/${base_name}_${suffix}.${extension}" ]]; do
            suffix=$((suffix + 1))
        done
        dest_path="${target_dir}/${base_name}_${suffix}.${extension}"
    fi

    mv "${path}" "${dest_path}"
    echo "Presunuty subor: ${path} -> sessions/${today}/$(basename "${dest_path}")"
    moved_any=1
done < <(git status --porcelain=v1 -z)

if [[ "${moved_any}" -eq 0 ]]; then
    echo "Ziadne nove .md subory v koreni repa na presun."
fi
