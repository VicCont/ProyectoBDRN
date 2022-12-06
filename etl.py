import json 
import csv
import copy

def transformaciones(data,responses,califs):
    aux_direcciones={}
    direcciones_extras={}
    brands=[]
    malos=[]
    for extras in califs:
        direcciones_extras[extras['name']]=extras
    for auris_marca in data:
        brands.append(auris_marca["name"])
        for auri in auris_marca["phones"]:
            auri["brand"]=auris_marca["name"]
            aux_direcciones[auri['name']]=auri
            if (type(auri['file']) is list ):
                auri['file']=auri['file']=0
    for respuesta in responses:
        brand=aux_direcciones[respuesta["earphone"]["name"]]['brand']
        llave=brand+' '+(respuesta["earphone"]["name"].split(' (')[0])
        llave=llave.upper().replace("-","")
        if (llave in direcciones_extras):
            aux_copy=copy.deepcopy(direcciones_extras[llave])
            del aux_copy['name']
            aux_direcciones[respuesta["earphone"]["name"]].update(aux_copy)
            del aux_copy
        aux_direcciones[respuesta["earphone"]["name"]]["L"]=respuesta[" L"]
        aux_direcciones[respuesta["earphone"]["name"]]["R"]=respuesta[" R"]
    f=open("insertable_mongo.json","w+")
    aux_direcciones=list(aux_direcciones.values())
    transformacion_neo4j(aux_direcciones,brands)
    [ f.write(json.dumps(x)) for x in transformacion_mongo(copy.deepcopy(aux_direcciones))]
    f.close()
    transformacion_monet(aux_direcciones)

def transformacion_mongo(data):
    sides=['L','R']
    fields=['freq','db']
    for auri in data:
        for side in sides:
            list_freq=[]
            for x in auri[side].items():
                dict_aux={}     
                for i in range(2):
                    dict_aux[fields[i]]=x[i]
                list_freq.append(dict_aux)
            auri[side]=list_freq

    return data

def transformacion_monet(data):
    header = ['brand', 'file', 'name', 'freqL','freqR','valueR','valueL','rank','value','price','category','description','tonality_rank','technical_rank','setup','owner','note_wheight']
    with open('insertable_monet.csv', 'w+', encoding='UTF8', newline='\n') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for auri in data:
            dict_aux={
                'brand':auri['brand'],
                 'file':auri['file'],
                  'name':auri['name']
            }
            extras=['rank','value','name','price','category','description','tonality_rank','technical_rank','setup','owner','note_wheight']
            for extra in extras:
                if extra in auri:
                    dict_aux[extra]=auri[extra]
                else:
                    dict_aux[extra]=''
            for L,R in zip(auri["L"].items(),auri["R"].items()):
                dict_aux["freqL"]=L[0]
                dict_aux["freqR"]=R[0]
                dict_aux["valueR"]=R[1]
                dict_aux["valueL"]=L[1]
                writer.writerow(dict_aux)

def transformacion_neo4j(data,brands):
    header_pruduct = ['brand', 'file', 'name','rank','value','price','category','description','tonality_rank','technical_rank','setup','owner','note_wheight']
    header_measurements=['brand','name','side','freq','db']
    sides=['L','R']
    with open('measurements_neo.csv', 'w+', encoding='UTF8', newline='\n') as mea:
        writer_samples = csv.DictWriter(mea, fieldnames=header_measurements)
        writer_samples.writeheader()
        with open('products_neo.csv', 'w+', encoding='UTF8', newline='\n') as f:
            writer = csv.DictWriter(f, fieldnames=header_pruduct)
            writer.writeheader()
            for auri in data:
                dict_aux={}
                for column in header_pruduct:
                    if column in auri:
                        dict_aux[column]=auri[column]
                    else:
                        dict_aux[column]=''
                writer.writerow(dict_aux)
                s = set(header_measurements)
                exclude = [x for x in header_pruduct if x not in s]
                for column in exclude:
                    del dict_aux[column]
                for side in sides:
                    dict_aux['side']=side
                    for freq,db in auri[side].items():
                        dict_aux['freq']=freq
                        dict_aux['db']=db
                        writer_samples.writerow(dict_aux)


                    
                

    with open('brands_neo.csv', 'w+',newline='\n') as f:
        write = csv.writer(f)
        write.writerow(['brand'])
        write.writerows([[x] for x in brands])

if __name__=="__main__":
    f = open('phone_book.json')
    data=json.load(f)
    f.close()
    f = open('califs.json')
    extras=json.load(f)
    f.close()

    f=open('mongo-data.json')
    responses=json.load(f)
    f.close()
    responses=sum(responses,[])
    responses=sum(responses,[])
    transformaciones(copy.deepcopy(data),responses,extras)
    
