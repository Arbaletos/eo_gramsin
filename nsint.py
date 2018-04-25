#!/usr/bin/python3
#coding=utf-8

import sys

"""In Data:
"""

def parse(inputo,mag,out):
  if len(inputo)>0:
#    print(mag,inputo)
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

def t_in(i,listo,ind):
  """True, if listo[a][ind] = i for at least one element."""
  for a in listo:
    if a[ind]==i:
      return True
  return False

def partparse(inputo):
  def part(inputo):
    ret = [[]]
    cur = 0
    for i in inputo:
      if i['vort'] == ',':
        if len(ret[cur])>0:
          cur+=1
          ret.append([])
      elif i['pos'] == 'CONJ' or i['pos'] == 'SCONJ':
        cur+=1
        ret.append([i])
      else:
        ret[cur].append(i)
    return ret

  def simple(parto):
    def finish(cur,cur_gram,ekz):
      if len(cur) > 0:
        if len(cur) > 1 or cur[0]['vort']!='la':
          new = {'DEF':False}
          if cur[0]['vort'] == 'la':
            new['DEF'] = True
          gram = cur[len(cur)-1]['tag'][1:]
          if 'A' in cur_gram:
            new['pos'] = 'ADJ'
            new['tag'] = 'A'+gram
          if 'N' in cur_gram:
            new['FULL'] = False
            if 'pos' in new.keys():
              new['FULL'] = True
            new['pos'] = 'NOUN'
            new['tag'] = 'N'+gram
          count = {'S':'SING','P':'PLUR','N':'NOM','A':'ACC'}
          new['count'] = count[gram[0]]
          new['case'] = count[gram[1]]
          new['vort'] = [i['vort'] for i in cur]
          new['stem'] = [i['stem'] for i in cur]
          ekz.append(new)
        else:
          ekz.append(cur[0])

    ret = []
    print('-')
    for p in parto:
#      print(p)
      ekz = []
      cur = []
      next = []
      cur_gram = []
      for w in p:
#        print(w)
#        print(cur)
        if len(next) > 0:
          est = next.pop()
          if est == 'LA' and w['vort'] == 'la':
            cur+=[w]
            continue
          elif est == 'LA':
            est = next.pop()
          if est == 'A' and w['pos']=='ADJ':
            gram = 'N' + w['tag'][1:]
            next = [gram,w['tag']]
            cur+=[w]
#            cur+=[w]
            cur_gram += ['A']
            continue
          if est == 'A' and w['pos']=='NOUN':
            gram = 'A' + w['tag'][1:]
            next = [gram]
            cur+=[w] 
            cur_gram += ['N']
            continue
          if est == w['tag']:
            next.push(est)
            cur+=[w]
            cur_gram += ['A']
            continue
          if est.startswith('A') and w['pos']=='NOUN':
            if len(next)>0 and est[1:]==w['tag'][1:]:
              cur+=[w]
              cur_gram += ['N']
              next.append('PUTIN')
              continue
          next = []
          finish(cur,cur_gram,ekz)
          cur = []
          cur_gram = []
        if w['pos'] == 'ADP':
          next = ['A','N','A','LA']
          ekz +=[w]
#          ekz += [('ADP',w)]
        elif w['vort'] == 'la':
          next = ['A','N','A']
          cur = [w]
        elif w['pos']=='NOUN':
          cur_gram+=['N']
          next = ['A'+w['tag'][1:]]
          cur = [w]
        elif w['pos']=='ADJ':
          next = ['N'+w['tag'][1:],w['tag']]
          cur_gram+=['A']
          cur = [w]
        elif w['pos']=='VERB':
#          ekz += [('VERB',w)]
          ekz +=[w]
          last = ekz[-1]
          time = {'VPR':'PRESENT','VFT':'FUTURE','VPS':'PAST'}
          if w['tag'] in time.keys():
            last['type'] = 'IND'
            last['time'] = time[w['tag']]
          else:
            type = {'VIN':'INF','VDM':'IMP','VCN':'CON'}
            last['type'] = type[w['tag']]
      finish(cur,cur_gram,ekz)
#      aro = [i[0] for i in ekz]
       
#      print(aro) 
      ret.append(ekz) 
    return (ret)

  def parse_import(imp,exp,est):
    for im in range(len(imp)):
      for ex in range(len(exp)):
        if imp[im[2][0]]!=exp[ex[2][0]] and imp[im[0]]==exp[ex[0]]:
          for k in imp[im[0]].keys():
            if imp[im[0]
        
  

  def parse(inp, est, need):
    """ in[] - list of input symbols. est[] - already parsed. need{'}- what symbols which sentpartneed. alt - all other variants. est: [{'ROOT':root,'SUBJ':subj,'TREE':[]}]"""
    """Флективность: 3 варианта глаголов, различная глубина предлогов, различные связки с некстярней"""
    cur = inp[:]
    imp = []
    exp = []
    est = []
    for i in range(len(inp)):
      if len(est) >= 0:
        roots = ['NONE','TRAN','PRED','INTR']
        rooti = {'TRAN':1,'PRED':2,'INTR':3}
        adp = 0
        nom = 0
        acc = 0
        verb = 0
        root = -1
        subj = -1
        obj = -1
        role = '' 
        strukt = []
        est.append(strukt)
        for w in range(len(inp[i])):
          """Первая часть. Частный анализ."""
          word = inp[i][w]
          curw = cur[i][w]

          if word['pos'] == 'ADP':
            """Cистема поиска предлогов может и получше будет. Пока что - глубина 1."""
            adp +=1
            role = 'COM'

          elif word['pos'] == 'NOUN':
            """Существительное. Может быть как объектом, так и субъектом."""
            if adp > 0:
              curw['role'] = 'COM'
              adp = 0
            else:
              if nom==0 and word['case'] == 'NOM' and verb != 2:
                role = 'SUBJ'
                nom+=1
                subj = w
              elif word['case'] == 'ACC' and acc==0 and verb in [0,1]:
                role = 'OBJ'
                acc = 1
                obj = w
              elif nom==1 and word['case'] == 'NOM' and verb == 2:
                role = 'OBJ'
                nom+=1
                obj = w
              else:
                return [] 

          elif word['pos'] == 'ADJ':
            """Определение."""
            role = 'DESC'

          elif word['pos'] == 'VERB': 
            if 'trans' not in word.keys():
              for r in [1,2,3]:
                word['trans'] = roots[r]
                ret = parse(cur,est,need)
                if ret:
                  return ret
              return []
            if word['type'] == 'INF':
              """Инфинитив. Может стать объектом в транзитивном предложении."""
              """Или же субъектом в предикативном предложении (Убивать - плохо)"""
              role = 'INF'
            elif word['type'] == 'IND':
              role = 'ROOT'
              verb = rooti[curw['trans']]
              root = w
          curw['role'] = role
          strukt.append((role,curw)) 
          """Вторая часть - полный анал из"""

        if root>=0:
          mem = strukt[root][1]
          for ind in range(len(strukt)):
            """Infinitives alignment"""
            s = strukt[ind]
            if s[0] == 'INF':
              if mem['trans'] == 'TRAN':
                mem = s[1]
              elif mem['trans'] == 'PRED':
                s[1].role = 'SUBJ'
                strukt[ind][0] = 'SUBJ'
              else:
                return []
          if mem['trans'] == 'TRAN':
            """Transitivus putinus"""
            if obj>=0 and strukt[obj][1]['case']!='ACC':
              return []
            if obj<0:
              imp.append(('OBJ',{'case':'ACC'},(i,root)))
            if subj<0:
              imp.append(('SUBJ',{'case':'NOM'},(i,root)))
          if mem['trans'] == 'INTR':
            if obj>=0:
              return []
            if subj<0:
              imp.append(('SUBJ',{'case':'NOM'},(i,root)))
          if mem['trans'] == 'PRED':
            if subj<0:
              return []
            if obj>=0 and strukt[obj][1]['case']=='ACC':
              return []
            if obj<0:
              imp.append(('OBJ',{'case':'NOM'},(i,root)))
        else:
          """Выбираем куда присобачити безкорневое предложение"""
          imp.append(('ROOT',{},(i)))    
        for s in strukt:
          """Находим все голые дескрипторы"""
          if s[0] == 'DESC':
            father = False
            for s2 in strukt:
              if s2[1]['pos'] == 'NOUN' and s2[1]['case'] == s[1]['case'] and s2[1]['count'] == s[1]['count']:
                father = True
            if not father:
              if s[1]['case'] == 'NOM':
                imp.append(('SUBJ',{'case':'NOM'},(i)))
              else:
                imp.append(('OBJ',{'case':'ACC'},(i)))
               
    #Часть 3:проводим совмещение желаемого с сущим
    parse_import(imp,exp,est):
    if len(imp)>0:
#      print(est)
      return []
    print(cur)
    return cur
 
  def makesent(inp):
    ret = ''
    for i in inp:
      ret+=i['vort']+' '
    return ret
    
  def printres(pars):
    for i in range(len(pars)):
      print('Sentence part 1:')
      sp = pars[i]
      root = ''
      subj = ''
      obj = ''
      if 'ROOT' in sp:
        root = 'Root: '+ sp['TREE'][sp['ROOT']]['in']['vort']
      print(root+subj+obj)
       
  sent = simple(part(inputo))
  print(makesent(inputo))
  sent = (parse(sent,[],[]))
  for p in sent:
    for w in p:
      print(w['vort'])
  
      
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

#print(rules)
while len(inp)>0:
  mag = ['SENT']
  outputo = []
  cursent = getsent(inp)
  inp = inp[len(cursent):]
#  inputo = list(map(lambda x: (x[1].lower(),x[4],x[2].lower(),x[3]),cursent))
  inputo = list(map(lambda x: {'vort':x[1].lower(),'tag':x[4],'stem':x[2].lower(),'pos':x[3]},cursent))
#(VORT,TAG,STEM,POS)
  partparse(inputo)
#  if parse(inputo,mag,outputo):
#    print (makesent(inputo)+' - Sucess!')
#   print(outputo)
#    print(makegood(inputo, outputo))
#  else:
#    print (makesent(inputo)+' - Fail!')

