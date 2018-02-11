#/usr/bin/python3
#coding=utf-8

import xml.etree.ElementTree as etree
import json
import sys

TEI = '{http://www.tei-c.org/ns/1.0}'

def numparse(instr):
  """Parses Esperanto numerals """
  edict = {'unu':1,'du':2,'tri':3,'kvar':4,'kvin':5,'ses':6,'sep':7,'ok':8,'naŭ':9}
  mdict = {'dek':10,'cent':100}
  cstr = instr[:]
  if len(kombiki(cstr,edict,mdict))>0:
    return ['NUM']
  return [] 

def kombini(cstr,kom_dict, fin_dict):
  ret = []
  for kom in kom_dict.keys():
    if cstr.startswith(kom):
      for fin in fin_dict.keys():
        if cstr.endswith(fin) and len(kom)+len(fin) == len(cstr):
          ret.append(kom_dict[kom])
          ret+=fin_dict[fin]
  return ret

def kombiki(cstr,kom_dict, fin_dict):
  ret = []
  for kom in kom_dict.keys():
      for fin in fin_dict.keys():
        if kom+fin==cstr:
          return [kom_dict[kom]+fin_dict[find]]
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
  return kombiki(sctr,kom_dict,fin_dict)

def gettag(cword):
  ret = []
  word = cword[:].lower()
  ret+=numparse(word)
  ret+=korelativoj(word)
  ret+=pronomoj(word)

  if len(word)==1:
    cur = ['SYMB']

  if word in dict.keys():
    ret.append(dict[word])

  if len(ret==0):
    for fin in fin_dict.keys():
      if word.endswith(fin):
        ret+=[find_dict[fin]]

  if cword[0].isupper():
    ret.append(['PROPN']) 
  return ret


def getstem(cword,gram):
  word = cword[:].lower()
  ret = []
  cur = numparse(word)
  if cur!='NAN':
     cur = [cur]
#    gram+=['NUM',cur]
#    ret.append([word[:],gram[:]])
  else:
    cur = korelativoj(word)
  if cur==[]:
#    ret.append([word[:],cur[:]])
    cur = pronomoj(word)
#    ret.append([word[:],cur[:]])

  if len(word)==1:
    cur = ['LITER']
#    ret.append([word[:],'LITER'])
  if len(cur)>0:
    ret.append({"stem":word[:],"gram":cur[:]})
  if word in dict.keys():
#    cur+=dict[word]
#    ret.append([word[:],gram[:]])
    ret.append({"stem":word[:],"gram":dict[word]})
#  if len(cur)>0:
#  ret.append({"stem":word[:],"gram":cur[:]})
  if cword[0].isupper():
  #  ret.append([word,['NAMED_ENT']])
    ret.append({"stem":word,"gram":['NAMED_ENT']}) 
#  if len(ret)>0:
#    return ret

  if len(word)>3 or (len(word)==3 and word[-1] in ['a','e','i','o','u']):
    found = 0
    if word.endswith('as'):
      gram += ['VERB','PRESENT']
      found = 2 
    if word.endswith('is'):
      gram += ['VERB','PAST']
      found = 2 
    if word.endswith('os'):
      gram += ['VERB','FUTURE']
      found = 2 
    if word.endswith('us'):
      gram += ['VERB','COND']
      found = 2 
    if word.endswith('u'):
      gram += ['VERB','DOM']
      found = 1 
    if word.endswith('i'):
      gram += ['VERB','INF']
      found = 1 
    if word.endswith('n'):
      gram.append('ACC')
      word = word[:-1]
    if word.endswith('j'):
      gram.append('PLUR')
      word = word[:-1]
    if word.endswith('o') or word.endswith("'"):
      gram.append('NOUN')
      found = 1 
    if word.endswith('a'):
      gram.append('ADJ')
      found = 1 
    if word.endswith('e'):
      if 'PLUR' not in gram:
        gram.append('ADV')
        found = 1 
    if found > 0:
#      ret.append([word[:-found],gram[:]])
      ret.append({"stem":word[:-found],"gram":gram[:]}) 
  if len(ret)<1:
#    ret.append([word,['UNDEF']])
    ret.append({"stem":word[:],"gram":['UNDEF']}) 
#    undef.append(word) 
  return ret

def parsesent(sent):
  #undef = []
  ret = []
  words = sent.split(' ')
  cont = sent
  word = ''
  w_size = 3
  curcont = ""
  for i in range(0,len(words)):
    word = words[i]
    w_s = 0
    w_e = len(words)-1
    if w_size < i:
      w_s = i-w_size
    if i+w_size<len(words)-1:
      w_e = i - w_size
    curcont = words[w_s:w_e]
    cw = ''
#    word = word.lower()
    for c in word:
      if c.isalpha() or c=="'":
        cw = cw + c
      else:
        stem = [[c,['PUNKT']]]
        stem = [{"stem":c,"gram":['PUNKT']}] 
        print ("%s:%r" %(c, stem)) 
        ret.append({'word':c,'morph':stem})
    if len(cw)>0:
      grams = []
#      stem = getstem(cw,grams)
      tag = gettag(cw)
      print ("%s:%r" %(cw, tag))
      ret.append({'word':cw,'tag':tag})

  if len(undef)>0:
    print ('Estas maldefinitaj vortoj. Ĉu vi volas Defini? (y/n)')
    if input()!='n':
      dictcsv = open("dict.csv","a")
      for word in undef:
        print ('')
        print ('Konteksto:"'+cont+'"')
        print ('Detala Konteksto:%r' % curcont)
        print ('Vorto:"'+word+'"')
        print ('Tajpu gramememoj por cxi tiu vorto aux tajpu nenion.')
        gram = input()
        if len(gram)>0:
          gram = gram.split(',')
          dict[word] = gram[:]
          dictcsv.write(','.join([word]+gram[:])+'\n')
          print("Informatio estas aldonita.")
        else:
          print("Nenio estis farita.")
  return ret
#|-------------------------->╔═╦═╗║ ║ ║╠═╬═╣╚═╩═╝

dict = {}
undef = []
out = ''

dictcsv = open("dict.csv","r")

fin_dict = {
'o':'NSN','oj':'NPN',:'on':'NSA','ojn':'NPA',
'a':'ASN','aj':'APN','an':'ASA','ajn':'APA',
'e':'ADE','en':'ADD',:'as':'VPR','os':'VFT',
'is':'VPS','i':'VIN','u':'VDM','us':'VCN'}

for line in dictcsv:
  c = line[:-1].split(',')
  dict[c[0]] = c[1:]
  dict['mal'+c[0]] = c[1:]
dictcsv.close()

for i in range (1, len(sys.argv)):
  filename = 'corp/in/'+sys.argv[i]+'.xml'
  out = open('out/'+sys.argv[i]+'.json',"w")
  tree = etree.parse(filename)
  root = tree.getroot()
  out.write('[')
  for s in tree.iter(tag = TEI+'p'):
    if len(s.text) > 0:
      out.write('[')
      out.write(json.dumps(parsesent(s.text)))
      out.write(']')
    undef = []
  out.write(']')
  out.close
out = open('out/stdout.json',"w")
out.write('[')
while True:
  sent = input("Input esperanto sentense or q to exit!\n")
  if (sent=='q'):
    out.write(']')
    out.close()
    exit()
  out.write('[')
#  print(parsesent(sent))
  ret = parsesent(sent)
  print (json.dumps(ret, indent=2))
  out.write(json.dumps(ret))
  out.write(']')
  undef = []


