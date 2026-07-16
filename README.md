# Mis Finanzas 50/30/20

Aplicación web para organizar tus gastos con la regla **50% servicios básicos
necesarios / 30% lujos personales / 20% ahorro**, con login, tablas, gráficos
(Chart.js) e historial mensual y quincenal.

Construida en **Python + Flask**, con **arquitectura limpia** (Clean
Architecture) separada en capas independientes.

## Cómo ejecutarla

Requisitos: Python 3.10+

```bash
# 1. Crear entorno virtual (recomendado)
python3 -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la aplicación
python main.py
```

Abre tu navegador en **http://localhost:5000**, crea una cuenta y comienza a
registrar tus gastos.

La base de datos SQLite se crea automáticamente en `data/expense_manager.db`
la primera vez que ejecutas la app.

## Arquitectura

El proyecto sigue **Clean Architecture**: las dependencias siempre apuntan
hacia adentro (hacia el dominio), nunca al revés.

```
app/
├── domain/                    # Núcleo del negocio (no depende de nada externo)
│   ├── entities.py             → User, Expense, CategoryType (enum 50/30/20)
│   ├── repositories.py         → Interfaces (puertos) que la infraestructura implementa
│   └── budget_rules.py         → Lógica pura del cálculo 50/30/20
│
├── application/                # Casos de uso (orquestan el dominio)
│   ├── dto.py                  → Objetos de transferencia de datos
│   └── use_cases/
│       ├── auth_use_cases.py      → Registro, login, actualizar ingreso
│       ├── expense_use_cases.py   → Agregar, listar, eliminar gastos
│       └── report_use_cases.py    → Reporte del mes, historial mensual/quincenal
│
├── infrastructure/              # Detalles concretos (reemplazables)
│   ├── db/database.py             → Conexión y esquema SQLite
│   ├── repositories/               → Implementación SQLite de los repositorios
│   └── security/
│       ├── password_hasher.py     → Hash de contraseñas (Werkzeug)
│       └── session_auth.py        → Login por sesión + decorador @login_required
│
├── presentation/web/            # Capa de entrega (Flask)
│   ├── routes/                    → Blueprints: auth, expenses, reports
│   ├── templates/                 → Vistas Jinja2
│   └── static/                    → CSS
│
└── container.py                 # Inyección de dependencias: conecta todas las capas
```


##  Funcionalidades

- **Login y registro** de usuarios con contraseñas hasheadas (Werkzeug).
- **Configuración de ingreso mensual**, base para calcular el presupuesto.
- **Panel principal**: tarjetas de presupuesto por categoría (gastado vs.
  recomendado), barra de progreso, gráfico de dona con la distribución del
  mes y tabla de últimos gastos.
- **Gestión de gastos**: formulario para agregar gastos por categoría
  (necesidad / lujo / ahorro) y tabla completa con opción de eliminar.
- **Historial mensual**: gráfico de barras apiladas + tabla por mes.
- **Historial quincenal**: igual que el anterior, pero agrupado en quincenas
  (días 1–15 y 16–fin de mes).

## Base de datos

SQLite con dos tablas: `users` y `expenses` (con `category` = `necesidad`,
`lujo` o `ahorro`, y `expense_date` en formato `YYYY-MM-DD`).

## Notas de seguridad

- Cambia `SECRET_KEY` en `config.py` (o vía variable de entorno) antes de
  usar esto en producción.
- Las contraseñas nunca se guardan en texto plano.
- se recomienda usar el puerto de su preferencia para ejecutarla 
