#!/usr/bin/python3
#coding=utf-8

import sys

"""In Data:
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
    print(mag,inputo)
    next = input()
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
      if cur[5:]!=inputo[0][0].lower():
        return False
      if cur[5:]==inputo[0][0].lower() and parse(inputo[1:],mag,out):
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
  if len(mag)>0:
    return False
  return True

def getsent(inp):
  for i in range(1,len(inp)):
    if inp[i][0]=='1':
      return inp[:i]
  return inp[:]

def makesent(inp):
  return ' '.join(list(map(lambda x:x[0],inp)))

def makegood(inp,outp):
  ink = inp[:]
  out = outp[:]
  mag = ['SENT']
  ret = [[]]
  ind = 0
  inpd = 0
# print(ink)
#  print(out)
  while len(out)>0:
    cur =  out.pop()[1]
    curm = mag.pop()
#   print(cur)
#   print(curm)
#   print(ret)
    ret[ind].append(curm)
    if cur[len(cur)-1].startswith('POSX') or cur[len(cur)-1].startswith('VORT'):
      ret[ind].append(inp[inpd][0])
      ind+=1 
      inpd+=1
    elif cur[len(cur)-1]=='EPS':
      ret[ind].append('EPS')
      ind+=1
    else:
      for i in range(1,len(cur)):
        ret.insert(ind+1,ret[ind][:])
      mag+=cur
  return ret
      
def pre_gram(rules):
  ret = {}
  for nterm in rules.keys():
    ret[nterm] = []
    for rule in rules[nterm]:
      ret.nterm.append((rule,getstart(rules,nterm,rule)))

rules = {'COLON':[['VORT/:']],'COMMA':[['VORT/,']]}
inp = list(map(lambda x:x.split('\t'),open('sint_in/nivelo2.con').read().split('\n')))

#KOSTYL
inputo = [('1','NUM'),('.','PUNCT')]
outputo = []
mag = ['SENT']

for line in open('sint_in/gram'):
  if line[len(line)-1]=='\n':
    line = line[:-1]
  head = line.split(':')[0]
  tail = line.split(':')[1].split(',')
  tail.reverse()
  if head in rules.keys():
    rules[head] += [tail]
  else:
    rules[head] = [tail]

print(rules)
while len(inp)>0:
  next = input()
  mag = ['SENT']
  outputo = []
  cursent = getsent(inp)
  inp = inp[len(cursent):]
  inputo = list(map(lambda x: (x[1],x[4]),cursent))
  if parse(inputo,mag,outputo):
    log = makesent(inputo)+' - Sucess!\n' + makegood(inputo, outputo)
    print (log)
    
  else:
    log = makesent(inputo)+' - Fail!'
    print (log)
    next = input()

