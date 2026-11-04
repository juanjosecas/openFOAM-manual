# Publicación automática del manual

El sitio utiliza MkDocs + Material y se publica en [GitHub Pages](https://juanjosecas.github.io/openFOAM-manual/) mediante `.github/workflows/pages.yml`.

## Configuración inicial (una sola vez)

1. Abrir **Settings → Pages → Build and deployment → Source**.
2. Cambiar **Deploy from a branch** por **GitHub Actions**. No elegir un template nuevo: el workflow ya está incluido en el repositorio.
3. Conservar el dominio predeterminado y **Enforce HTTPS**.
4. En **Settings → Actions → General**, comprobar que GitHub Actions esté habilitado. El workflow declara `contents: read`, `pages: write` e `id-token: write`.
5. Una vez incorporado el PR a `main`, abrir **Actions → Publicar manual MkDocs en GitHub Pages → Run workflow** para iniciar el primer despliegue. Los siguientes se ejecutan automáticamente con cada cambio relevante en `main`.

No se necesita token personal ni la rama `gh-pages`. El flujo oficial construye `site/`, sube el artefacto y lo publica. Se puede restringir el entorno `github-pages` a la rama `main` en Settings → Environments.

## Actualización del catálogo

`scripts/generate_case_catalog.py` lee los directorios reales de `cases/` y genera `docs/catalogo-casos.md` durante el build. El índice incluye nombre, solver declarado en `system/controlDict`, presencia de `run_docker.sh` y enlace a los archivos del caso. El índice se regenera cuando se modifica `cases/**`; no se edita manualmente.

Los casos y tutoriales siguen estando disponibles en GitHub, con enlaces desde el sitio. El catálogo **no ejecuta OpenFOAM** ni determina si un caso converge.

## Previsualización local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-docs.txt
python scripts/generate_case_catalog.py
mkdocs serve
```

Abrir http://127.0.0.1:8000/. Para detectar problemas de navegación antes de publicar: `mkdocs build --clean`.

La compilación web no ejecuta simulaciones ni genera videos. Las figuras y GIF deben producirse y agregarse explícitamente a la documentación si se quieren publicar.
