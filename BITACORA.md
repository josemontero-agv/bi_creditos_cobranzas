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

### 🚀 EVOLUCIÓN MAYOR - BI PROFESIONAL PARA CANAL INTERNACIONAL
**Fecha: 26/09/2025**

#### Fase 1: Backend - Filtros de Canal Internacional
- **`odoo_connector.py`** - Método `get_unpaid_invoices()`:
  - ➕ Filtro permanente: `['team_id.name', 'ilike', 'INTERNACIONAL']`
  - ➕ Campo `team_id` añadido a fields para compatibilidad
- **`odoo_connector.py`** - Método `get_report_lines()`:
  - ➕ Filtro permanente: `['move_id.team_id.name', 'ilike', 'INTERNACIONAL']`
- **Resultado**: Toda la data ahora corresponde EXCLUSIVAMENTE al canal de ventas INTERNACIONAL

#### Fase 2: Frontend - Rediseño Visual Corporativo
- **`main.css`** - Reemplazo completo con diseño profesional:
  - 🎨 Nueva paleta corporativa (--odoo-primary: #714B67, --color-success: #2ecc71, etc.)
  - ✨ Gradientes profesionales y sombras corporativas
  - 💫 Animaciones fadeInUp para tarjetas
  - 📊 Estilos específicos para BI (métricas positivas/negativas, indicadores financieros)
  - 📱 Diseño totalmente responsive
  - ♿ Mejoras de accesibilidad (focus states, contraste)
- **Inspiración**: Basado en la estética de `dashboard-ventas` con enfoque en análisis financiero

#### Fase 2.1: Mejoras Adicionales de UX/UI
- **🎯 KPIs Uniformizados**:
  - Todos los KPIs: `2.0rem` (tamaño uniforme y profesional)
  - Altura consistente: `110px` para todos los KPIs
  - Cada KPI mantiene su gradiente específico por tipo de métrica
  - Responsive escalado uniforme: 1.7rem (tablet) → 1.4rem (mobile) → 1.2rem (small)
- **🧭 Navbar Uniforme**: Estilo consistente entre dashboard y reportes
- **📝 Títulos Actualizados**: "Cuentas por Cobrar - Canal Internacional"
- **🎨 Botones Uniformes**: Color corporativo unificado en toda la aplicación
- **📊 Tabla de Reportes Mega-Optimizada** (Inspirada en sales.html):
  - `table-layout: auto` + `min-width: 2200px` para máxima información visible
  - **Columnas mega-anchas**: Nombre cuenta (250px), Cliente (280px), Referencia (200px), Vendedor (200px), Etiqueta (180px)
  - **Container ampliado**: 98% del ancho de pantalla para máximo espacio
  - **Hover interactivo**: Expansión de celdas con transform scale y box-shadow
  - **Scroll optimizado**: max-height 75vh con scroll vertical y horizontal
  - **Headers estilo Odoo**: Gradient background con text-shadow
  - **Efectos visuales**: Hover con colores diferenciados para celdas críticas

#### Fase 2.2: UI Interactiva Avanzada (Basada en sales.html)
- **🔄 Loading Indicators**: Spinner y feedback visual durante cargas
- **⚡ Optimización de Scroll**: RequestAnimationFrame para performance
- **🎯 Feedback de Botones**: Estados disabled y loading en acciones
- **📱 Navbar Ampliado**: Padding aumentado y mejor distribución del espacio
- **🚀 JavaScript Mejorado**: Async/await y manejo de errores
- **💡 UX Intuitivo**: Delays controlados y transiciones suaves

#### Fase 2.3: Header Profesional y Filtros Avanzados
- **🏢 Dashboard-Header**: Reemplazo completo del navbar con header estilo sales.html
  - Padding extra amplio: `1.8rem vertical` + `3rem horizontal`
  - Márgenes amplios: `1.5rem 2rem` para máximo uso del espacio
  - Botones con iconos Bootstrap: Dashboard, Reportes, Exportar, Salir
  - Typography Poppins para apariencia más profesional
- **📊 Filtro de Resultados**: Selector con opciones 100, 500, 1000 registros
  - Auto-recarga al cambiar número de resultados
  - Integración completa con paginación existente
  - Event listener para cambio automático
- **🖥️ Responsive Dashboard-Header**: Breakpoints específicos para tablet y mobile
  - Tablet: `1.5rem 2rem` padding
  - Mobile: Layout vertical centrado con gaps optimizados
  - Botones adaptativos con iconos escalables

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
