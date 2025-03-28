# TP0: Docker + Comunicaciones + Concurrencia

En el presente repositorio se provee un esqueleto básico de cliente/servidor, en donde todas las dependencias del mismo se encuentran encapsuladas en containers. Los alumnos deberán resolver una guía de ejercicios incrementales, teniendo en cuenta las condiciones de entrega descritas al final de este enunciado.

 El cliente (Golang) y el servidor (Python) fueron desarrollados en diferentes lenguajes simplemente para mostrar cómo dos lenguajes de programación pueden convivir en el mismo proyecto con la ayuda de containers, en este caso utilizando [Docker Compose](https://docs.docker.com/compose/).

## Instrucciones de uso
El repositorio cuenta con un **Makefile** que incluye distintos comandos en forma de targets. Los targets se ejecutan mediante la invocación de:  **make \<target\>**. Los target imprescindibles para iniciar y detener el sistema son **docker-compose-up** y **docker-compose-down**, siendo los restantes targets de utilidad para el proceso de depuración.

Los targets disponibles son:

| target  | accion  |
|---|---|
|  `docker-compose-up`  | Inicializa el ambiente de desarrollo. Construye las imágenes del cliente y el servidor, inicializa los recursos a utilizar (volúmenes, redes, etc) e inicia los propios containers. |
| `docker-compose-down`  | Ejecuta `docker-compose stop` para detener los containers asociados al compose y luego  `docker-compose down` para destruir todos los recursos asociados al proyecto que fueron inicializados. Se recomienda ejecutar este comando al finalizar cada ejecución para evitar que el disco de la máquina host se llene de versiones de desarrollo y recursos sin liberar. |
|  `docker-compose-logs` | Permite ver los logs actuales del proyecto. Acompañar con `grep` para lograr ver mensajes de una aplicación específica dentro del compose. |
| `docker-image`  | Construye las imágenes a ser utilizadas tanto en el servidor como en el cliente. Este target es utilizado por **docker-compose-up**, por lo cual se lo puede utilizar para probar nuevos cambios en las imágenes antes de arrancar el proyecto. |
| `build` | Compila la aplicación cliente para ejecución en el _host_ en lugar de en Docker. De este modo la compilación es mucho más veloz, pero requiere contar con todo el entorno de Golang y Python instalados en la máquina _host_. |

### Servidor

Se trata de un "echo server", en donde los mensajes recibidos por el cliente se responden inmediatamente y sin alterar. 

Se ejecutan en bucle las siguientes etapas:

1. Servidor acepta una nueva conexión.
2. Servidor recibe mensaje del cliente y procede a responder el mismo.
3. Servidor desconecta al cliente.
4. Servidor retorna al paso 1.


### Cliente
 se conecta reiteradas veces al servidor y envía mensajes de la siguiente forma:
 
1. Cliente se conecta al servidor.
2. Cliente genera mensaje incremental.
3. Cliente envía mensaje al servidor y espera mensaje de respuesta.
4. Servidor responde al mensaje.
5. Servidor desconecta al cliente.
6. Cliente verifica si aún debe enviar un mensaje y si es así, vuelve al paso 2.

### Ejemplo

Al ejecutar el comando `make docker-compose-up`  y luego  `make docker-compose-logs`, se observan los siguientes logs:

```
client1  | 2024-08-21 22:11:15 INFO     action: config | result: success | client_id: 1 | server_address: server:12345 | loop_amount: 5 | loop_period: 5s | log_level: DEBUG
client1  | 2024-08-21 22:11:15 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°1
server   | 2024-08-21 22:11:14 DEBUG    action: config | result: success | port: 12345 | listen_backlog: 5 | logging_level: DEBUG
server   | 2024-08-21 22:11:14 INFO     action: accept_connections | result: in_progress
server   | 2024-08-21 22:11:15 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:15 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°1
server   | 2024-08-21 22:11:15 INFO     action: accept_connections | result: in_progress
server   | 2024-08-21 22:11:20 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:20 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°2
server   | 2024-08-21 22:11:20 INFO     action: accept_connections | result: in_progress
client1  | 2024-08-21 22:11:20 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°2
server   | 2024-08-21 22:11:25 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:25 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°3
client1  | 2024-08-21 22:11:25 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°3
server   | 2024-08-21 22:11:25 INFO     action: accept_connections | result: in_progress
server   | 2024-08-21 22:11:30 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:30 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°4
server   | 2024-08-21 22:11:30 INFO     action: accept_connections | result: in_progress
client1  | 2024-08-21 22:11:30 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°4
server   | 2024-08-21 22:11:35 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:35 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°5
client1  | 2024-08-21 22:11:35 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°5
server   | 2024-08-21 22:11:35 INFO     action: accept_connections | result: in_progress
client1  | 2024-08-21 22:11:40 INFO     action: loop_finished | result: success | client_id: 1
client1 exited with code 0
```


## Parte 1: Introducción a Docker
En esta primera parte del trabajo práctico se plantean una serie de ejercicios que sirven para introducir las herramientas básicas de Docker que se utilizarán a lo largo de la materia. El entendimiento de las mismas será crucial para el desarrollo de los próximos TPs.

### Ejercicio N°1:
Definir un script de bash `generar-compose.sh` que permita crear una definición de Docker Compose con una cantidad configurable de clientes.  El nombre de los containers deberá seguir el formato propuesto: client1, client2, client3, etc. 

El script deberá ubicarse en la raíz del proyecto y recibirá por parámetro el nombre del archivo de salida y la cantidad de clientes esperados:

`./generar-compose.sh docker-compose-dev.yaml 5`

Considerar que en el contenido del script pueden invocar un subscript de Go o Python:

```
#!/bin/bash
echo "Nombre del archivo de salida: $1"
echo "Cantidad de clientes: $2"
python3 mi-generador.py $1 $2
```

En el archivo de Docker Compose de salida se pueden definir volúmenes, variables de entorno y redes con libertad, pero recordar actualizar este script cuando se modifiquen tales definiciones en los sucesivos ejercicios.

### Ejercicio N°2:
Modificar el cliente y el servidor para lograr que realizar cambios en el archivo de configuración no requiera reconstruír las imágenes de Docker para que los mismos sean efectivos. La configuración a través del archivo correspondiente (`config.ini` y `config.yaml`, dependiendo de la aplicación) debe ser inyectada en el container y persistida por fuera de la imagen (hint: `docker volumes`).


### Ejercicio N°3:
Crear un script de bash `validar-echo-server.sh` que permita verificar el correcto funcionamiento del servidor utilizando el comando `netcat` para interactuar con el mismo. Dado que el servidor es un echo server, se debe enviar un mensaje al servidor y esperar recibir el mismo mensaje enviado.

En caso de que la validación sea exitosa imprimir: `action: test_echo_server | result: success`, de lo contrario imprimir:`action: test_echo_server | result: fail`.

El script deberá ubicarse en la raíz del proyecto. Netcat no debe ser instalado en la máquina _host_ y no se pueden exponer puertos del servidor para realizar la comunicación (hint: `docker network`). 


### Ejercicio N°4:
Modificar servidor y cliente para que ambos sistemas terminen de forma _graceful_ al recibir la signal SIGTERM. Terminar la aplicación de forma _graceful_ implica que todos los _file descriptors_ (entre los que se encuentran archivos, sockets, threads y procesos) deben cerrarse correctamente antes que el thread de la aplicación principal muera. Loguear mensajes en el cierre de cada recurso (hint: Verificar que hace el flag `-t` utilizado en el comando `docker compose down`).

## Parte 2: Repaso de Comunicaciones

Las secciones de repaso del trabajo práctico plantean un caso de uso denominado **Lotería Nacional**. Para la resolución de las mismas deberá utilizarse como base el código fuente provisto en la primera parte, con las modificaciones agregadas en el ejercicio 4.

### Ejercicio N°5:
Modificar la lógica de negocio tanto de los clientes como del servidor para nuestro nuevo caso de uso.

#### Cliente
Emulará a una _agencia de quiniela_ que participa del proyecto. Existen 5 agencias. Deberán recibir como variables de entorno los campos que representan la apuesta de una persona: nombre, apellido, DNI, nacimiento, numero apostado (en adelante 'número'). Ej.: `NOMBRE=Santiago Lionel`, `APELLIDO=Lorca`, `DOCUMENTO=30904465`, `NACIMIENTO=1999-03-17` y `NUMERO=7574` respectivamente.

Los campos deben enviarse al servidor para dejar registro de la apuesta. Al recibir la confirmación del servidor se debe imprimir por log: `action: apuesta_enviada | result: success | dni: ${DNI} | numero: ${NUMERO}`.



#### Servidor
Emulará a la _central de Lotería Nacional_. Deberá recibir los campos de la cada apuesta desde los clientes y almacenar la información mediante la función `store_bet(...)` para control futuro de ganadores. La función `store_bet(...)` es provista por la cátedra y no podrá ser modificada por el alumno.
Al persistir se debe imprimir por log: `action: apuesta_almacenada | result: success | dni: ${DNI} | numero: ${NUMERO}`.

#### Comunicación:
Se deberá implementar un módulo de comunicación entre el cliente y el servidor donde se maneje el envío y la recepción de los paquetes, el cual se espera que contemple:
* Definición de un protocolo para el envío de los mensajes.
* Serialización de los datos.
* Correcta separación de responsabilidades entre modelo de dominio y capa de comunicación.
* Correcto empleo de sockets, incluyendo manejo de errores y evitando los fenómenos conocidos como [_short read y short write_](https://cs61.seas.harvard.edu/site/2018/FileDescriptors/).


### Ejercicio N°6:
Modificar los clientes para que envíen varias apuestas a la vez (modalidad conocida como procesamiento por _chunks_ o _batchs_). 
Los _batchs_ permiten que el cliente registre varias apuestas en una misma consulta, acortando tiempos de transmisión y procesamiento.

La información de cada agencia será simulada por la ingesta de su archivo numerado correspondiente, provisto por la cátedra dentro de `.data/datasets.zip`.
Los archivos deberán ser inyectados en los containers correspondientes y persistido por fuera de la imagen (hint: `docker volumes`), manteniendo la convencion de que el cliente N utilizara el archivo de apuestas `.data/agency-{N}.csv` .

En el servidor, si todas las apuestas del *batch* fueron procesadas correctamente, imprimir por log: `action: apuesta_recibida | result: success | cantidad: ${CANTIDAD_DE_APUESTAS}`. En caso de detectar un error con alguna de las apuestas, debe responder con un código de error a elección e imprimir: `action: apuesta_recibida | result: fail | cantidad: ${CANTIDAD_DE_APUESTAS}`.

La cantidad máxima de apuestas dentro de cada _batch_ debe ser configurable desde config.yaml. Respetar la clave `batch: maxAmount`, pero modificar el valor por defecto de modo tal que los paquetes no excedan los 8kB. 

Por su parte, el servidor deberá responder con éxito solamente si todas las apuestas del _batch_ fueron procesadas correctamente.

### Ejercicio N°7:

Modificar los clientes para que notifiquen al servidor al finalizar con el envío de todas las apuestas y así proceder con el sorteo.
Inmediatamente después de la notificacion, los clientes consultarán la lista de ganadores del sorteo correspondientes a su agencia.
Una vez el cliente obtenga los resultados, deberá imprimir por log: `action: consulta_ganadores | result: success | cant_ganadores: ${CANT}`.

El servidor deberá esperar la notificación de las 5 agencias para considerar que se realizó el sorteo e imprimir por log: `action: sorteo | result: success`.
Luego de este evento, podrá verificar cada apuesta con las funciones `load_bets(...)` y `has_won(...)` y retornar los DNI de los ganadores de la agencia en cuestión. Antes del sorteo no se podrán responder consultas por la lista de ganadores con información parcial.

Las funciones `load_bets(...)` y `has_won(...)` son provistas por la cátedra y no podrán ser modificadas por el alumno.

No es correcto realizar un broadcast de todos los ganadores hacia todas las agencias, se espera que se informen los DNIs ganadores que correspondan a cada una de ellas.

## Parte 3: Repaso de Concurrencia
En este ejercicio es importante considerar los mecanismos de sincronización a utilizar para el correcto funcionamiento de la persistencia.

### Ejercicio N°8:

Modificar el servidor para que permita aceptar conexiones y procesar mensajes en paralelo. En caso de que el alumno implemente el servidor en Python utilizando _multithreading_,  deberán tenerse en cuenta las [limitaciones propias del lenguaje](https://wiki.python.org/moin/GlobalInterpreterLock).

## Condiciones de Entrega
Se espera que los alumnos realicen un _fork_ del presente repositorio para el desarrollo de los ejercicios y que aprovechen el esqueleto provisto tanto (o tan poco) como consideren necesario.

Cada ejercicio deberá resolverse en una rama independiente con nombres siguiendo el formato `ej${Nro de ejercicio}`. Se permite agregar commits en cualquier órden, así como crear una rama a partir de otra, pero al momento de la entrega deberán existir 8 ramas llamadas: ej1, ej2, ..., ej7, ej8.
 (hint: verificar listado de ramas y últimos commits con `git ls-remote`)

Se espera que se redacte una sección del README en donde se indique cómo ejecutar cada ejercicio y se detallen los aspectos más importantes de la solución provista, como ser el protocolo de comunicación implementado (Parte 2) y los mecanismos de sincronización utilizados (Parte 3).

Se proveen [pruebas automáticas](https://github.com/7574-sistemas-distribuidos/tp0-tests) de caja negra. Se exige que la resolución de los ejercicios pase tales pruebas, o en su defecto que las discrepancias sean justificadas y discutidas con los docentes antes del día de la entrega. El incumplimiento de las pruebas es condición de desaprobación, pero su cumplimiento no es suficiente para la aprobación. Respetar las entradas de log planteadas en los ejercicios, pues son las que se chequean en cada uno de los tests.

La corrección personal tendrá en cuenta la calidad del código entregado y casos de error posibles, se manifiesten o no durante la ejecución del trabajo práctico. Se pide a los alumnos leer atentamente y **tener en cuenta** los criterios de corrección informados  [en el campus](https://campusgrado.fi.uba.ar/mod/page/view.php?id=73393).

## Informe

### Ejercicio 1

Ejecutar:
```bash
./generar-compose.sh <archivo_salida> <cantidad_clientes>
```

En caso de falta de permisos:
```bash
chmod +x generar-compose.sh
```

El script de bash realizado primero valida que se le pasen los dos parámetros necesarios: el nombre del archivo de salida y la cantidad de clientes. Si no se pasan correctamente, se muestra un mensaje de error y se finaliza la ejecución. Caso contrario, se ejecuta el subscript de Python `generate_compose.py` pasándole los dos parámetros mencionados.

El script de Python realiza nuevamente la validación de parámetros para evitar inconsistencias en el caso de que no sea invocado a través de `generar-compose.sh`. Luego, convierte el número de clientes a entero y agrega la extensión .yaml al archivo de salida, en caso de ser necesario. Con estos datos, se procede a escribir el archivo dado.

El contenido del archivo de Docker Compose resultante incluye:
- Servicios: son los contenedores. Incluye el servidor y N clientes, donde N se refiere a la cantidad de clientes definida al ejecutar el script de bash. El `clientk` será identificado con el id `k`.
- Redes: configura cómo se conectan los contenedores entre sí. Para el ejercicio 1, se basa en la `testing_net` del archivo compose de ejemplo.

Casos de interés:

- Caso de error: faltan el nombre del archivo de salida.
    ```bash
    ./generar-compose.sh 2
    ```
    Salida esperada: 
    ```El script de bash debe ejecutarse de la siguiente manera: ./generar-compose.sh <archivo_salida> <cantidad_clientes>```

- Caso de error: faltan la cantidad de parámetros.
    ```bash
    ./generar-compose.sh docker-compose.yaml
    ```
    Salida esperada: 
    ```El script de bash debe ejecutarse de la siguiente manera: ./generar-compose.sh <archivo_salida> <cantidad_clientes>```

- Caso de error: faltan ambos parámetros.
    ```bash
    ./generar-compose.sh
    ```
    Salida esperada: 
    ```El script de bash debe ejecutarse de la siguiente manera: ./generar-compose.sh <archivo_salida> <cantidad_clientes>```
    
- Caso de error: la cantidad de clientes no es un número entero no negativo. 
    ```bash
    ./generar-compose.sh docker-compose.yaml sd
    ```
    Salida esperada: 
    ```Error: La cantidad de clientes debe ser un número entero no negativo.```

- Caso de éxito:
    ```bash
    ./generar-compose.sh docker-compose-example.yaml 3
    ```

    Salida esperada:
    ``` bash
        Nombre del archivo de salida: docker-compose-example.yaml
        Cantidad de clientes: 3
        Archivo compose.yaml generado correctamente
    ```

    Definición de Docker Compose:

    ```yaml
    name: tp0
    networks:
        testing_net:
            ipam:
            config:
            - subnet: 172.25.125.0/24
            driver: default
    services:
        client1:
            container_name: client1
            depends_on:
            - server
            entrypoint: /client
            environment:
                CLIENT_ID: '1'
                CLIENT_LOG_LEVEL: DEBUG
                SERVER_HOST: server
            image: client:latest
            networks:
            - testing_net
        client2:
            container_name: client2
            depends_on:
            - server
            entrypoint: /client
            environment:
                CLIENT_ID: '2'
                CLIENT_LOG_LEVEL: DEBUG
                SERVER_HOST: server
            image: client:latest
            networks:
            - testing_net
        client3:
            container_name: client3
            depends_on:
            - server
            entrypoint: /client
            environment:
                CLIENT_ID: '3'
                CLIENT_LOG_LEVEL: DEBUG
                SERVER_HOST: server
            image: client:latest
            networks:
            - testing_net
        server:
            container_name: server
            entrypoint: python3 /main.py
            environment:
                LOGGING_LEVEL: DEBUG
                PYTHONUNBUFFERED: '1'
            image: server:latest
            networks:
            - testing_net
    ```

### Ejercicio 2

Para lograr evitar reconstruir las imágenes de Docker al hacer cambios en los archivos de configuración, `config.ini` y `config.yaml`, modifiqué la definición de Docker Compose para utilizar volúmenes. Mediante estos, se montan los archivos de configuración en los contenedores, permitiendo que los cambios en los mismos persistan sin reconstruir las imágenes.

Por otro lado, agregué al docker-compose la variable de entorno `CONFIG_FILE` (tanto en los clientes como en el servidor), lo que permite definir la ubicación del archivo de configuración de la aplicación dada dentro del contenedor. 

Elegí usar `bind mount` porque permite que los archivos de configuración puedan editarse desde el host y que los cambios se reflejen de manera inmediata dentro del contenedor.

**Ejemplo**:

1) 

    ```bash
    ./generar-compose.sh docker-compose-dev.yaml 3
    docker build -f ./server/Dockerfile -t server:latest .
    docker build -f ./client/Dockerfile -t client:latest .
    docker compose -f docker-compose-dev.yaml up -d
    docker logs client3
    docker compose -f docker-compose-dev.yaml stop
    docker compose -f docker-compose-dev.yaml down
    ```

2) Cambiar alguna configuración en `client/config.yaml`. Por ejemplo: `level: "DEBUG"`.

3) Visualizar el cambio realizado en los logs:
    ```bash
    docker compose -f docker-compose-dev.yaml up -d
    docker logs client3
    ```

### Ejercicio 3

#### Ejecución

1) 

    ```bash
    ./generar-compose.sh docker-compose-dev.yaml 1
    docker build -f ./server/Dockerfile -t server:latest .
    docker build -f ./client/Dockerfile -t client:latest .
    docker compose -f docker-compose-dev.yaml up -d
    ```

2) 

- Enviar mensaje default: `./validar-echo-server.sh`
- Enviar mensaje personalizado: `./validar-echo-server.sh <mensaje_sin_espacios>`

#### Explicación

**Obtener puerto:**

`SERVER_PORT=$(grep '^SERVER_PORT' ./server/config.ini | cut -d '=' -f2 | tr -d '[:space:]')`

- `grep '^SERVER_PORT' ./server/config.ini` busca la línea que contiene el parámetro SERVER_PORT en el archivo de configuración.
- `cut -d '=' -f2` extrae el valor del puerto, que se encuentra después del signo igual (=).
- `tr -d '[:space:]'`elimina espacios alrededor del número de puerto extraído.

**Enviar mensaje al servidor y recibir respuesta:**

`RESPONSE=$(docker run --rm --network "$NETWORK_NAME" busybox sh -c "echo $MESSAGE | nc -w 2 $SERVER_CONTAINER $SERVER_PORT")`

- `docker run` crea y ejecuta un nuevo contenedor.
- `--rm` elimina el contenedor automáticamente una vez que el comando finaliza.
- `--network "$NETWORK_NAME"` hace que el contenedor busybox utilice la misma red que el contenedor del servidor. Esto permite la comunicación sin necesidad de exponer puertos.
- `busybox` usa una imagen mínima de Docker que tiene herramientas como netcat.
- `sh` invoca la shell.
- `-c` le pasa a la shell el comando que está entre comillas para que lo ejecute.
- `-w 2` define un tiempo de espera de 2 segundos.

### Ejercicio 4

#### Ejecución

A continuación detallo un ejemplo en el cual se puede observar en los logs del servidor lo que ocurre cuando este recibe SIGTERM:

```bash
./generar-compose.sh docker-compose-dev.yaml 3
docker build -f ./server/Dockerfile -t server:latest .
docker build -f ./client/Dockerfile -t client:latest .
docker compose -f docker-compose-dev.yaml up -d
docker compose -f docker-compose-dev.yaml stop server
docker logs server
```

También se puede utilizar el flag `-t int` para especificar los segundos que se esperará para que los contenedores se cierren gracefully: `docker compose -f docker-compose-dev.yaml stop -t 20`.

#### Explicación

Cuando el cliente recibe `SIGTERM`, se ejecuta la función `GracefulShutdown(client *common.Client)`. Esto permite que el cliente realice el proceso de cierre antes de terminar, a través del método `Close()`. Durante el cierre, el cliente procede primero a avisarle al servidor que se está cerrado mediante el mensaje `CLIENT_SHUTDOWN`, para luego cerrar la conexión con el mismo.

Durante la ejecución del cliente, se crean sockets para cada mensaje enviado. Si el servidor responde con el mensaje `SERVER_SHUTDOWN`, el cliente también cierra su conexión. En el caso de que el servidor finalice después de que el cliente ya haya cerrado una conexión, cuando este último intente establecer una nueva conexión en la siguiente iteración, se atrapará el error y se saldrá del loop.
    
Cuando el servidor recibe la signal `SIGTERM`, se ejecuta la función `graceful_shutdown`. En ésta se invoca el método `close()` en el cual el servidor le avisa a los clientes conectados acerca del proceso de cierre enviándoles el mensaje `SERVER_SHUTDOWN`. Luego, cierra todas las conexiones abiertas con los clientes. Por último, se cierra el socket del servidor. Cuando no se pueda aceptar una conexión en `__accept_new_connection()`, se atrapará el error y finalizará el proceso del servidor.

Si durante el manejo de una conexión el servidor recibe `CLIENT_SHUTDOWN`, cierra el socket asociado y lo elimina de la lista de conexiones abiertas.

### Ejercicio 5

Para ejecutar este ejercicio, pueden seguirse los siguientes pasos:

```bash
./generar-compose.sh docker-compose-dev.yaml 5
docker build -f ./server/Dockerfile -t server:latest .
docker build -f ./client/Dockerfile -t client:latest .
docker compose -f docker-compose-dev.yaml up -d
```

En el caso de querer configurar menos o más de 5 agencias, es posible modificar el parámetro asociado en `./generar-compose.sh docker-compose-dev.yaml <cantidad_agencias>`.

Los datos de cada agencia (nombre, apellido, dni, fecha de nacimiento y número de la apuesta) son recibidos como variables de entorno del archivo de Docker Compose. En este se definen las agencias con datos aleatorios. El identificador de la agencia es el id del cliente. 

Tanto en el cliente como en el servidor se utilizan las funciones de envío y recepción de mensajes definidas en `communicationProtocol.go` y `communication_protocol.py` para evitar los fenómenos _short read y short write_. Se lee de a un byte, hasta el delimitador de mensajes `\n`.

El cliente sabe cómo serializar los datos de una apuesta para poder enviarlos al servidor, mientras que este último sabe cómo deserializarlos.
- Cliente: La clase Bet define los datos de la apuesta y los serializa convirtiendo a string con el formato DATO=VALOR, separados por comas.
- Servidor: La clase Bet tiene el método de clase `deserialize(cls, data: str)` que divide la cadena recibida por comas y obtiene los datos de la apuesta para luego crear una instancia de Bet. Si el formato es inesperado, lanza un error.

Cada agencia envía la apuesta al servidor con `SendMessage(conn net.Conn, msg string) error`. Luego, recibe la confirmación con `ReceiveMessage(conn net.Conn) (string, error)`. La respuesta del servidor puede ser
- SUCCESS: La apuesta fue almacenada correctamente. Ante esta respuesta, el cliente imprime por log: `action: apuesta_enviada | result: success | dni: ${DNI} | numero: ${NUMERO}`.
- FAIL: La apuesta no fue almacenada. Puede ocurrir, por ejemplo, si se reciben datos inválidos. En este caso, la agencia imprime un log de error: `action: apuesta_enviada | result: fail | dni: ${DNI} | numero: ${NUMERO}`.

El Servidor, al recibir una apuesta con `receive_message(socket)`, intenta almacenarla. Dependiendo del resultado de esta operación, envía a la agencia el mensaje de confirmación o error mencionado previamente, utilizando `send_message(socket, msg)`.
- Caso de éxito: se imprime por log `action: apuesta_almacenada | result: success | dni: ${DNI} | numero: ${NUMERO}`.
- Caso de error: se imprime por log `action: apuesta_almacenada | result: fail | dni: {bet.document} | numero: {bet.number} | error: {e}`

### Ejercicio 6

Para ejecutar este ejercicio, pueden seguirse los siguientes pasos:

```bash
./generar-compose.sh docker-compose-dev.yaml 5
docker build -f ./server/Dockerfile -t server:latest .
docker build -f ./client/Dockerfile -t client:latest .
docker compose -f docker-compose-dev.yaml up -d
```

Los archivos de las apuestas se encuentran descomprimidos en `.data/`. En el Docker Compose se agregó la configuración necesaria para montar el archivo `agency-{N}.csv` en el contenedor del cliente N y persistirlo por fuera de la imagen. La variable de entorno `BETS_FILE` tiene como valor la ruta para acceder al archivo correspondiente, dependiendo de cada agencia.

Cuando se crea una agencia (cliente), se lee el archivo de sus apuestas y se crea una `Bet` por cada línea con datos válidos. La clase `Bet` es la misma que en el ejercicio anterior, con la diferencia de que ahora el cliente se guarda un arreglo de apuestas en lugar de solo una.

En `StartClient()` se envían conjuntos de máximo `batch.maxAmount` apuestas, limitados solo en el caso en que el paquete supere 8kB. Para ello se utiliza la clase `BetsInBatches` que representa una colección de apuestas y la función `CreateBetsInBatches` que crea un arreglo de `BetsInBatches`. 
- Como el mensaje que se envía al servidor con el batch de apuestas tiene el formato final `bet1;bet2;...;betN\n`, en `CreateBetsInBatches` me aseguro que `bytesDelBatch + 1 (delimiter \n) + (cantidadDeApuestasDelBatch - 1 (delimiters ;)) <= 8kB` y que, a la vez, `cantidadDeApuestasDelBatch` sea máximo `batch.maxAmount`.

La clase `BetsInBatches` convierte a string las apuestas con `bet.Serialize()` creada en el ejercicio 5 y las junta una tras otra, separadas por `;`. Este es el mensaje que se envía al servidor.

Luego de enviar un conjunto de apuestas, el cliente espera la respuesta del servidor para poder enviar el siguiente grupo. Cuando termina de mandar todas las apuestas, le avisa al servidor que terminó y cierra la conexión.

Por otro lado, una vez que el servidor acepta una conexión, recibe las `BetsInBatches` de la agencia dada. Procesa las apuestas y las almacena. Responde con `SUCCESS` si todas las apuestas del batch fueron procesadas correctamente o con `FAIL` si hubo error con alguna. Luego, procede a recibir el siguiente batch. Finaliza y cierra la conexión con ese cliente cuando este último le informa que ha terminado de enviar apuestas.

### Ejercicio 7

Para ejecutar este ejercicio, pueden seguirse los siguientes pasos:

```bash
./generar-compose.sh docker-compose-dev.yaml 5
docker build -f ./server/Dockerfile -t server:latest .
docker build -f ./client/Dockerfile -t client:latest .
docker compose -f docker-compose-dev.yaml up -d
```

Con `docker logs clientN` se pueden observar los logs del cliente N, incluyendo la cantidad de ganadores de esa agencia. Por otro lado, con `docker logs server` se detallan los logs del servidor, entre los cuales podemos encontrar el que corresponse al sorteo.

A continuación detallo el procedimiento del cliente y el servidor.

<u>Cliente</u>:

1. Envía las apuestas de a batches, como en el ejercicio 6.
2. Una vez que termina de enviar todas las apuestas, le notifica esto al servidor con el mensaje `BETS_SENT`.
3. Le pide al servidor los DNIs de los ganadores de su agencia a través del mensaje de `GET_WINNERS`.
4. Espera la respuesta del servidor.
5. Recibe el mensaje `WINNERS:DNI_1,DNI_2,...,DNI_N` con los DNIs ganadores de la agencia. La clase Winners sabe como deserializar este mensaje y guardar un arreglo con los DNIs.
6. Log: `action: consulta_ganadores | result: success | cant_ganadores: {len(winners)}`.
7. Cierra la conexión con el servidor.

<u>Servidor</u>:

1. Nuevos atributos: 
	- `total_agencies` es la cantidad de agencias que enviarán apuestas. Depende de la variable de entorno `TOTAL_AGENCIES` del servidor en el Docker Compose, que coincide con la cantidad de clientes generados en el script.
	- `agencies_waiting` es un diccionario que tiene por valor el id de la agencia y como valor el socket asociado a ese cliente.
2. Acepta el intento de conexión de la agencia `i`.
3. Recibe todas las apuestas de la agencia `i` hasta recibir el mensaje `BETS_SENT` (o `CLIENT_SHUTDOWN`). Guarda el socket en el diccionario `waiting_agencies`
4. Repetir 2 y 3 hasta que todas las agencias hayan enviado sus apuestas.
5. Log action: sorteo | result: success
6. Sorteo: se cargan las apuestas (`load_bets()`) y se guarda las ganadoras (`has_won()`) en el diccionario `winners = {agency_id: [bet1.document, ..., betN.document]}`
7. Para cada agencia de `agencies_waiting` de la cual se reciba el mensaje `GET_WINNERS`, se le envía los documentos ganadores de la misma. Se utiliza este diccionario y `winners` para evitar hacer un broadcast de todos los ganadores hacia todas las agencias, limitándonos a enviar únicamente los que corresponden a la agencia dada. `Message.WINNERS.to_string(dni_winners)` serializa el mensaje enviado a cada cliente.
8. Luego de enviar los DNIs, se cierra la conexión con el cliente.

### Ejercicio 8

Para ejecutar este ejercicio, pueden seguirse los siguientes pasos:

```bash
./generar-compose.sh docker-compose-dev.yaml 5
docker build -f ./server/Dockerfile -t server:latest .
docker build -f ./client/Dockerfile -t client:latest .
docker compose -f docker-compose-dev.yaml up -d
```

Decidí usar _multiprocessing_ para que el servidor pueda aceptar conexiones y procesar mensajes en paralelo. Cada vez que un cliente (agencia) intenta conectarse con el servidor, se crea un nuevo proceso que maneja esa conexión. El `Process-i` recibe las apuestas de la agencia `i`, obtiene las ganadoras de la misma y le envía los DNIs de los ganadores.

Nuevos atributos del servidor:
- `self._agency_waiting` reemplaza al diccionario agregado en el ejercicio anterior. Guarda el id (número) de la agencia que maneja el proceso dado. No necesita ser un recurso compartido porque cada proceso conoce únicamente la agencia de la cual es responsable. 
-  `self.lock = threading.Lock()` permite controlar el acceso concurrente a los recursos compartidos del servidor, como el archivo de apuestas. El objetivo es evitar que múltiples procesos intenten acceder a estos recursos al mismo tiempo y resulten en datos inconsistentes.
- `self._clients_processes` guarda referencias a los procesos activos con el objetivo de poder hacerles `join()`. Solo el proceso principal que los creó accede a esta lista, por lo cual no necesita ser un recurso compartido (lo mismo ocurre con _clients_sockets).
 - `self.barrier_bets_received = threading.Barrier(total_agencies)` es una barrera que asegura que todas las agencias hayan finalizado de enviar sus apuestas para poder proceder con el sorteo. Si algún cliente se desconecta, se aborta la barrera y no se realizará el sorteo.
 - `self._client_socket` reemplaza al atributo `_clients_sockets` de los ejercicios anteriores. Cada proceso hijo se guarda únicamente un socket para comunicarse con la agencia que tiene a cargo. Como las conexiones son aceptadas desde el proceso principal, este cierra su copia del socket.
 - `self._name` es utilizado para indicar en los logs cuál es el proceso encargado de tal acción.

Los procesos hijos son creados con una copia de los datos del proceso principal, por lo que, antes de recibir las apuestas, realizan las siguientes acciones:
- Cambiar el nombre (`self._name`) del padre por el suyo.
- Cerrar su copia del socket del servidor (`self._server_socket`).
- Asignar correctamente `self._client_socket`.