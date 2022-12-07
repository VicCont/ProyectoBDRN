# **Proyecto Final NoSQL2022**
**Equipo**: Victor Contreras, David González

## **Objetivo**
En este proyecto presentaremos el uso de una API en Python que nos conecte a una base de datos para su uso en bases de datos NoSQL. Primero, se procesarán sus datos en un MongoDB, el cual a su vez se enviará a un MonetDB (base columnar) y un Neo4J/GraphQL (base de datos de grafos), presentando así unos queries de ejemplo.

En este proyecto, se estará presentado una base de datos de audífonos.

## **Acerca de su uso**
### **Requerimientos**
Para su uso, se requiere acceso a la consola de Ubuntu (que puede ser por medio de consola de Linux o instalando [Ubuntu 20.04](https://ubuntu.com/server/docs/installation) en el equipo).

Hecho eso, se requiere además la instalación de Docker, el cual puede instalarse como la aplicación [Docker Desktop](https://docs.docker.com/desktop/install/windows-install/) o por medio del [Ubuntu](https://docs.docker.com/desktop/install/ubuntu/) previamente instalado.

Así, ahora se puede instalar las bases de datos de MongoDB, MonetDB y Neo4J.

**MongoDB** se instala por medio del siguiente comando en consola de Ubuntu:

```
docker volume create mongo-data
docker stop mongo
docker rm mongo
# cd carpeta de sus datos
export EX_DIR=`pwd`/mongodb-sample-dataset
echo $EX_DIR
mkdir -p $DATA_DIR
docker run -p 27017:27017 \
       -v mongo-data:/data/db \
       -v $EX_DIR:/mongodb-sample-dataset \
       --name mongo \
       -d mongo
```
Para correr su shell se usa:

```
docker exec -it mongo mongosh
```

En el caso del **MonetDB**, este se inicializa como:

```
docker volume create monet-data
docker stop monetdb
docker rm monetdb
docker run \
       -v monet-data:/var/monetdb5/dbfarm \
       -p 50001:50000 \
       --name monetdb \
       -d monetdb/monetdb:latest
```

Y para meternos al shell de MonetDB y correr comandos, se usa:

```
docker exec -it monetdb /bin/bash
```

Por último, para el **Neo4J**, se hace lo siguiente:

Actualizamos lista de paquetes del sistema

```
sudo apt update
```

Instalamos el Neo4J

```
sudo apt install neo4j
```

Por último, se habilita el servicio de Neo4J con (este último comando se hace para consola Ubuntu instalada en sistema operativo Windows)

```
sudo service neo4j start
```

Finalmente, también se requiere instalación de [Python](https://linuxhint.com/install-python-ubuntu-22-04/) y [Anaconda](https://linuxhint.com/install-anaconda-ubuntu-22-04/) en el equipo, lo cual se puede hacer, como se indica, en Ubuntu, y paquetes adicionales a la versión vanilla de Python están presentes en el **requirements.txt**, pero estos se instalan solos al correr el archivo **etl.py** y **comandos.sh**.

## **Manejo**
El código principal se corre por medio del archivo **comandos.sh**, el cual se encarga de levantar las bases de datos NoSQL, al igual de cargar el API de la base de datos, presente en el archivo **etl.py** para insertar los datos en las bases y correr los queries de ejemplo.

Primero, se levanta el contenedor en Docker para el MongoDB y el MonetDB con las líneas mostradas anteriormente.

Luego, se levanta el ambiente virtual del proyecto con la siguiente línea de comandos:

```
virtualenv proyecto_final
source proyecto_final/bin/activate
pip install requirements.txt

conda create -n proyecto_final anaconda
source activate proyecto_final
conda install requirements.txt
```

De este, luego se invoca el API de audífonos invocando el scraper
```
python scrapper_crin.py
```

Este último nos regresa el **insertable_mongo.json**, el archivo que poblará nuestro MongoDB por un comando de **mongoimport**. El formato general que sigue el JSON es el siguiente:

```
{
    "name": <string>,
    "file": <string>,
    "brand": <string>,
    "rank": <string>,
    "value": <integer>,
    "price": <integer>,
    "category": <string>,
    "description": <string>,
    "tonality_rank": <string>,
    "technical_rank": <string>,
    "setup": <string>,
    "owner": <string>,
    "note_weight": <integer>,
    "L": [{
        "freq": <string-float>,
        "db": <string-float>
    },{
        "freq": <string-float>,
        "db": <string-float>
    },...],
    "R": [{
        "freq": <string-float>,
        "db": <string-float>
    },{
        "freq": <string-float>,
        "db": <string-float>
    },...]
}
```

Esto es la representación del JSON que se inserta, conteniendo un documento con dichos datos para cada producto en existencia de la API. Los datos presentes representan lo siguiente:
* *name*: nombre del producto
* *file*: archivo del producto que guarda sus datos dentro de la API
* *brand*: marca del producto
* *tonality_rank y technical_rank*: rangos de tono y técnico del producto según la reseña
* *rank*: rango de calificación general del producto por reseña. Estas se presentan en formato de letras 'S', 'A', 'B', etc. con 'S' el más alto y 'F' el más bajo, a veces cargando '+' o '-' junto a la letra
* *value*: valor del producto
* *price*: precio real del producto en el mercado
* *category*: tipo de audífonos, que pueden ser Balanceados, Warm, entre otros 
* *description*: comentarios del producto sobre detalles de uso.
* *setup*: configuración por usar
* *owner*: dueño del producto (no es lo mismo que marca)
* *note_weight*: peso del audio por su uso
* *L y R*: test de frecuencia *freq* y su resultado *bd* para el lado izquierdo (L) o lado derecho (R); esta es una lista de pruebas hechas al dispositivo por distintas frecuencias

Estos mismos datos también están presentes en el MonetDB y Neo4J, pero convertidos a tablas CSV.

 **insertable_monet.csv**, generado al correr el scrapper y el ETL, se copia al MonetDB tras crear la tabla que almacena sus datos. El método de crear Queries es similar al de SQL, pero con cambios mínimos a la forma de correr código, ya que la diferencia principal de la base de datos es el proceso interno del código. 

 ```
docker cp insertable_monet.csv monetdb:/home/monetdb
docker exec -it monetdb bash
monetdb create 'proyecto_final'
monetdb release 'proyecto_final'
mclient -d 'proyecto_final'
create table data_proyecto(
brand varchar(50),
file varchar(50),
name varchar(50),
freqL varchar(10),
freqR varchar(10),
valueR varchar(10),
valueL varchar(10),
rank varchar(5),
value varchar(10),
price varchar(20),
category varchar(50),
description varchar(200),
tonality_rank varchar(5),
technical_rank varchar(5),
setup varchar(50),
owner varchar(50),
note_wheight varchar(5)
);
 ```
 
 Al Neo4J se le insertan las tablas primero entrando al shell de Neo4J usando el comando
 ```
docker exec -it testneo4j bash
cypher-shell -u neo4j -p test
 ```

Luego, se cargan los CSV con terminación **_neo.csv** con comandos como
```
LOAD CSV WITH HEADERS FROM "https://raw.githubusercontent.com/VicCont/ProyectoBDRN/main/brands_neo.csv" AS row
CREATE (b:Brands)
SET b = row;
```

Los cuales luego se usan para formar relaciones como de Owner dueño de Product
```
MATCH (p:Products),(c:Owners)
WHERE p.owner = c.owner
CREATE (C)-[:OWNS]->(p);
```

La forma de construir Queries en Neo4J es distinta a SQL en varios modos, pero de los principales es:
* SELECT es sutituído por RETURN
* Tus datos se escogen de nodos y relaciones por medio de MATCH
* GROUP BY no existe como tal, sino que si en el RETURN se hace un agregado, la cláusula del agregado de agrupa según los otros campos presentes en el RETURN

## **Ejemplo de Uso**

Los comandos de ejemplo para Queries de las tres bases de datos ya se presentan comentariados en **comandos.sh**, pero se presentan aquí también para facilidad.

### **Ejemplo.** En el Neo4J, ¿cuáles son las marcas más populares en cada rango de calificación?
Primero, dado que los WITH son 'subqueries', queremos reordenar los datos por el nombre de la marca, que a su vez los ordena por popularidad acumulada en cada rango, haciendo un segundo WITH que usa el agregado de count() para contar recurrencias de cada marca en cada rank. Finalmente, se orden de forma descendente la popularidad y se regresa el primer resultado en cada rango usando el agregado head() con el collect() que colecciona todos los nombres de marcas en cada rank de forma descendente. Esto al final nos da la marca más popular por rank
```
MATCH (b:Brands)
WITH b
ORDER BY b.brand
MATCH (b:Brands)-[:BRANDS]->(p:Products), (r:Ranks)-[:RANKING]->(p:Products)
WITH b.brand as brand, r.rank as ranking, count(b.brand) as popularity
ORDER BY popularity DESC
RETURN head(COLLECT(distinct brand)), ranking, max(popularity) as most_popular
ORDER BY ranking;
```

### **Ejemplo.** En el MongoDB, ¿cuáles audífonos presentan una explicación de daño auditivo al usuario, donde la exposición máxima recomendada es de 70 dB?

Recordando que *'L'* y *'R'* almacenan las frecuencias a las que se presentan los audífonos, tenemos el siguiente Query que nos regresa la respuesta con un 'find' que nos regrese 'db' de 'L' cuyos valores sean mayores a 80, dándonos el nombre y marca del producto:

```
db.insertable_mongo.find({"L.db":{$gte:"80"}},{name:1,brand:1,_id:0}) 
```

### **Ejemplo.** En el MonetDB, ¿cuál sería la frecuencia de sonido del audífono más 'promedio' (esto es, promedio de frecuencia de audífonos de todos los registrados)?

Este es un QUERY directo que usa el agregado de avg() para promediar, resaltando que su formato es similar al SQL, pero con los beneficios de una base columnar por el gran tamaño de la tabla

```
select rank ,avg(abs(cast(valuel as decimal(9,4))-cast(valuer as decimal(9,4)))) as avg_in from data_proyecto where rank is not null group by rank order by avg_in;

```
