#!/usr/bin/python3
#coding=utf-8

import sys

"""In Data:
Word - Stem - XPOS
[num,dot]      
[SENT]

SENT RULES:

SENT:- S + AS DOT
AS:-CONJ+AS
AS:-e
SENT:- NUM DOT

SINT RULES:
S:- PV + FN
S:- FN + PV
AN:- AG + N
AN:- N + AG
AG:- A + AG
AG:- e
FN:- ART + AN
ART:- D
ART:- e

TERM Rules
CONJ - Word(kaj)
D - Word(la)
PV:- POSX(VPR)
A:-  POSX(ASN)
N:-  POSX(NSN)
NUM :- POSX(NUM)
DOT :- WORD(.)

ROLE ROLES:
A in AG is ATTRIBUTIVE ADJECTIVE
N in FN is SUBJecive
PV in S


M - МАГАЗ - лист
S - СТАЧИНА - лист
Структурка: 
Дикт. Ключ - нетерминал. Значение - массив варьянтов.
Варьянт - совокупность других нетерминалов или терминалов!
терминалы:
EPS - просто-напросто вынимвает себя из магазина.
POSX/Putin - вынимается, если после пусикс в магазине равен пусиксу в стечаре
VORT/Putin - вынимается, если слово бомжа равно слову в стечаре.
"""

def parse(inputo,mag,out):
  if len(inputo)>0:
    print(mag)
    """Terminal Section!"""
    if len(mag)==0:
      return False
    cur = mag.pop()
    if cur.startswith('POSX'):
      if cur[5:]!=inputo[0][1]:
        return False
      if cur[5:]==inputo[0][1] and parse(inputo[1:],mag,out):
        return True
      return False
    if cur.startswith('VORT'):
      if cur[5:]!=inputo[0][0]:
        return False
      if cur[5:]==inputo[0][0] and parse(inputo[1:],mag,out):
        return True
      return False
    if cur.startswith('EPS'):
      return parse(inputo[:],mag,out)
    """Non-Terminal Section!"""
    mag.append(cur)
    nterm = mag.pop()
    for r in rules[nterm]:
      if parse(inputo[:],mag[:]+r,out):
        out.append([nterm,r])
        return True
    return False
  if len(mag)==0:
    return False
  return True

rules = {'COLON':[['VORT/:']],'COMMA':[['VORT/,']]}
#KOSTYL
inputo = [('1','NUM'),('.','PUNCT')]
outputo = []
mag = ['SENT']

for line in open('sint_in/gram'):
  head = line[:-1].split(':')[0]
  tail = line[:-1].split(':')[1].split(',')
  tail.reverse()
  if head in rules.keys():
    rules[head] += [tail]
  else:
    rules[head] = [tail]

print(rules)

print(parse(inputo,mag,outputo))
print (outputo)

