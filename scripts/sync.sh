#!/usr/bin/env bash
# Deja tu copia local igual a GitHub despues de fusionar un pull request:
#   1. trae los cambios de GitHub y olvida las ramas remotas que ya se borraron
#   2. se pasa a main y lo actualiza con lo que aceptaste
#   3. borra las ramas locales que ya quedaron dentro de main
#
# Uso (desde cualquier carpeta dentro del repo):
#   ./scripts/sync.sh
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

# 0. No seguir si tienes cambios sin guardar en el codigo.
#    Se ignoran build/, install/ y log/, que cambian cada vez que corres colcon build.
pendientes=$(git status --porcelain -- . ':(exclude)build' ':(exclude)install' ':(exclude)log')
if [ -n "$pendientes" ]; then
    echo "Tienes cambios sin commit:"
    echo "$pendientes"
    echo
    echo "Haz commit (git add . && git commit -m \"...\") o descartalos, y vuelve a correr el script."
    exit 1
fi

# 1. Traer todo de GitHub y limpiar referencias a ramas remotas borradas.
echo "==> Trayendo cambios de GitHub..."
git fetch origin --prune

# 2. Pasarse a main y ponerlo al dia.
echo "==> Actualizando main..."
git checkout main

if git merge-base --is-ancestor main origin/main; then
    # Caso normal: main local esta atras de GitHub. Avanza sin crear commits nuevos.
    git merge --ff-only origin/main
elif git merge-base --is-ancestor origin/main main; then
    echo "Tu main local tiene commits que no estan en GitHub."
    echo "Si son tuyos y quieres subirlos: git push origin main"
    exit 1
else
    # main local y GitHub se separaron. Se guarda una copia de seguridad
    # y main queda exactamente como en GitHub.
    respaldo="respaldo-main-$(date +%Y%m%d-%H%M%S)"
    git branch "$respaldo"
    git reset --keep origin/main
    echo "Tu main local era distinto al de GitHub. Lo deje igual a GitHub"
    echo "y guarde tu version anterior en la rama $respaldo."
fi

# 3. Borrar ramas locales que ya estan dentro de main.
echo "==> Borrando ramas locales ya fusionadas..."
for rama in $(git for-each-ref --format='%(refname:short)' refs/heads/); do
    [ "$rama" = "main" ] && continue
    case "$rama" in respaldo-main-*) continue ;; esac
    if git merge-base --is-ancestor "$rama" main; then
        git branch -d "$rama"
    fi
done

echo
echo "Listo. Estas en main, igual a GitHub. Ramas locales que quedan:"
git branch
