##insertar monngo

docker cp insertable_mongo.json mongo:/
docker exec -it mongo mongoimport --db proyecto_final --drop --file insertable_mongo.json 

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





