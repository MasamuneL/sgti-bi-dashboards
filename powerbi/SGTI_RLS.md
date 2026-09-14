# Roles de RLS (Seguridad) para el modelo SGTI

Configuracion en **Power BI Desktop > Administrar roles** (`Modelo > Administrar roles`).
Prueba con **`Modelo > Ver como roles`**.

## Como funciona el RLS en este modelo

`USERPRINCIPALNAME()` devuelve el correo con el que el usuario inicio sesion en
Power BI Service (su UPN, ej. `usuario.ejemplo@hospital.gob.mx`). Las reglas de RLS
son expresiones DAX booleanas que filtran cada tabla; la regla puesta en una dimension
se propaga a las tablas de hechos a traves de las relaciones many-to-one del modelo
(dimension -> hechos).

Datos clave del esquema real (verificado de los Parquet):

- La unica columna con correo en el modelo es `personal_ti[correo]`
  (institucional, formato `nombre.apellido@hospital.gob.mx`).
- `coordinaciones[nombre_coordinador]` guarda **nombres de persona** (ej.
  "Dra. Nombre Ejemplo"), NO correos. No se puede comparar contra
  `USERPRINCIPALNAME()`.
- `usuarios_sistema[rol]` guarda `ADMIN` / `COORDINADOR` / `TECNICO`, pero el
  acceso de Power BI no se deriva de esta tabla: se asigna por membership al rol
  (Power BI Service > Seguridad > Agregar miembro).

> Reglas de sintaxis: en RLS no existe la funcion `RELATE()` (solo `RELATED`, y solo
> en columnas calculadas). No se puede usar `LOOKUPVALUE` mal formado ni mezclar una
> columna con un escalar en una comparacion. Cada regla usa SOLO columnas que existen.

---

## Tabla de mapeo manual `Seguridad` (requerida por el rol Coordinador)

`coordinaciones` no guarda el correo del coordinador, por lo que el vinculo
"usuario -> su coordinacion" se mantiene en una tabla manual. Creela como consulta
(no como tabla calculada, para que el hospital la pueda editar sin tocar el modelo):

1. `Obtener datos > Consulta en blanco` > `Editor avanzado`.
2. Pegue la M siguiente y nombre la consulta `Seguridad`:

```powerquery
let
    Origen = #table(
        type table [correo = text, coordinacion_id = Int64.Type],
        {
            // Reemplace estos ejemplos por el correo real de cada coordinador.
            // coordinacion_id DEBE coincidir con coordinaciones[id].
            {"direccion@hospital.gob.mx",        1},   // Direccion
            {"subdireccion.medica@hospital.gob.mx", 2}, // Subdireccion Medica
            {"subdireccion.admin@hospital.gob.mx", 3}  // Subdireccion Administrativa
        }
    )
in
    Origen
```

3. `Cerrar y aplicar`. Luego oculte `Seguridad` del reporte (clic derecho > Ocultar):
   debe existir en el modelo pero no verse en los visuales.

Relacion a crear (`Modelo > Administrar relaciones`):

| Desde | Hasta | Cardinalidad | Direccion de filtro |
|-------|-------|--------------|---------------------|
| `Seguridad[coordinacion_id]` | `coordinaciones[id]` | Muchos a uno (*:1) | Ambas (ver nota) |

> Nota sobre la direccion: para que la regla puesta en `Seguridad` filtre
> `coordinaciones` (y de ahi los hechos), la relacion debe propagar el filtro de
> `Seguridad` hacia `coordinaciones`. Use **direccion "Ambas"** en esta unica
> relacion, o bien use la Opcion B (regla sobre `coordinaciones`) que funciona con
> direccion unica y mantiene el resto del modelo con filtro unico (como en
> `SGTI_Setup_Guide.md`).

---

## 1. Rol `Admin_TI`

Sin restriccion: ve todo el modelo.

- En `Administrar roles`, crear el rol y **no agregar regla de fila a ninguna tabla**
  (o, para dejarlo explicito, poner `TRUE()` en una sola tabla, ej. `personal_ti`).

```dax
TRUE()
```

## 2. Rol `Coordinador`

Ve solo la informacion de su propia coordinacion. Usa la tabla `Seguridad`.

**Opcion A** — regla sobre `Seguridad` (requiere relacion con direccion "Ambas"):

```dax
Seguridad[correo] = USERPRINCIPALNAME()
```

**Opcion B (recomendada)** — regla sobre `coordinaciones` (funciona con direccion
unica; `LOOKUPVALUE` bien formado: devuelve un escalar y se compara contra la
columna):

```dax
coordinaciones[id] =
    LOOKUPVALUE(
        Seguridad[coordinacion_id],
        Seguridad[correo],
        USERPRINCIPALNAME()
    )
```

- La regla filtra `coordinaciones` a una sola fila y se propaga a las tablas de
  hechos via `coordinacion_id` / `departamento_id` (relaciones ya definidas en
  `SGTI_Relationships.csv`).
- Si el correo del usuario no esta en `Seguridad`, el resultado es `BLANK()` y el
  coordinador no ve nada (seguro por defecto).
- **Mantenimiento**: el hospital debe poblar `Seguridad` con el correo de cada
  coordinador y el `id` de su coordinacion. Es la unica tabla que se edita a mano.

## 3. Rol `Tecnico`

Ve solo los registros en los que figura como responsable. Regla sobre la dimension
`personal_ti`:

```dax
personal_ti[correo] = USERPRINCIPALNAME()
```

La regla filtra `personal_ti` a la fila del tecnico y se propaga a los hechos a
traves de las relaciones `personal_ti[id] -> <fact>.<fk>` definidas en el modelo:

- `historico_reubicaciones_equipos[responsable_personal_ti_id]`
- `oficios_realizados[elaborado_por_id]`, `oficios_recibidos[atendido_por_id]`
- `notas_informativas[elaboro_id]`, `minutas_circulares[elaboro_id]`
- `entregas_suministro[tecnico_personal_ti_id]`, `ingresos_suministro[quien_recibe_personal_ti_id]`
- `bitacora_equipo_portatil[personal_ti_id]`, `bitacora_omision_reportes[personal_ti_id]`
- `vacaciones_incidencias[personal_ti_id]` y `usuarios_sistema[personal_ti_id]`

> Nota: `quien_recibe_personal_ti_id` existe tambien en `entregas_suministro`, pero
> en `SGTI_Relationships.csv` solo `tecnico_personal_ti_id` esta relacionado; si se
> desea filtrar entregas por quien recibe, agregar la relacion correspondiente.

## 4. Rol `Auditor`

Ve solo `audit_log` y catalogos; sin datos operativos sensibles.

No lleva regla de fila (ver todo dentro de las tablas habilitadas):

```dax
TRUE()
```

En `Administrar roles`, dentro del rol `Auditor`, **desmarcar** (quitar acceso a) las
tablas de hechos sensibles:

- `cuentas_usuario`
- `asignaciones_licenciamiento`
- `entregas_suministro`
- `ingresos_suministro`

Dejar habilitadas: `audit_log` y los catalogos/dimensiones (coordinaciones,
personal_ti, personal_hospital, aplicativos_licencia, catalogo_suministros, etc.).

> Alternativa DAX si se prefiere un solo modelo sin quitar tablas: mantener `TRUE()`
> en todo y confiar en que el rol solo se asigne a auditores de confianza. La
> restriccion por tablas (desmarcar) es la opcion mas estricta.

## 5. Consideraciones

- El RLS se aplica en Import mode y DirectQuery; en Power BI Service se reaplica por
  usuario.
- No hay contraseñas en visuales: `password_hash` (usuarios_sistema) y
  `password_asignado_cifrado` (cuentas_usuario) se cargaron pero no se exponen.
- Pruebas: `Modelo > Ver como roles`, elegir rol y escribir un UPN de prueba
  (ej. `usuario.ejemplo@hospital.gob.mx` para Tecnico; el correo de un coordinador
  para Coordinador).
