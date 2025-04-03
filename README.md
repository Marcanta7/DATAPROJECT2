# DATA PROJECT 2: DANARESTART
DanaRestart. “Conectando ayuda para un nuevo comienzo.”
## Descripción
Tras la catastrofe ocurrida en Valencia y alrededores que ha representado la DANA, un numero muy grande de personas se han ofrecido como voluntarios para ayudar en las tareas de limpieza y recogida de muebles/alimentos, etc. Sin embargo el descontrol en las idas y venidas de los mismos hace que esta ayuda sea poco eficiente y por ello mucha gente se ha quedado sin ayuda a pesar de la cantidad abundante de recursos y medios que hay. En respuesta a ello se ha propuesto DANARESTAR, que consiste en una arquitectura E2E en un entorno cloud cuyas caracteristicas principales son que se trata de un proyecto Serverless en Streamming cuya funcion principal es encontrar match entre voluntarios y afectados.

En este repositorio, se encuentra la solución en Google Cloud que hemos diseñado. Consta de las siguientes partes:

1. Generador de datos con envío a Pub/Sub

2. Dataflow para transformación de los mensajes

3. BigQuery como almacenamiento

4. Cloud functions para avisos

5. Tableau para visualización


## Diseño de la arquitectura
Nuestra arquitectura se representa de la manera siguiente:

<div align=center><img src="https://github.com/Marcanta7/DATAPROJECT2/blob/847560ba424ae6f959c462c2fda5a98fa136123e/Arquitectura_DP2.png" /></div>

## PUB/SUB

Para simular las entradas de voluntarios y afectados hemos creado un scrip de python donde generamos dentro de unos parametros registrados y controlados, de forma aleatoria cada pocos segundos alertas tanto de voluntarios como de afectados las cuales se envian a dos topicos distintos de Pub/Sub. Además hemos querido realizar una UI con Streamlit donde se representaria de manera mas acertada lo que seria el ingreso de datos y la experiencia de Usuario. Estos datos ingresados se transfieren a Pub/Sub al igual que lo hacen los que generamos nosotros.

## DATAFLOW
El pipeline realiza las siguientes tareas:

### 1. Lectura de datos desde Pub/Sub

Se reciben mensajes JSON desde dos suscripciones de Pub/Sub: afectados y voluntarios.

Se decodifican los mensajes y se les asigna un tipo (affected o volunteer).

Se incrementa un contador processed para rastrear cuántas veces se ha intentado emparejar un registro.

Se agrupan los datos por clave (city, necessity, disponibility).

### Emparejamiento de afectados y voluntarios

Se comparan los datos agrupados.

Si hay coincidencia entre un afectado y un voluntario, se genera un registro matched.

Si no hay coincidencias, el afectado o voluntario no emparejado se marca como non_matched.

### Almacenamiento en BigQuery

Los registros emparejados (matched) se guardan en la tabla de BigQuery matched_table.

Los registros no emparejados (unmatched) se guardan en la tabla unmatched_table si han alcanzado el límite de intentos de emparejamiento.

### Reenvío de no emparejados a Pub/Sub

Si un afectado o voluntario no ha sido emparejado después de 7 intentos, se almacena en BigQuery.

Si tiene menos de 7 intentos, se reenvía al tema de Pub/Sub correspondiente para reintentar su emparejamiento en el siguiente ciclo del pipeline.

## CONFIGURACION
El script obtiene las configuraciones de GCP desde variables de entorno:
'''
export PROJECT_ID=<your-gcp-project>
export AFFECTED_SUB=<affected-subscription>
export VOLUNTEER_SUB=<volunteer-subscription>
export VOLUNTEER_TOPIC=<volunteer-topic>
export AFFECTED_TOPIC=<affected-topic>
export BQ_DATASET=<bigquery-dataset>
export MATCHED_TABLE=<matched-table>
export UNMATCHED_TABLE=<unmatched-table>
export TEMP_LOCATION=<gs://your-temp-bucket>
export STAGING_LOCATION=<gs://your-staging-bucket>
export REGION=<gcp-region>
'''

