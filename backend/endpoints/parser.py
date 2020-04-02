import requests
import json
import urllib
from requests.utils import requote_uri
from flask import jsonify, request, g
from models import Volunteer, Beneficiary, Operator, Tags

mp ={
    'Timestamp'   :'timestamp',
 'Ce Ofera'       :'offer',
 'Nume Prenume/ И':'last_name',#first_name
 'Telefon (activ)':'phone',
 'Facebook'       :'facebook_profile',
 'Sector / Cектор':'zone_address',
 'Adresa / Адрес' :'address',
 'Vârsta / Возрас':'age',
 'Câte ore zilnic':'availability',
 'Ce tip de activ':'activity_types',
 'Sunt de acord c':'aggreed_terms',
 'e-mail'         :'email',
 'A fost implIcat':'new_volunteer',
 'ce ECHIPA este ':'team',
 'Are nevoie cart':'need_sim_unite',
 'A trimis foto p':'sent_photo',
 'Ultima Temperat':'last_tempreture',
 'Activitatea de ':'profesia',
 'comentarii / fe':'comments',
 'Au primit legit':'received_contract',
 'Au primit carte':'received_cards',
 'Voluntari pentr':'april1',
 'Lista neagră':'black_list',
}

def parsephone(a):
    c = []
    for j in a:
        try:
            g = int(j)
            c.append(j)
        except:
            pass
    if c[0] == '0':
        c = c[1:]
    c = ''.join(c).replace('373','')
    if len(c)<8:
        c = '9'*(8-len(c))+c
    return c[:8]

def parseEmail(a):
    email = a['e-mail'].strip()
    if len(email)==0:
        email = a['Telefon (activ)']+'@test.com'
    return email

def parseName(name):
    c = name.strip().split(' ')
    c = [i for i in c if len(i)>0]
    if len(c)==0:
        c = ['-','-']
    elif len(c) == 1:
        c.append('-')
    elif len(c)>2:
        c = [c[0], ' '.join(c[1:])]
    return c[0], c[1]

mem = {}

def getTagId(ro, ru, key):
    ob = Tags.objects(select=key, ro=ro)
    if ob:
        return ob.get().clean_data()['_id']
    new_Tags = {
		  "select": key,
		  "ro": ro,
		  "ru": ru,
		  "en": "-",
		  "is_active": True
        }
    comment = Tags(**new_Tags)
    comment.save()
    return comment.clean_data()['_id']

def parseActivitati(a):
    a = [[j.strip() for j in i.split('/')] for i in a.split(',')]
    a = [j+['-'] if len(j)==1 else j[:2] for j in a]
    a = [getTagId(i[0],i[1],'activity_types') for i in a]
    return a

def getCoordinates(text):
    text = text.replace('strada','str').replace('Strada','str').replace('str','Strada')
    text = text.replace('bulevardul','bd').replace('bd','bulevardul')
    text = requote_uri(text)# text.replace(' ','%20')#urllib.parse.quote_plus(text)
    
    url = "https://info.iharta.md:6443/arcgis/rest/services/locator/CompositeLoc/GeocodeServer/findAddressCandidates?SingleLine={}&City=Chisinau&maxLocations=5&f=pjson"
    resp = requests.get(url=url.format(text))#,params=[('SingleLine',text)])
    print(url.format(text))
    data = resp.json()
    coord = None
    if len(data['candidates'])>0:
        data['candidates'] = sorted(data['candidates'], key=lambda x:x['score'], reverse=True)
        coord = data['candidates'][0]
    return coord

def parseRow(row):
    it = {}
    for k,v in row.items():
        if k not in mp:
            continue
        it[mp[k]] = v
    it['activity_types'] = parseActivitati(it['activity_types'])
    it['email'] = parseEmail(row)
    it['phone'] = parsephone(it['phone'])
    last, first = parseName(it['last_name'])
    it['last_name'] = last
    it['first_name'] = first
    it['last_tempreture'] = it['last_tempreture'].strip()
    it['last_tempreture'] = 36 if len(it['last_tempreture'])==0 else float(it['last_tempreture'])
    it['password'] = it['phone']
    it['aggreed_terms'] = it['aggreed_terms'].find('Da')>=0
    it['new_volunteer'] = it['new_volunteer'].lower().find('nu')>=0
    it['sent_photo'] = it['sent_photo'].lower().find('da')>=0
    it['need_sim_unite'] = it['need_sim_unite'].lower().find('da')>=0
    it['team'] = getTagId(it['team'] ,'-','team')
    it['age'] = getTagId(it['age'] ,'-','age')
    it['offer'] = getTagId(it['offer'] ,'-','offer')
    ro, ru = (it['zone_address'].split('/') + ['-'])[:2]
    it['zone_address'] = getTagId(ro.strip() ,ru.strip(),'sector')
    ro, ru = it['availability'].split('/')
    it['availability'] = getTagId(ro.strip() ,ru.strip(),'availability')
    coord = getCoordinates(it['address'])
    if coord:
        it['latitude'] = coord['location']['x']
        it['longitude'] = coord['location']['y']
        it['address_old'] = it['address']
        it['address'] = coord['address']
    return it



def parseFile(json_url, begin, end):
	resp = requests.get(url=json_url)
	data = resp.json()

	cols = max([int(i['gs$cell']['col']) for i in data['feed']['entry']])
	rows = max([int(i['gs$cell']['row']) for i in data['feed']['entry']])
	df = [['' for i in range(cols)] for j in range(rows)]
	for i in data['feed']['entry']:
	    col = int(i['gs$cell']['col'])
	    row = int(i['gs$cell']['row'])
	    #print(i['gs$cell'])
	    df[row-1][col-1] = i['gs$cell']['inputValue']

	lb = [df[1][i] if df[0][i]=='' else df[0][i] for i in range(cols)]
	lb = [i[:15] for i in lb]

	rr = [{lb[i]:v for i,v in enumerate(j)} for j in df[3:]]
	ids = []
	begin = int(begin)
	end = int(end)
	for row in rr[begin:end]:#add 
		item = parseRow(row)
		ob = Volunteer.objects(phone=item['phone'], is_active=True)
		if not ob:
			comment = Volunteer(**item)
			comment.save()
			ids.append(comment.clean_data())
			#return jsonify(comment.clean_data()['_id'])

	return jsonify(ids)
		

