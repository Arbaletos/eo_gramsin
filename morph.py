#/usr/bin/python3
#coding=utf-8

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
  if cword.is_digit:
    return ['NUM']
  if cword.is_punct:
    return ['PUNCT']
  word = cword.text[:].lower()
  ret+=numparse(word)
  ret+=korelativoj(word)
  ret+=pronomoj(word)

  if len(word)==1:
    ret = ['SYM']

  if word in dict.keys():
    ret+=dict[word]

  if len(ret)==0:
    for fin in fin_dict.keys():
      if word.endswith(fin):
        ret+=[fin_dict[fin]]

  if cword.text[0].isupper():
    ret.append('PROPN') 
  
  if len(ret)==0:
    ret.append('X')
  return ret

def parsesent(sent):
  ret = []
  sent = qtrick(sent)
  words = nlp(sent)
  cont = sent
  id = 1
  for word in words:
    ret.append([id,word,gettag(word)])
    id+=1
  return ret

def output(conl):
  for i in conl:
#   print(i)
    print ("%d\t%s\t%s" % (i[0],i[1],','.join(i[2])))
#|-------------------------->╔═╦═╗║ ║ ║╠═╬═╣╚═╩═╝

dict = {}
undef = []
out = ''
nlp = Esperanto()

dictcsv = open("dict.csv","r")

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
#  out = open('out/'+sys.argv[i]+'.json',"w")
  tree = etree.parse(filename)
  root = tree.getroot()
#  out.write('[')
  for s in tree.iter(attr = TEI+'p'):
    if len(s.text) > 0:
       print(s.text)
       output(parsesent(s.text))
#      out.write('[')
#      out.write(json.dumps(parsesent(s.text)))
#      out.write(']')
#    undef = []
#  out.write(']')
#  out.close
#out = open('out/stdout.json',"w")
#out.write('[')
while True:
  sent = input("Input esperanto sentense or q to exit!\n")
  if (sent=='q'):
#    out.write(']')
#    out.close()
    exit()
# out.write('[')
  output(parsesent(sent))
#  ret = parsesent(sent)
#  print (json.dumps(ret, indent=2))
#  out.write(json.dumps(ret))
#  out.write(']')
  undef = []


