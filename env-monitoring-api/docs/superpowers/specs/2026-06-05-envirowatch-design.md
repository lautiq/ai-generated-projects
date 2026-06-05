# EnviroWatch — Diseño de Sistema

Web app de monitoreo ambiental IoT para laboratorios, salas técnicas y habitaciones controladas.

---

## 1. Arquitectura general

```
┌─────────────────────────────────────────────────────┐
│                   FastAPI App                       │
│                                                     │
│  ┌──────────────────┐   ┌──────────────────────┐   │
│  │   HTML Routes    │   │      API Routes       │   │
│  │  Jinja2 pages    │   │     /api/* JSON       │   │
│  │                  │   │                       │   │
│  │  GET /           │   │  POST /api/devices    │   │
│  │  GET /rooms      │   │  GET  /api/devices    │   │
│  │  GET /rooms/{id} │   │  POST /api/devices/   │   │
│  │  GET /login      │   │    {id}/measurements  │   │
│  │  GET /config     │   │  GET  /api/devices/   │   │
│  │  GET /users      │   │    {id}/measurements  │   │
│  └──────────────────┘   │  GET  /api/rooms/     │   │
│                         │    {id}/status        │   │
│                         └──────────────────────┘   │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │                Services Layer                │   │
│  │  RoomService · DeviceService ·               │   │
│  │  MeasurementService · ThresholdService ·     │   │
│  │  AlertService · UserService · AuthService    │   │
│  └──────────────────────────────────────────────┘   │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │           SQLAlchemy ORM (sync)              │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
              │
              ▼
        PostgreSQL
```

- **HTML Routes**: páginas completas renderizadas con Jinja2 + Bootstrap, consumidas por el navegador.
- **API Routes**: responden JSON puro. Usadas por los nodos sensores (POST measurements) y por el frontend vía `fetch` para cargar datos de gráficos y estado de rooms.
- **Services Layer**: contiene la lógica de negocio. Las rutas solo delegan en servicios, los servicios hablan con el ORM.
- **SQLAlchemy sync**: variante síncrona estándar (`sessionmaker`), provista a las rutas mediante una dependency de FastAPI.

---

## 2. Modelo de datos

### `rooms`
| campo | tipo | notas |
|---|---|---|
| id | integer PK | |
| name | varchar | nombre de la sala |
| location | varchar | descripción física |
| created_at | timestamp | |

### `devices`
| campo | tipo | notas |
|---|---|---|
| id | integer PK | |
| room_id | integer FK → rooms | una room tiene un device |
| name | varchar | nombre del nodo sensor |
| status | enum | `online`, `offline`, `maintenance` |
| created_at | timestamp | |

### `measurements`
| campo | tipo | notas |
|---|---|---|
| id | integer PK | |
| device_id | integer FK → devices | |
| temperature | float | en Celsius |
| humidity | float | 0–100 % |
| timestamp | timestamp | enviado por el nodo |

### `thresholds`
| campo | tipo | notas |
|---|---|---|
| id | integer PK | |
| device_id | integer FK → devices, unique | uno por device |
| temp_min | float | |
| temp_max | float | |
| humidity_min | float | |
| humidity_max | float | |

### `users`
| campo | tipo | notas |
|---|---|---|
| id | integer PK | |
| username | varchar unique | |
| password_hash | varchar | bcrypt |
| role | enum | `admin`, `user` |
| created_at | timestamp | |

**Alertas:** no se persisten. El estado (verde/amarillo/rojo) se calcula en `AlertService` al momento de servir cada página o respuesta de status.

**Retención de mediciones:** los datos históricos se mantienen en la base de datos; la UI solo consulta las últimas 24 horas por device.

**Migraciones:** gestionadas con Alembic.

---

## 3. Autenticación — dos mecanismos

### Usuarios web
- Sesión por **cookie** firmada con `SECRET_KEY`.
- `POST /login` valida credenciales → setea cookie → redirige a `/`.
- `POST /logout` destruye la cookie → redirige a `/login`.
- Dependency de FastAPI `get_current_user` protege todas las rutas HTML y las rutas API de gestión. Si no hay sesión válida, redirige a `/login`.

### Nodos sensores
- **Token estático** en header `Authorization: Bearer <SENSOR_TOKEN>`.
- `SENSOR_TOKEN` se define en variables de entorno.
- Solo los endpoints de ingesta de mediciones (`POST /api/devices/{id}/measurements`) usan este mecanismo; no tienen acceso a rutas de gestión.

---

## 4. Páginas y rutas

### Páginas HTML

| Ruta | Acceso | Descripción |
|---|---|---|
| `GET /login` | público | Formulario de login |
| `GET /` | autenticado | Dashboard: todas las rooms con su estado actual |
| `GET /rooms/{id}` | autenticado | Detalle de room: valores actuales, estado, gráfico 24h |
| `GET /config` | autenticado | Configuración de thresholds por device |
| `GET /users` | solo admin | ABM de usuarios |

### API Routes (JSON)

| Método | Ruta | Auth | Caller |
|---|---|---|---|
| `POST /api/devices` | cookie (solo admin) | web app |
| `GET /api/devices` | cookie | web app |
| `POST /api/devices/{id}/measurements` | token sensor | nodo IoT |
| `GET /api/devices/{id}/measurements` | cookie | frontend (gráfico 24h) |
| `GET /api/rooms/{id}/status` | cookie | frontend (estado actual) |

---

## 5. Capa de servicios

| Servicio | Responsabilidad |
|---|---|
| `RoomService` | crear, listar, obtener rooms |
| `DeviceService` | crear, listar, obtener, eliminar devices; actualizar `status` |
| `MeasurementService` | guardar medición, consultar últimas 24h por device; actualiza `status` del device a `online` al recibir medición |
| `ThresholdService` | leer y escribir thresholds por device |
| `AlertService` | dado última medición + thresholds, devuelve `green` / `yellow` / `red` / `unknown` |
| `UserService` | crear, listar, eliminar usuarios (solo admin); hashea con bcrypt |
| `AuthService` | validar credenciales, crear/destruir sesión |

**Lógica de estado (`AlertService`):**
- `unknown`: sin medición o sin thresholds configurados
- `green`: temperatura y humedad dentro de rango
- `yellow`: al menos un parámetro dentro del rango pero dentro del 10% del rango total desde cualquiera de sus límites (ej: rango 20–30 °C → zona amarilla entre 20–21 y 29–30)
- `red`: al menos un parámetro fuera de límite

---

## 6. Stack y dependencias

| Componente | Tecnología |
|---|---|
| Backend | FastAPI + Uvicorn |
| ORM | SQLAlchemy (sync) |
| Migraciones | Alembic |
| Base de datos | PostgreSQL |
| Templates | Jinja2 |
| CSS/UI | Bootstrap 5 (CDN) |
| Gráficos | Chart.js (CDN) |
| Auth web | Cookie de sesión firmada |
| Auth sensores | Bearer token estático |
| Hash contraseñas | bcrypt (`passlib`) |
| Validación | Pydantic v2 |
| Config | `python-dotenv` |

**Variables de entorno requeridas:**
```
DATABASE_URL=postgresql://...
SECRET_KEY=...
SENSOR_TOKEN=...
```

---

## 7. Estructura de carpetas

```
app/
├── main.py
├── db.py                  # sesión SQLAlchemy
├── models/                # modelos SQLAlchemy
│   ├── room.py
│   ├── device.py
│   ├── measurement.py
│   ├── threshold.py
│   └── user.py
├── schemas/               # esquemas Pydantic
├── routes/
│   ├── html/              # páginas Jinja2
│   └── api/               # endpoints JSON
├── services/
│   ├── room_service.py
│   ├── device_service.py
│   ├── measurement_service.py
│   ├── threshold_service.py
│   ├── alert_service.py
│   ├── user_service.py
│   └── auth_service.py
├── templates/             # archivos .html
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── room_detail.html
│   ├── config.html
│   └── users.html
└── static/                # CSS, JS propios
alembic/
docs/
```
