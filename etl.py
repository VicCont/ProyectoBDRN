import json 
import csv
import copy

def transformacion_mongo(data,responses):
    aux_direcciones={}
    brands=[]
    for auris_marca in data:
        brands.append(auris_marca["name"])
        for auri in auris_marca["phones"]:
            auri["brand"]=auris_marca["name"]
            aux_direcciones[auri['name']]=auri
    for respuesta in responses:
        aux_direcciones[respuesta["earphone"]["name"]]["L"]=respuesta[" L"]
        aux_direcciones[respuesta["earphone"]["name"]]["R"]=respuesta[" R"]
    f=open("insertable_mongo.json","w+")
    aux_direcciones=list(aux_direcciones.values())
    transformacion_neo4j(aux_direcciones,brands)
    f.write(json.dumps(aux_direcciones))
    f.close()
    transformacion_monet(aux_direcciones)

def transformacion_monet(data):
    header = ['brand', 'file', 'name', 'freqL','freqR','valueR','valueL']
    with open('insertable_monet.csv', 'w+', encoding='UTF8', newline='\n') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for auri in data:
            dict_aux={
                'brand':auri['brand'],
                 'file':auri['file'],
                  'name':auri['name']
            }
            for L,R in zip(auri["L"].items(),auri["R"].items()):
                dict_aux["freqL"]=L[0]
                dict_aux["freqR"]=R[0]
                dict_aux["valueR"]=R[1]
                dict_aux["valueL"]=L[1]
                writer.writerow(dict_aux)

def transformacion_neo4j(data,brands):
    header = ['brand', 'file', 'name',]
    with open('products_neo.csv', 'w+', encoding='UTF8', newline='\n') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for auri in data:
            dict_aux={
                'brand':auri['brand'],
                 'file':auri['file'],
                  'name':auri['name']
            }
            writer.writerow(dict_aux)
    with open('brands_neo.csv', 'w+',newline='\n') as f:
        write = csv.writer(f)
        write.writerow(['brand'])
        write.writerows([[x] for x in brands])

if __name__=="__main__":
    f = open('phone_book.json')
    data=json.load(f)
    f.close()
    f=open('mongo-data.json')
    responses=json.load(f)
    f.close()
    responses=sum(responses,[])
    responses=sum(responses,[])
    transformacion_mongo(copy.deepcopy(data),responses)
    
