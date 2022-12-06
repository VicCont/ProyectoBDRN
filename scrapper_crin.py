import uuid
import requests
import asyncio
import multiprocessing
import json
from Cryptodome.Cipher import AES
import base64
import hashlib
import aiohttp
from Cryptodome.Protocol.KDF import PBKDF2
import codecs
from aiohttp.client import ClientTimeout
import random

import etl
import limpia_califs

def limpiar_respuestas(response):
    freq={}
    for linea in response.split('\n'):
        if(linea.count(",")!=0):
            try:
                float(str(linea[0:linea.index(",")]))
                freq[str(linea[0:linea.index(",")])]=str(linea).strip()[linea.index(",")+1:]
            except:
                continue
    return freq

async def get_file(url, datos):
    cookies={'__adblocker':'true'}
    headers={"alt-svc":'h3=":443"; ma=86400, h3-29=":443"; ma=86400'
    ,'origin': 'https://crinacle.com'
    ,'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    ,'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"'
    ,"sec-fetch-site": "same-origin",
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'accept': '*/*',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'x-requested-with': 'XMLHttpRequest',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
    ,'referer': 'https://crinacle.com/graphing/tooliemfree.html'}
    respuesta=''
    await asyncio.sleep(random.randint(2,5))
    timeout = ClientTimeout(total=80000)  # `0` value to disable timeout
    async with aiohttp.ClientSession(headers=headers,timeout=timeout,cookies=cookies) as session:
        async with session.post(url,data=datos) as resp:
            body=await resp.read()
            respuesta = codecs.escape_decode(body)[0].decode('utf-8')

    respuesta=json.loads(respuesta)
    iv = bytes.fromhex(respuesta["iv"])
    salt = bytes.fromhex(respuesta['s'])

    md = hashlib.md5()
    md.update(datos['k'].encode("utf-8"))
    md.update(salt)
    cache0 = md.digest()
    md = hashlib.md5()
    md.update(cache0)
    md.update(datos['k'].encode("utf-8"))
    md.update(salt)
    cache1 = md.digest()
    key = cache0 + cache1
    cifrador=AES.new(key,AES.MODE_CBC,iv)
    texto=cifrador.decrypt(base64.b64decode(respuesta["ct"]))
    unpad = lambda s : s[:-ord(s[len(s)-1:])]
    resultado=unpad(texto).decode("utf-8").replace("\\n","\n").replace("\\r","").replace("\\t",",").replace('"',"").strip()
    return limpiar_respuestas(f"{resultado}")
    ##f = open(datos["f_p"],"w+")
    ##f.writelines(resultado)
    ##f.close()


async def get_earphone_data(auri):
    url_base="https://crinacle.com/graphing/d-c.php"
    if (type(auri["file"])==list):
        auri["file"]=auri["file"][0]
    id=str(uuid.uuid4())
    lados=[" L"," R"]
    responses={}
    responses["earphone"]=auri
    for lado in lados:
        archivo=f"data/{auri['file']+lado}.txt"
        data={'f_p':archivo,"k":id}
        responses[lado]=await get_file(url_base,data)
    return responses

def handler_get_earphone_data(workload):
    loop_async=asyncio.get_event_loop()
    resultados=[]
    exitosas, errores= loop_async.run_until_complete(asyncio.wait([get_earphone_data(x) for x in workload]))
    [resultados.append(x.result()) for x in exitosas]
    print(f"{type(resultados)}")
    return resultados

def append_results(results):
    resultados.append(results)

if __name__=='__main__':
    pool = multiprocessing.Pool(processes=10)
    peticiones_concurrentes=5
    worker_id=0
    f = open('phone_book.json')
    data=[]
    data = json.load(f)
    f.close()
    aux_workload=[]
    for auris_marca in data:
        aux_workload+=auris_marca["phones"]
    resultados=[]
    workload=iter(aux_workload)
    bandera=next(workload,None)
    while bandera is not None:
        parcial=[]
        for i in range(peticiones_concurrentes):
            if (bandera is not None):
                parcial.append(bandera)
                bandera=next(workload,None)
            else:
                break
        if (len(parcial)>0):
            pool.map_async(handler_get_earphone_data,[parcial],callback=append_results)
    pool.close()
    pool.join()

    extras=limpia_califs.main()
    etl.transformaciones(data,resultados,extras)

    # f=open("mongo-data.json","w+")    
    # f.write(json.dumps(resultados))
    # f.close()




    

