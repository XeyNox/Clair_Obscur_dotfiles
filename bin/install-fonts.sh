#!/usr/bin/env bash
# Installe les polices d'affichage Clair Obscur depuis Google Fonts.
# Idempotent : ne retélécharge pas ce qui est déjà résolvable.
set -euo pipefail

DEST="${HOME}/.local/share/fonts"
TMP="$(mktemp -d)"
trap 'rm -rf "${TMP}"' EXIT

BASE="https://github.com/google/fonts/raw/main/ofl"

# famille -> chemin distant relatif à BASE
declare -A CHEMINS=(
    ["Cormorant Garamond"]="cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf"
    ["Cinzel"]="cinzel/Cinzel%5Bwght%5D.ttf"
)

# famille -> nom de fichier local
declare -A FICHIERS=(
    ["Cormorant Garamond"]="CormorantGaramond.ttf"
    ["Cinzel"]="Cinzel.ttf"
)

mkdir -p "${DEST}"
installe=0

familles_installees="$(fc-list : family)"
for famille in "${!CHEMINS[@]}"; do
    if grep -qiF "${famille}" <<< "${familles_installees}"; then
        echo "déjà présente : ${famille}"
        continue
    fi
    url="${BASE}/${CHEMINS[$famille]}"
    cible="${TMP}/${FICHIERS[$famille]}"
    echo "téléchargement : ${famille}"
    if ! curl -fsSL "${url}" -o "${cible}"; then
        echo "ÉCHEC du téléchargement de ${famille} depuis ${url}" >&2
        exit 1
    fi
    # Un dépôt qui répond du HTML au lieu d'une police est une panne silencieuse.
    if ! file "${cible}" | grep -qiE 'truetype|opentype|font'; then
        echo "ÉCHEC : ${cible} n'est pas une police (dépôt déplacé ?)" >&2
        exit 1
    fi
    mv "${cible}" "${DEST}/"
    installe=1
done

if [[ "${installe}" -eq 1 ]]; then
    echo "reconstruction du cache fontconfig…"
    fc-cache -f >/dev/null
fi

echec=0
for famille in "${!CHEMINS[@]}"; do
    resolu="$(fc-match "${famille}")"
    attendu="$(echo "${famille}" | tr -d ' ')"
    if echo "${resolu}" | grep -qiF "${attendu}"; then
        echo "OK  ${famille} → ${resolu}"
    else
        echo "ÉCHEC ${famille} ne se résout pas : ${resolu}" >&2
        echec=1
    fi
done
exit "${echec}"
