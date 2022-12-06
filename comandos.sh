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