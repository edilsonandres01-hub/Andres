# Inventario de módulos — HORUS HEALTH Versión 2.0

Respuesta al numeral 4 de la solicitud de información y documentación inicial (Mateus Carlier S.A.S.): identificación mediante título de los **54 módulos** de HORUS HEALTH Versión 2.0 (SUIM-HORUS).

| Campo | Valor |
|---|---|
| Software | HORUS HEALTH Versión 2.0 (SUIM-HORUS) |
| URL de producción | https://horus2.horus-health.com/ |
| Titular | SUMIMEDICAL S.A.S. |
| Fecha de levantamiento | 4 de septiembre de 2026 |
| Conteo | 54 títulos (47 de menú principal + 7 áreas funcionales con rutas propias) |

## Metodología

El inventario se tomó del menú maestro de la aplicación de producción (definición de navegación Nuxt/Vue con la que se renderiza el menú lateral y se aplican permisos). El menú declara 49 entradas de primer nivel; *Gestión Riesgo* y *Fias* están duplicados, por lo que hay **47 títulos únicos de menú**. Se adicionan **7 módulos funcionales** con rutas propias para completar **54 títulos**.

## Listado de los 54 módulos

| # | Título del módulo | Origen |
|---:|---|---|
| 01 | Inicio | Menú principal |
| 02 | Agendamiento | Menú principal |
| 03 | Citas | Menú principal |
| 04 | Gestión de sucesos | Menú principal |
| 05 | Aseguramiento | Menú principal |
| 06 | Contratos | Menú principal |
| 07 | Farmacia | Menú principal |
| 08 | Panel Médico | Menú principal |
| 09 | Gestión de Red | Menú principal |
| 10 | Transcripciones | Menú principal |
| 11 | SISCAC | Menú principal |
| 12 | Históricos | Menú principal |
| 13 | Prestadores | Menú principal |
| 14 | Caracterización | Menú principal |
| 15 | Gestión Riesgo | Menú principal |
| 16 | Empalme | Menú principal |
| 17 | Audimedf | Menú principal |
| 18 | Mesa ayuda | Menú principal |
| 19 | Oncologia | Menú principal |
| 20 | Centro Regulador | Menú principal |
| 21 | Rips | Menú principal |
| 22 | RIAS | Menú principal |
| 23 | Fias | Menú principal |
| 24 | Cuentas medicas | Menú principal |
| 25 | Acción Constitucional | Menú principal |
| 26 | Telesalud | Menú principal |
| 27 | Salud Ocupacional | Menú principal |
| 28 | Domiciliaria | Menú principal |
| 29 | PQRS | Menú principal |
| 30 | Talento Humano | Menú principal |
| 31 | Solicitudes | Menú principal |
| 32 | Estadísticas | Menú principal |
| 33 | Indicadores | Menú principal |
| 34 | Turno | Menú principal |
| 35 | Autogestión | Menú principal |
| 36 | Libre elección | Menú principal |
| 37 | Sarlaft | Menú principal |
| 38 | Evaluación Médica Ocupacional | Menú principal |
| 39 | SST | Menú principal |
| 40 | Reportes | Menú principal |
| 41 | Reportes - Prestadores | Menú principal |
| 42 | Desarrollo | Menú principal |
| 43 | API | Menú principal |
| 44 | Log Interoperabilidad | Menú principal |
| 45 | Interoperabilidad - Historias Clinicas | Menú principal |
| 46 | Gestion Documental | Menú principal |
| 47 | Admin | Menú principal |
| 48 | Historia Clínica | Área funcional con rutas propias |
| 49 | Consentimiento Informado | Área funcional con rutas propias |
| 50 | Certificados de Aptitud Laboral | Área funcional con rutas propias |
| 51 | Cuadro de Turnos | Área funcional con rutas propias |
| 52 | Gestión del Conocimiento | Área funcional con rutas propias |
| 53 | Medicina Laboral | Área funcional con rutas propias |
| 54 | Códigos SUMI | Área funcional con rutas propias |

## Detalle por módulo (submódulos)

### 01. Inicio

Punto de entrada del sistema: manuales de usuario y gestión de contenido institucional.

- **Manuales** `/inicio/manual`
- **Gestión de Contenido** `/inicio/gestionContenido`

### 02. Agendamiento

Programación de agenda médica, histórico de cambios y parametrización de agenda.

- **Agendar** `/agendamiento/medico`
- **Programación** `/agendamiento/registro`
- **Histórico cambios agenda** `/agendamiento/historicoCambios`
- **Parametrización** `/agendamiento/parametrizacion`

### 03. Citas

Agendamiento de citas y su parametrización operativa.

- **Agendar** `/cita/agendamiento`
- **Parametrización** `/cita/parametrizacion`

### 04. Gestión de sucesos

Análisis, informe y parametrización de eventos / sucesos asistenciales.

- **Gestión** `/evento/analisisEvento`
- **Informe** `/evento/informeEvento`
- **Parametrización** `/evento/parametrizacion`

### 05. Aseguramiento

Verificación de derechos, portabilidad, gestor de afiliados, barreras de acceso y parametrización del aseguramiento.

- **Verificación** `/aseguramiento/verificacion`
- **Traslados (Portabilidad)** `/aseguramiento/portabilidad`
- **Gestor de Afiliados** `/aseguramiento/gestorAfiliados`
- **Barreras de acceso** `/aseguramiento/barreraAcceso`
- **Parametrización** `/aseguramiento/parametrizacionAseguramiento`

### 06. Contratos

Administración de contratos, familias, prestadores y servicios (CUPS).

- **Contratos** `/contrato/contratos`
- **Familias** `/contrato/familia`
- **Prestadores** `/contrato/prestador`
- **Servicios** `/contrato/cups`

### 07. Farmacia

Dispensación, inventario, kardex, bodegas, farmacovigilancia, contratos de medicamentos y reposición.

- **Reposición inventario** `/farmacia/reposicionInventario`
- **Dispensación** `/farmacia/dispensacion`
- **Panel de Seguimiento** `/historico/medicamentosParciales`
- **Contratos** `/farmacia/contratos`
- **Solicitudes Bodega** `/farmacia/solicitudesBodegas`
- **Auditoria Solicitudes** `/farmacia/auditoriaSolicitudes`
- **Movimiento Solicitudes** `/farmacia/movimientosSolicitudes`
- **Existencia** `/farmacia/existencias`
- **Kardex** `/farmacia/kardex`
- **Dispensado** `/farmacia/dispensado`
- **Codigos lasa** `/farmacia/codigosLasa`
- **Inventario** `/farmacia/inventario`
- **Farmacovigilancia** `/farmacia/Farmacovigilancia`
- **Bodega medicamentos** `/farmacia/bodegaMedicamentos`
- **Bodegas** `/farmacia/bodegas`
- **Productos** `/codigosSumi/codigoSumi`
- **Parametrizacion** `/farmacia/parametrizacionProgramas`
- **Parametrizacion Contratos Medicamentos** `/farmacia/parametrizacionContratoMedicamentos`

### 08. Panel Médico

Atención médica, asistencia educativa, demanda inducida y parametrización del acto médico.

- **Atención médica** `/panelMedico/atencion`
- **Asistencia educativa** `/panelMedico/asistenciaEducativa`
- **Demanda inducida** `/panelMedico/demandaInducida`
- **Parametrizacion** `/panelMedico/parametrizacion`

### 09. Gestión de Red

Autorización de medicamentos, servicios, cirugía, oncología y otros servicios de la red.

- **Medicamentos** `/autorizacion/medicamentos`
- **Servicios** `/autorizacion/servicios`
- **Cirugía** `/autorizacion/serviciosCirugia`
- **Oncología** `/autorizacion/oncologia`
- **Otros Servicios** `/autorizacion/otrosServicios`

### 10. Transcripciones

Transcripción de órdenes externas e internas.

- **Externa** `/transcripcion/transcripcion`
- **Interna** `/transcripcion/transcripcionInterna`

### 11. SISCAC

Cargue, auditoría y parametrización SISCAC (resolución de calidad / indicadores).

- **Cargues** `/siscac/cargue`
- **Auditoria** `/siscac/auditoria`
- **Parametrización** `/siscac/parametrizacion2`

### 12. Históricos

Consulta histórica de atenciones, historias clínicas interoperables, órdenes, incapacidades y laboratorios.

- **Consultas** `/historico/consultas`
- **Interoperabilidad Historias CLinicas** `/historico/interoperabilidadHc`
- **Repositorio Historias** `/historico/repositorio`
- **Ordenes** `/historico/historico-ordenes`
- **Incapacidades** `/historico/incapacidades`
- **Laboratorios** `/historico/laboratorios`

### 13. Prestadores

Gestión de prestadores, toma de procedimientos y dispensación de medicamentos en red.

- **Prestadores** `/prestadores/prestadores`
- **Toma Procedimientos** `/prestadores/tomaProcedimientos`
- **Dispensación Medicamentos** `/prestadores/historicoMedicamentos`

### 14. Caracterización

Registro de caracterización de afiliados, ECIS y marcación masiva.

- **Registro** `/Caracterizacion/caracterizacion`
- **ECIS** `/Caracterizacion/caracterizacionEcis`
- **Marcación Masiva Afiliados** `/rias/marcacionMasivaAfiliados`

### 15. Gestión Riesgo

Asistencia educativa, demanda inducida y administración de demanda inducida en gestión del riesgo.

- **Asistencia Educativa** `/gestionRiesgo/asistenciaPrincipal`
- **Demanda Inducida** `/demandaInducida/demandaInducida`
- **Admin Demanda Inducida** `/demandaInducida/administracionDemandaInducida`

### 16. Empalme

Registro de empalme de información / continuidad operativa.

- **Registro** `/empalme/RegistroEmpalme`

### 17. Audimedf

Auditoría médica concurrente: ingreso, enfermería, medicina general, seguimiento y alta.

- **Ingreso Manual** `/concurrencia/ingreso`
- **Aux de auditoria concurrente** `/concurrencia/auxiliarEnfermeria`
- **Enfermeria concurrente** `/concurrencia/enfermeria`
- **Medico Concurrente** `/concurrencia/medicinaGeneral`
- **Seguimiento** `/concurrencia/seguimiento`
- **Alta** `/concurrencia/alta`
- **Parametrizacion** `/concurrencia/parametrizacion`

### 18. Mesa ayuda

Mesa de ayuda institucional: radicación, asignación, solución y parametrización de tickets.

- **Radicar solicitud** `/mesaAyuda/radicarSolicitud`
- **Mis solicitudes** `/mesaAyuda/misSolicitudes`
- **Mis asignadas** `/mesaAyuda/misAsignadas`
- **Solucionadas** `/mesaAyuda/solucionadas`
- **Parametrización** `/mesaAyuda/parametrizacion`

### 19. Oncologia

Gestión oncológica: procedimientos, resultados, prestadores, esquemas y enfermería.

- **Toma Procedimientos** `/oncologia/tomaProcedimientos`
- **Resultados Oncologícos** `/oncologia/solicitudesPrestadores`
- **Prestadores** `/oncologia/prestadores`
- **Esquemas** `/oncologia/esquemas`
- **Enfermeria** `/oncologia/enfermeriaOncologia`

### 20. Centro Regulador

Referencia y contrarreferencia: registro, seguimientos, procesado y tarifas vs prestadores.

- **Registro** `/referencia/registro`
- **Seguimientos** `/referencia/seguimientos`
- **Procesado** `/referencia/procesado`
- **Tarifa VS Prestadores** `/referencia/tarifaVsPrestadores`
- **Logs Concurrencia** `/referencia/logs`

### 21. Rips

RIPS: banco de proveedores, radicación JSON (Res. 2275/2023), validación (Res. 3374/2000) y soportes.

- **Banco de proveedores** `/rips/banco`
- **Radicacion (JSON)** `/rips/radicacion`
- **Validación rips** `/rips/validadorRips`
- **Técnicos de radicación** `/rips/TecnicosRadicacion`
- **Validación de soportes administrativos** `/rips/validacionSoportes`
- **Recepción** `/rips/radicados`
- **Registro de cargue 3374** `/rips/registroCargues`
- **Registro de cargue 2275** `/rips/registroCarguesJson`

### 22. RIAS

Rutas Integrales de Atención en Salud: rutas, seguimiento y cargues masivos.

- **Rutas** `/rias/rutasRias`
- **Seguimiento** `/rias/seguimientoRias`
- **Cargues masivos** `/rias/carguesMasivosRias`
- **Marcación Masiva Afiliados** `/rias/marcacionMasivaAfiliados`

### 23. Fias

Descarga de archivos FIAS.

- **Descarga** `/fias/descargaFias`

### 24. Cuentas medicas

Auditoría de cuentas médicas: asignación de facturas, auditoría, informes y reportes a prestadores.

- **Administración** `/cuentasMedicas/adminCuentasMedicas`
- **Facturas pendientes de asignar** `/cuentasMedicas/facturasPendientes`
- **Reasignacion de Facturas** `/cuentasMedicas/reasignarFacturas`
- **Auditoria** `/cuentasMedicas/auditoria`
- **Reporte auditores** `/cuentasMedicas/reporteAuditores`
- **Informe** `/cuentasMedicas/informeCuentasMedicas`
- **Informe prestador** `/cuentasMedicas/informePrestador`

### 25. Acción Constitucional

Gestión de tutelas / acciones constitucionales: asignación, gestión y parametrización.

- **Asignada** `/tutela/tutelaAsignada`
- **Gestión** `/tutela/tutelaGestion`
- **Parametrización** `/tutela/tutelaParametrizacion`

### 26. Telesalud

Creación, pendientes, juntas de profesionales y cierre de atenciones de telesalud.

- **Parametrización** `/telesalud/parametrizacion`
- **Crear Telesalud** `/telesalud/crearTelesalud`
- **Pendientes** `/telesalud/pendientes`
- **Junta profesionales** `/telesalud/juntaProfesionales`
- **Solucionados** `/telesalud/solucionados`

### 27. Salud Ocupacional

Histórico de salud ocupacional.

- **Histórico** `/saludOcupacional/historicoOcupacional`

### 28. Domiciliaria

Ingreso y censo de atención domiciliaria.

- **Ingreso** `/domiciliaria/ingresoDomiciliario`
- **Censo Domiciliario** `/domiciliaria/censoDomiciliario`

### 29. PQRS

PQRSF: formulario, gestión interna/externa, central de PQRS y parametrización.

- **Formulario** `/gestionPqrsf/formulario`
- **Gestión** `/gestionPqrsf/gestion/gestion`
- **Gestión Interna** `/gestionPqrsf/gestionInterna/gestionInterna`
- **Gestión Externa** `/gestionPqrsf/gestionExterna/gestionExterna`
- **Central PQRS** `/gestionPqrsf/centralPqrf/centralPqrf`
- **Parametrización** `/gestionPqrsf/parametrizacion`

### 30. Talento Humano

Empleados, cierre de mes, inducción, incidentes, evaluación de desempeño, beneficios y parametrización.

- **Empleados** `/talentoHumano/empleados`
- **Cierre de mes** `/talentoHumano/cierreMes`
- **Inducción específica** `/talentoHumano/induccionEspecifica`
- **Incidentes laborales** `/talentoHumano/incidentes`
- **Evaluación desempeño** `/talentoHumano/evaluacionDesempeno`
- **Plan seguimiento individual** `/talentoHumano/planSeguimiento`
- **Beneficios laborales** `/talentoHumano/beneficios`
- **Parametrización** `/talentoHumano/parametrizacion`

### 31. Solicitudes

Radicación, gestión, asignación, administración e informe de solicitudes.

- **Radicar** `/solicitudes/radicarSolicitud`
- **Gestión** `/solicitudes/gestion`
- **Asignadas** `/solicitudes/asignadas`
- **Admin** `/solicitudes/Admin`
- **Informe** `/solicitudes/informe`

### 32. Estadísticas

Estadísticas operativas, parametrización y usuarios en línea.

- **Estadisticas** `/estadistica/estadistica`
- **Parametrización** `/estadistica/parametrizacion`
- **Usuario en línea** `/estadistica/usuarios-en-linea`

### 33. Indicadores

Tablero de indicadores de gestión.

- **Indicadores** `/indicador/indicadores`

### 34. Turno

Gestión de turnos, tablero, llamado, taquilla y áreas clínicas.

- **Turnos** `/turno/listar`
- **Tablero** `/turno/tablero`
- **Llamado** `/turno/llamado`
- **Taquilla** `/taquilla/taquilla`
- **Areas clinica** `/areaClinica/areaClinica`

### 35. Autogestión

Portal del afiliado: certificado de afiliación, solicitudes, órdenes, PQRSDF y agendamiento de citas.

- **Certificado de Afiliación** `/autogestion/certificadoAfiliacion`
- **Solicitudes** `/autogestion/radicarAutogestion`
- **Órdenes** `/autogestion/ordenesAutogestion`
- **PQRSDF** `/autogestion/pqrsfAutogestion`
- **Agendamiento de citas** `/autogestion/citasAutogestion`

### 36. Libre elección

Formulario de libre elección de IPS.

- **Formulario Libre Elección** `/autogestion/ips-seleccionada`

### 37. Sarlaft

Formulario y revisión SARLAFT (prevención de lavado de activos y financiación del terrorismo).

- **Formulario** `/sarlaft/formularioSarlaft`
- **Revisión sarlaft** `/sarlaft/revisionSarlaft`

### 38. Evaluación Médica Ocupacional

Solicitudes EMO, gestión y parametrización de sedes ocupacionales.

- **Solicitudes EMO** `/medicinaLaboral/emo/formularioSolicitudes`
- **Gestión Solicitudes EMO** `/medicinaLaboral/emo/gestionSolicitudes`
- **Parametrización Sedes EMO** `/medicinaLaboral/emo/parametrizacionSedesOcupacionales`

### 39. SST

Seguridad y Salud en el Trabajo: FURAT, FUREL, investigaciones, determinación de origen y junta regional.

- **FURAT** `/furat/registro`
- **FUREL** `/furel/registroFurel`
- **Gestión Investigaciones** `/Sst/historicos`
- **Firma Investigaciones** `/sst/firmaInvestigaciones`
- **Determinacion Origen** `/Sst/determinacion-origen`
- **Junta Regional de Calificacion** `/sst/junta-regional-calificacion`
- **Informe** `/furat/reporte`
- **Parametrizacion ETC** `/furat/parametrizacion`
- **Parametrizacion Adjuntos** `/Sst/parametrizacionAdjuntos`

### 40. Reportes

Generación de reportes, mis reportes, parametrización y vademécum.

- **Generación de Reportes** `/reportes/reportes`
- **Mis Reportes** `/reportes/mis-reportes`
- **Parametrización** `/reportes/parametrizacion`
- **VADEMECUM** `/farmacia/vademecum`

### 41. Reportes - Prestadores

Reportes específicos para prestadores (formato 202).

- **202** `/reportesPrestadores/reporte202`

### 42. Desarrollo

Catálogo de permisos y estados del sistema (herramientas de desarrollo / configuración avanzada).

- **Permisos** `/desarrollo/permiso`
- **Estados** `/desarrollo/estado`

### 43. API

Clientes, rutas, auditoría y configuración de interoperabilidad vía API.

- **Clientes** `/api/clientes`
- **Rutas** `/api/rutas`
- **Auditoría - Interoperabilidad** `/api/auditoriaInteroperabilidad`
- **Configuración - Interoperabilidad** `/api/configuracionInteroperabilidad`
- **Logs** `/api/logsInteroperabilidades`

### 44. Log Interoperabilidad

Auditoría, notificación de despacho y manuales de interoperabilidad.

- **Auditoria** `/logInteroperabilidad/auditoriaInteroperabilidad`
- **Notificacion de Despacho** `/logInteroperabilidad/notificacionDespacho`
- **Manuales** `/logInteroperabilidad/manuales`

### 45. Interoperabilidad - Historias Clinicas

Registro de clientes e historias clínicas interoperables.

- **Registrar - Clientes** `/logInteroperabilidad/registroInteroperabilidades`
- **Historias Clinicas - Interoperabilidad** `/Interoperabilidad/historiasClinicasInteroperabilidad`

### 46. Gestion Documental

Repositorio documental / intranet.

- **Gestion Documental** `/intranet/documentos`

### 47. Admin

Administración general: roles, usuarios, sedes, entidades, auditorías, notificaciones y parametrizaciones.

- **Auditoria** `/admin/auditoria`
- **Auditoria Logueos** `/admin/auditoria-logueos`
- **Central Notificaciones** `/admin/central-notificaciones`
- **Roles** `/admin/roles`
- **Cargos** `/admin/cargos`
- **Usuarios** `/admin/usuarios`
- **Especialidades** `/admin/especialidades`
- **Entidades** `/admin/entidades`
- **Citas** `/admin/citas`
- **Sedes** `/admin/sedes`
- **Colegios** `/admin/colegios`
- **Tipo de test** `/admin/tipoTest`
- **Consentimientos informados** `/admin/consentimientosInformados`
- **Parametrizacion cups rips** `/admin/parametrizacionCupRips`
- **Parametrizacion remision a programas** `/admin/parametrizacionProgramas`
- **Empresas** `/admin/empresas`
- **Envio - Correos** `/admin/envioCorreos`

## Módulos funcionales adicionales (48–54)

### 48. Historia Clínica

Parametrización de estructura de historia clínica (categorías, tipos de campo y campos). Rutas /historia/*.

- **Campo historia** `/historia/campoHistoria`
- **Categoría** `/historia/categoria`
- **Tipo de campo** `/historia/tipoCampo`

### 49. Consentimiento Informado

Registro y consulta de consentimientos informados. Ruta /consentimiento/consentimientoInformado y administración en Admin.

- **Consentimiento informado** `/consentimiento/consentimientoInformado`
- **Histórico de consentimientos** `/historico/consentimientos`

### 50. Certificados de Aptitud Laboral

Emisión y gestión de certificados de aptitud laboral. Ruta /certificadosAptitudLaboral/certificadosAptitudLaboral.

- **Certificados de aptitud laboral** `/certificadosAptitudLaboral/certificadosAptitudLaboral`

### 51. Cuadro de Turnos

Programación mensual de turnos clínicos. Ruta /cuadroTurno/programacionMensual.

- **Programación mensual** `/cuadroTurno/programacionMensual`

### 52. Gestión del Conocimiento

Solicitudes de capacitación. Ruta /gestionConocimiento/solicitudCapacitacion.

- **Solicitud de capacitación** `/gestionConocimiento/solicitudCapacitacion`

### 53. Medicina Laboral

Agenda y atención de medicina laboral, adicional al módulo de Evaluación Médica Ocupacional (EMO). Rutas /medicinaLaboral/*.

- **Agendar** `/medicinaLaboral/agendar`
- **Atención médica** `/medicinaLaboral/atencionMedica`

### 54. Códigos SUMI

Catálogo de productos y parametrización farmacéutica (formas farmacéuticas, grupos terapéuticos, vías de administración). Parcialmente expuesto bajo Farmacia > Productos.

- **Productos / Código SUMI** `/codigosSumi/codigoSumi`
- **Formas farmacéuticas** `/codigosSumi/formasFarmaceuticas`
- **Grupos terapéuticos** `/codigosSumi/gruposTerapeuticos`
- **Subgrupos terapéuticos** `/codigosSumi/subgruposTerapeuticos`
- **Vías de administración** `/codigosSumi/viasAdministracion`
- **Líneas bases** `/codigosSumi/lineasBases`
- **Parametrización** `/codigosSumi/parametrizacionCodesumis`

## Archivos de soporte

- `docs/inventario-modulos-horus-health-v2.html` — documento para impresión / envío al expediente.
- `docs/horus/menu-produccion.json` — menú maestro extraído de producción (49 entradas, con duplicados).
- `docs/horus/menu-produccion-unico.json` — mismos títulos únicos (47).
