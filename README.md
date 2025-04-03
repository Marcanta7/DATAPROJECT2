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



