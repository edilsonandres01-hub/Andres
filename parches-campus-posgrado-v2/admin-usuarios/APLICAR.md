# `admin-usuarios/` — administrador que crea instructores, alumnos y matrículas

Tres parches sobre `main` en `6f20fc7`. El rol `admin` ya existía en la base
de datos, pero no había usuario, APIs ni pantalla. Tras aplicarlos:

1. El seed crea `admin@example.com` / `Password123` (`ON CONFLICT DO NOTHING`).
2. El administrador crea alumnos, instructores y directores de TFM.
3. Los matricula en un curso, en varios, o en **todo el Máster IEP**.
4. Un alumno o un instructor reciben 403 si llaman a esas rutas; `/admin` en
   el frontend redirige si el rol no es `admin`.

```bash
git clone https://github.com/edilsonalvarez-create/campus-posgrado-v2
cd campus-posgrado-v2
git checkout -b cursor/admin-usuarios-matricula-21ab main
git am /ruta/a/admin-usuarios/*.patch
git push -u origin cursor/admin-usuarios-matricula-21ab
```

## Los dos parches

| # | Commit | Qué hace |
|---|---|---|
| 0001 | `feat(admin)` | Seed del admin, `GET/POST /api/admin/users`, `POST /api/admin/enrollments`, `DELETE …/enrollments/:courseId`, smoke. |
| 0002 | `feat(ui)` | Página `/admin`, login que redirige al panel, botón en el dashboard. |
| 0003 | `feat(deploy)` | El backend sirve el SPA. Permite desplegar el panel sin Vercel. |

## Credenciales

| Email | Contraseña | Rol |
|---|---|---|
| `admin@example.com` | `Password123` | administrador |
| `instructor@example.com` | `Password123` | instructor (ya existía) |
| `test@example.com` | `Password123` | alumno (ya existía) |

Cambia la contraseña del admin en cuanto esté en producción. El seed **no**
resetea una contraseña ya existente (`ON CONFLICT DO NOTHING`).

Con `AUTO_SEED=sync` en Railway, el usuario admin aparece en el siguiente
arranque **después de mergear**. Hasta entonces no hay con quién entrar al panel.

## Endpoints

| Método | Ruta | Quién | Efecto |
|---|---|---|---|
| GET | `/api/admin/users?role=&q=` | admin | Lista (sin hashes) |
| POST | `/api/admin/users` | admin | Crea `student` \| `instructor` \| `director_tfm`. **No** crea `admin`. |
| GET | `/api/admin/users/:id` | admin | Detalle + matrículas |
| POST | `/api/admin/enrollments` | admin | `{ userId, courseId? \| courseIds? \| programSlug?, role? }` |
| DELETE | `/api/admin/users/:userId/enrollments/:courseId` | admin | Quita una matrícula |

`programSlug: "master-iep"` matricula en las 11 asignaturas + TFM. Si el curso
es `master-tfm` y el rol de matrícula es alumno, también abre `tfm_enrollments`.
Si el rol es `instructor`, el usuario pasa a ser `instructor_id` de ese curso
(para que aparezca en el panel de instructor).

Matricular **no** salta la cascada de prerrequisitos: el alumno queda inscrito
pero sigue sin poder avanzar la asignatura II hasta completar la I.

## Relación con los otros lotes

Independiente de `llm-nvidia/`, `plantillas/`, `dashboard/` y
`gate-prerrequisitos/`. No comparte ficheros con ellos salvo
`frontend/src/pages/Dashboard.tsx` (también lo toca `dashboard/`) y
`backend/simple-server.js` (también el gate). Aplícalo **después** de
`dashboard/` y del gate, o resuelve el conflicto en el header del Dashboard
quedándote con el botón de administración **y** el filtro de asignaturas.

Orden sugerido:

```
llm-nvidia → plantillas → dashboard → gate-prerrequisitos → admin-usuarios
```

## En producción (2026-09-10)

El panel ya está servido junto a la API:

**https://campus-posgrado-v2-production.up.railway.app**

Login: `admin@example.com` / `Password123`. El login redirige a `/admin`.

`campus-posgrado-v2.vercel.app` sigue con el bundle anterior: este agente no
puede pushear a `edilsonalvarez-create/campus-posgrado-v2`, que es lo que
construye Vercel. Hasta que esos parches entren en `main`, usa la URL de
Railway.

## Verificación

Contra PostgreSQL local, `AUTO_SEED=sync`:

- `backend/scripts/smoke.mjs` → **27 ok, 0 fallos** (15 previos + 12 de admin).
- UI: login admin → `/admin` → alta de alumno → matrícula de todo el Máster
  (12 cursos en el dashboard del alumno) → alta de instructor en Asignatura I
  → un alumno no ve «Panel de Administración» y `/admin` redirige.
