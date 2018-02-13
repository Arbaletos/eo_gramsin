#/usr/bin/python3
#coding=utf-8

try:
  import xml.etree.cElementTree as etree
except ImportError:
  import xml.etree.ElementTree as etree
import json
import sys
from spacy.lang.eo import Esperanto

TEI = '{http://www.tei-c.org/ns/1.0}'

def numparse(instr):
  """Parses Esperanto numerals """
  edict = {'unu':1,'du':2,'tri':3,'kvar':4,'kvin':5,'ses':6,'sep':7,'ok':8,'naŭ':9}
  mdict = {'dek':10,'cent':100}
  cstr = instr[:]
  if len(kombiki(cstr,edict,mdict))>0:
    return ['NUM']
  return [] 


def kombiki(cstr,kom_dict, fin_dict):
  ret = []
  for kom in kom_dict.keys():
      for fin in fin_dict.keys():
        if kom+fin==cstr:
          return [kom_dict[kom]+fin_dict[fin]]
  return ret

      
def korelativoj(instr):
  """Parses correlatives in esperanto"""
  cstr = instr[:]
  kom_dict = {'ki':'INT','i':'IND','ĉi':'TOT','neni':'NEG','ti':'DEM'}
  fin_dict = {'a':'ASN', \
    'o':'PRN','u':'DSN', \
    'e':'ADV','el':'ADV','en':'ADD', \
    'es':'DPS','om':'DQU', \
    'am':'ADV','al':'ADV','on':'PRA', \
    'aj':'APN','an':'ASA',\
    'ajn':'APA','uj':'DPN',\
    'un':'DSA','ujn':'DPA'}
  return kombiki(cstr,kom_dict,fin_dict)

def pronomoj(instr):
  """Parses pronouns"""
  cstr = instr[:]
  kom_dict = {'m':'PR',
    'v':'PR', \
    'c':'PR', \
    'l':'PR', \
    'ŝ':'PR', \
    'ĝ':'PR', \
    's':'PR', \
    'n':'PR', \
    'il':'PR', \
    'on':'PR'}
  fin_dict = {'i':'N', \
    'in':'A', \
    'ia':'PSN', \
    'ian':'PSA', \
    'iaj':'PPN', \
    'iajn':'PPA'}
  return kombiki(cstr,kom_dict,fin_dict)

def qtrick(text):
  """The most bitchesfull trick in all this code. It changes all putin' kind shits with putinq shits, so we can parse it. ahahaHAHAHA!"""
  i = 0
  qu = False
  ret = text
  while text.find("'",i+1)>=0:
    i = text.find("'",i+1)
    if qu:
      qu = False
      continue
    if text[i-1].isalpha():
      ret = text[:i]+'q'+text[i+1:]
    else:
      qu = True
  return ret

def gettag(cword):
  ret = []
  global new_sent
  if cword.is_digit:
    return ['NUM']
  if cword.is_punct:
    return ['PUNCT']
  if not new_sent:
    if cword.text[0].isupper():
      nomo = cword.text
      ACC = False
      if cword.text.endswith('y'):
        return(['FPROPN'])
      if nomo.endswith('on'):
        print ('in putin we trust!')
        nomo = nomo[:-1]
        ACC = True
      if nomo not in names_list:
        names_list.append(nomo)
      if ACC:
        return(['PROPA'])
      return(['PROPN']) 
  new_sent = False
  word = cword.text[:].lower()
  ret+=numparse(word)
  ret+=korelativoj(word)
  ret+=pronomoj(word)

  if len(word)==1 or cword.text[-1]=='.':
    ret = ['SYM']

  if word in dict.keys():
    ret+=dict[word]

  if len(ret)==0:
    for fin in fin_dict.keys():
      if word.endswith(fin):
        ret+=[fin_dict[fin]]
  if len(ret)==0:
    if cword.text[0].isupper():
      nomo = cword.text
      ACC = False
      if nomo.endswith('on'):
        print ('in putin we trust!')
        nomo = nomo[:-1]
        ACC = True
      if nomo not in names_list:
        names_list.append(nomo)
      if ACC:
        return(['PROPA'])
      return(['PROPN']) 
    return(['X'])
  return ret

def postparse(sent):
  """Adding POS-TAG, lemmas, changing qu and y trick back. id, vort, NPOS"""
  """next: id vort lemm XPOS NTAG"""
  ret = []
  for ent in sent:
      if ent[1] in names_list:
        ent[2] = ['PROPN']
      if ent[1].endswith('y'):
        ent[1] = ent[1][0:-1]
      else:
        if ent[1].endswith('q'):
          ent[1] = ent[1][0:-1]+"'"
      for tag in ent[2]:
        ret.append([])
        ret[-1].append(str(ent[0])) 
        ret[-1].append(ent[1])
        if tag in convert_dict.keys():
          ret[-1].append(ent[1][0:0-convert_dict[tag][1]])
          ret[-1].append(convert_dict[tag][0])
        else:
          ret[-1].append(ent[1])
          ret[-1].append(tag)
        ret[-1].append(tag)
  return ret

def parsesent(sent):
  ret = []
  sent = qtrick(sent)
  words = nlp(sent)
  cont = sent
  id = 1
  global new_sent
  new_sent = True
  comm_dict = {'"':False,"'":False}
  for word in words:
    ret.append([id,word.text,gettag(word)])
    id+=1
    if word.text[0] in comm_dict.keys():
      if comm_dict[word.text[0]]:
        comm_dict[word.text[0]] = False
      else:
        comm_dict[word.text[0]] = True
        new_sent = True
        id = 1
    if word.text[0] in ['.','!','?']:
      new_sent = True
      id = 1
  return postparse(ret)

def output(conl):
  for i in conl:
    s = '\t'.join(i)
    print(s)
    out.write(s+'\n')
  out.write('\n')
#|-------------------------->╔═╦═╗║ ║ ║╠═╬═╣╚═╩═╝

dict = {}
names_list = []
undef = []
out = ''
nlp = Esperanto()

dictcsv = open("dict.csv","r")

convert_dict = {   'NSN':['NOUN',1],  'NPN':['NOUN',2],
'NSA':['NOUN',2],  'NPA':['NOUN',3],  'ASN':['ADJ',1],
'APN':['ADJ',2],   'ASA':['ADJ',2],   'APA':['ADJ',3],
'ADE':['ADV',1],   'ADD':['ADV',2],   'VPR':['VERB',2],
'VFT':['VERB',2],  'VPS':['VERB',2],  'VIN':['VIN',1],
'VDM':['VERB',1],  'VCN':['VERB',2],  'PRN':['PRON',0],
'PRA':['PRON',1],  'PRPSN':['DET',1], 'PRPSA':['DET',2],
'PRPPN':['DET',2], 'PRPPA':['DET',3], 'FPROPN':['PROPN',0],
'PROPA':['PROPN',1]}

kom = ['INT','IND','TOT','NEG','DEM']
fin = ['ASN','PRN','DSN','ADV','ADV',\
  'ADD','DPS','DQU','ADV','ADV','PRA',\
  'APN','ASA','APA','DPN','DSA','DPA']

for k in kom:
  for f in fin:
    if f in ['APN','ASA','DPN','DSA']:
      convert_dict[k+f] = ['DET',1]
    elif f in ['DPA','APA']:
      convert_dict[k+f] = ['DET',2]
    elif f in ['DSN','ASN','DQU','DPS']:
      convert_dict[k+f] = ['DET',0]
    elif f == 'PRA':
      convert_dict[k+f] = ['PRON',1]
    elif f == 'PRN':
      convert_dict[k+f] = ['PRON',0]
    elif f == 'ADV':
      convert_dict[k+f] = ['ADV',0]
    elif f == 'ADD':
      convert_dict[k+f] = ['ADV',1]

fin_dict = { "'":'NSN',"q":"NSN",
'o':'NSN','oj':'NPN','on':'NSA','ojn':'NPA',
'a':'ASN','aj':'APN','an':'ASA','ajn':'APA',
'e':'ADE','en':'ADD','as':'VPR','os':'VFT',
'is':'VPS','i':'VIN','u':'VDM','us':'VCN'}

for line in dictcsv:
  c = line[:-1].split(',')
  dict[c[0]] = c[1:]
  dict['mal'+c[0]] = c[1:]
dictcsv.close()

for i in range (1, len(sys.argv)):
  filename = 'corp/in/'+sys.argv[i]+'.xml'
  out = open('out/'+sys.argv[i]+'.con',"w")
  tree = etree.parse(filename)
  root = tree.getroot()
  for s in tree.iter(tag = TEI+'p'):
    text = s.text
    for t in s:
      c = t.text.split()
      for i in range(len(c)):
        c[i] = c[i]+'y'
#It is 'y-trick' - as a q-trick, aber anderer.
      text+=' '.join(c)
      text+=t.tail
    print (text)
    if len(text) > 0:
       print(text)
       output(parsesent(text))
  out.close
out = open('out/stdout.out',"w")
while True:
  sent = input("Input esperanto sentense or q to exit!\n")
  if (sent=='q'):
    out.close()
    exit()
  output(parsesent(sent))
  undef = []


