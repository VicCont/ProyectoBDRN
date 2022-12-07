## creamos los dockers




docker run \
    --name testneo4j \
    -p7474:7474 -p7687:7687 \
    -d \
    -v $HOME/neo4j/data:/data \
    -v $HOME/neo4j/logs:/logs \
    -v $HOME/neo4j/import:/var/lib/neo4j/import \
    -v $HOME/neo4j/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/test \
    neo4j:latest

docker run -p 27017:27017 \
       -v $DATA_DIR:/data/db \
       -v $EX_DIR:/mongodb-sample-dataset \
       --name mongo \
       -d mongo
sleep 2
docker exec -it mongo mongosh

docker volume create monet-data
docker stop monetdb
docker rm monetdb
docker run \
       -v monet-data:/var/monetdb5/dbfarm \
       -p 50001:50000 \
       --name monetdb \
       -d monetdb/monetdb:latest

## creamos el ambiente para el proyecto
## para virtualenv
virtualenv proyecto_final
source proyecto_final/bin/activate
pip install requirements.txt

conda create -n proyecto_final anaconda
source activate proyecto_final
conda install requirements.txt

##obtenemos y generamos insertables
python scrapper_crin.py

##insertar monngo

docker cp insertable_mongo.json mongo:/
docker exec -it mongo mongoimport --db proyecto_final --drop --file insertable_mongo.json 

## explicación del daño auditivo, la exposición máxima recomendada es de 70 db
db.insertable_mongo.find({"L.db":{$gte:"80"}},{name:1,brand:1,_id:0}) 



#desbalance mayor a 5db por lado, esto nos habla de un mal control de calidad en los productos 
db.insertable_mongo.aggregate([

  { $project: { x: { $zip: { inputs: ["$L.db", "$R.db"] } } ,name:1,brand:1} },

  { $unwind: "$x" },

      { $project: {vall:{$toDouble:{ $first: "$x" }}, valr:{$toDouble:{ $last: "$x" }},name:1,brand:1}} ,
           { $project: {diff: {$abs:{$subtract:["$vall","$valr"]}},name:1,brand:1}} ,
    {$match: { diff: {$gte:5} }},
  {
    $group: {
       _id: "$_id",name:{ $first:"$name"},brand:{$first:"$brand"}
    }
  },
])



#desbalance promedio por marca, que marcas tienen menos control de calidad sobre sus productos 
db.insertable_mongo.aggregate([

  { $project: { x: { $zip: { inputs: ["$L.db", "$R.db"] } } ,name:1,brand:1} },

  { $unwind: "$x" },

      { $project: {vall:{$toDouble:{ $first: "$x" }}, valr:{$toDouble:{ $last: "$x" }},name:1,brand:1}} ,
           { $project: {diff: {$abs:{$subtract:["$vall","$valr"]}},name:1,brand:1}} ,
  {
    $group: {
       _id: "$brand",avarage_imbalance:{$avg: "$diff"},brand:{$first:"$brand"}
    }
  },
  { $sort : { avarage_imbalance : -1 } }
])



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
copy offset 2 into data_proyecto from '/home/monetdb/insertable_monet.csv' on client using delimiters ',',E'\n',E'\"' null as '';
exit


## desbalance promedio entre rangos (notamos que los mejores tienen menos)
select rank ,avg(abs(cast(valuel as decimal(9,4))-cast(valuer as decimal(9,4)))) as avg_in from data_proyecto where rank is not null group by rank order by avg_in;


## como sonaría el audifono más promedio 
select cast(freql as decimal(7,2)) freq, avg(cast(valuel as decimal(9,4))+cast(valuer as decimal(9,4)))/2 from data_proyecto group by freql order by freq;

## diferencia entre los audifonos considerados como calientes (warm mucho bajo) y brillosos (bright demasiado agudo) (son considerados los opuestos)
## se ve claramente como los warm estan por arriba de los bright en los bajos y se hace un cruce entre la región media, depués predomina el agudo
create table diferencia_extremos as select cast(freql as decimal(7,2)) freq,avg(cast(valuel as decimal(9,4))+cast(valuer as decimal(9,4)))/2 as db from data_proyecto where "like"(category, '%Warm%', '#', true) group by freql order by freq;
insert into diferencia_extremos select cast(freql as decimal(7,2)) freq, -avg(cast(valuel as decimal(9,4))+cast(valuer as decimal(9,4)))/2 as db from data_proyecto where "like"(category, '%Bright%', '#', true) group by freql order by freq; 
select freq ,avg(db) from diferencia_extremos group by freq having count(*)>=2;  



docker exec -it testneo4j bash
cypher-shell -u neo4j -p test
LOAD CSV WITH HEADERS FROM "https://raw.githubusercontent.com/VicCont/ProyectoBDRN/main/brands_neo.csv" AS row
CREATE (b:Brands)
SET b = row;
#brand,name,side,freq,db
SET m = row;
LOAD CSV WITH HEADERS FROM "https://raw.githubusercontent.com/VicCont/ProyectoBDRN/main/note_weight_neo.csv" AS row
CREATE (nw:NoteWeight)
SET nw = row;
LOAD CSV WITH HEADERS FROM "https://raw.githubusercontent.com/VicCont/ProyectoBDRN/main/owners_neo.csv" AS row
CREATE (o:Owners)
SET o = row;
LOAD CSV WITH HEADERS FROM "https://raw.githubusercontent.com/VicCont/ProyectoBDRN/main/products_neo.csv" AS row
CREATE (p:Products)
SET p = row
n.price = toInteger(row.price);

LOAD CSV WITH HEADERS FROM "https://raw.githubusercontent.com/VicCont/ProyectoBDRN/main/ranks_neo.csv" AS row
CREATE (r:Ranks)
SET r = row;
LOAD CSV WITH HEADERS FROM "https://raw.githubusercontent.com/VicCont/ProyectoBDRN/main/technical_ranks_neo.csv" AS row
CREATE (tcr:TechnicalRanks)
SET tcr = row;
LOAD CSV WITH HEADERS FROM "https://raw.githubusercontent.com/VicCont/ProyectoBDRN/main/tonality_rank_neo.csv" AS row
CREATE (tnr:TonalityRank)
SET tnr = row;

MATCH (p:Products),(c:Owners)
WHERE p.owner = c.owner
CREATE (C)-[:OWNS]->(p);

MATCH (p:Products),(c:Ranks)
WHERE p.rank = c.rank
CREATE (p)-[:RANKED]->(c);

MATCH (p:Products),(c:Brands)
WHERE p.brand = c.brand
CREATE (c)-[:PRODUCES]->(p);

:exit
exit

##Distribución de rank por owner

MATCH (o:Owners)-[:OWNS]->(p:Products), (p:Products)-[:RANKED]->(r:Ranks)
WITH o.owner as owner, r.rank as rank, count( r.rank) as num_rank
RETURN owner, rank, num_rank 
ORDER BY rank;

## Precio promedio por brand


MATCH (b:Brands)-[:PRODUCES]->(p:Products), (p:Products)-[:RANKED]->(r:Ranks)
where p.price is not null and p.price>=0
RETURN b.brand as brand, avg(p.price) as avg_price
order by avg_price desc;


## Marca más popular por rank

MATCH (b:Brands)
WITH b
ORDER BY b.brand
MATCH (b:Brands)-[:BRANDS]->(p:Products), (r:Ranks)-[:RANKING]->(p:Products)
WITH b.brand as brand, r.rank as ranking, count(b.brand) as popularity
ORDER BY popularity DESC
RETURN head(COLLECT(distinct brand)), ranking, max(popularity) as most_popular
ORDER BY ranking;
