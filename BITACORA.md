# Bitácora - BI Créditos y Cobranzas

## Estado actual
- App Flask estructurada con Blueprints: `auth` y `main`.
- Login con `Flask-Login` y modelo `User` (SQLAlchemy).
- Conector a Odoo vía XML‑RPC (`app/services/odoo_connector.py`).
- Endpoints de API para KPIs, Top 15 y reportes (`app/main/routes.py`).
- UI base con Bootstrap y gráficos (Chart.js, ECharts, Plotly).
- Ejecución en puerto 5001 (modo debug) desde `run.py`.

## Cambios recientes
- `run.py`: forzado `host=127.0.0.1`, `port=5001`, `debug=True`.
- Rutas `main`/`auth` revisadas; vistas `dashboard.html` y `reports.html` integradas.
- Cálculo de KPIs y Top 15 encapsulados en `kpi_calculator.py`.

## Requisitos de configuración
Config esperada (por variables de `config.py`):
- `ODOO_URL` (incluye esquema, p.ej. `https://...`)
- `ODOO_DB`
- `ODOO_USERNAME`
- `ODOO_PASSWORD`
- Cadena de DB para SQLAlchemy (si se usa persistencia local)

## Cómo ejecutar (local)
1) (Opcional) Crear venv e instalar requisitos:
```
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
```
2) Ejecutar:
```
python run.py
```
Abrir `http://127.0.0.1:5001`.

## Rutas clave
- Login: `GET/POST /auth/login`
- Dashboard: `GET /dashboard` (protegida)
- Reportes: `GET /reports` (protegida)
- API KPIs: `GET /api/kpis`
- API Top15: `GET /api/reports/top15`
- Export Excel: `GET /api/reports/export.xlsx`

## Pendientes sugeridos
- Semillas de usuario admin (crear usuario por defecto si no existe).
- Manejar errores de Odoo (timeouts, auth) y cache corto.
- Variables de entorno + `.env` y `config.py` con lectura segura.
- Tests unitarios para `kpi_calculator.py`.
- Pipeline de migraciones (alembic) documentado.

## Registro de decisiones
- Puerto 5001 para convivir con otras apps locales en 5000.
- Debug activado en desarrollo; desactivar para producción.
