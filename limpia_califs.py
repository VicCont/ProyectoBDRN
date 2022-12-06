import requests
from lxml import html
import json
import csv
import copy

def fix_content(dictionary,key,replacement=''):
    if len(dictionary[key])==0:
        dictionary[key]=replacement
    else:
        dictionary[key]=dictionary[key][0].replace('\t',"").replace('\n','')

def save_unique_edges(values,file_name,column_name):
    with open(file_name, 'w+',newline='\n') as f:
        write = csv.writer(f)
        write.writerow([column_name])
        write.writerows([[x] for x in values])


if __name__=="__main__":
    f=open('califs.html',encoding='utf-8')
    aux_parser=html.fromstring(f.read())
    f.close()
    results=[]
    ranks={}
    technical_ranks={}
    owners={}
    tonality_rank={}
    note_wheights={}
    missing_prices=['?','Discont.']
    for x in aux_parser.xpath('//tbody/tr'):
        dict_aux={
            'rank':x.xpath('td[@class="column-1 dtr-control"]/span/text()')[0],
            'value':x.xpath('td[@class="column-2"]/text()'),
            'name':str(x.xpath('td[@class="column-3"]/descendant-or-self::*/text()')[0]).upper().replace('\t',"").replace('(','').replace(')','').replace("-","").replace('\n',' ').split('\\')[0].split('"')[0].strip(),
            'price':x.xpath('td[@class="column-4"]/text()')[0],
            'category':x.xpath('td[@class="column-5"]/text()')[0],
            'description':x.xpath('td[@class="column-6"]/text()'),
            'tonality_rank':x.xpath('td[@class="column-7"]/text()')[0],
            'technical_rank':x.xpath('td[@class="column-8"]/text()')[0],
            'setup':x.xpath('td[@class="column-9"]/text()'),
            'owner':x.xpath('td[@class="column-10"]/text()'),
            'note_wheight':x.xpath('td[@class="column-11"]/text()')
        }
        fix_content(dict_aux,'description')
        fix_content(dict_aux,'owner','unknown')
        fix_content(dict_aux,'setup','unknown')
        fix_content(dict_aux,'note_wheight',0)
        if (len(dict_aux['value'])==0):
            dict_aux['value']=0
        else:
            dict_aux['value']=len(dict_aux['value'][0])
        if (dict_aux['price'] in missing_prices):
            dict_aux['price']=-1
        ranks[dict_aux['rank']]=None
        technical_ranks[dict_aux['technical_rank']]=None
        owners[dict_aux['owner']]=None
        tonality_rank[dict_aux['tonality_rank']]=None
        note_wheights[dict_aux['note_wheight']]=None
        results.append(dict_aux)
    save_unique_edges(list(owners.keys()),'owners_neo.csv','owner')
    save_unique_edges(list(tonality_rank.keys()),'tonality_rank_neo.csv','tonality_rank')
    save_unique_edges(list(note_wheights.keys()),'note_wheight_neo.csv','note_wheight')
    save_unique_edges(list(ranks.keys()),'ranks_neo.csv','rank')
    save_unique_edges(list(technical_ranks.keys()),'technical_ranks_neo.csv','technical_rank')

    f=open('califs.json','w+',encoding='utf-8')
    f.write(json.dumps(results))
    f.close()


