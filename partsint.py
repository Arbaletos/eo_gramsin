#!/usr/bin/python3
#coding=utf-8

import sys

class Sent:
  """Sentence, consists of phrases"""
   
  def __init__(self, conlu):
    self.vortoj = [Vort(v) for v in conlu]
    self.frazoj = self.fragmentu(self.vortoj[:])

  def __len__(self):
    return len(self.vortoj)
 
  def __str__(self):
    return ' '.join([str(f) for f in self.frazoj])

  def struct(self):
    return ' '.join(['['+str(f)+']' for f in self.frazoj])
 
  def fragmentu(self, vortoj):

    def rule(vort):
      rules = [('vort',','), 
               ('pos','CONJ'), 
               ('pos','SCONJ')]
      for r in rules:
        if vort[r[0]] == r[1]: return True
      return False

    ret = []
    cur = []
    for v in vortoj:
      if rule(v) and len(cur):
        ret.append(Frazo(cur))
        cur.clear()
      cur.append(v)
    ret.append(Frazo(cur))
    return ret


class Frazo:
  """Phrase, consists of words"""
  
  def __init__(self,vortoj):
    self.simpligu(vortoj[:])

  def __str__(self):
    return ' '.join(['|'+str(t)+'|' for t in self.tokens])

  def simpligu(self,vortoj):
    self.tokens = []
    cur = None
    for v in vortoj:
      new = True
      if v.pos=='NOUN':
        if cur and cur.pos in ['DET','ADJ'] and cur.cc_match(v):
          cur.add(v,True)
          new = False
      elif v.pos=='ADJ':
        if cur and cur.pos in ['NOUN','DET','ADJ'] and cur.cc_match(v) and not cur.full:
          cur.add(v,cur.pos!='NOUN')
          cur.full = True
          new = False
          cur.full = True
      if new and v.pos in ['NOUN','ADJ','VERB','SCONJ','ADP','ADV','DET']:
        cur = Token([v]) 
        self.tokens.append(cur)
        if v.pos == 'ADJ': cur.full = True
        if v.pos == 'DET': cur.det = True

class Token:
  """Word, consits of grammems"""

  def add(self, vort, mv=False):
    self.vortoj.append(vort)
    if mv:
      self.main = self.vortoj[-1]

  def cc_match(self,v):
    return self.main.cc_match(v)

  def __init__(self, vortoj, mvort=0):
    self.vortoj = vortoj
    self.main = vortoj[mvort]
    self.det = False
    self.full = False

  def __str__(self):
    return ' '.join(str(v) for v in self.vortoj)
 
  def __getattr__(self, attr):
    if attr=='m': return self.main
    return self.main.__dict__[attr]

  def __getitem__(self, key):
    return self.main[key]

  def __setitem__(self, key, value):
    self.main[key] = value


class Vort:
  """Word, consits of grammems"""
  sing_tag = ['NSN','NSA','ASN','ASA']
  plur_tag = ['NPN','NPA','APN','APA']
  nom_tag = ['NSN','NPN','ASN','APN']
  acc_tag = ['NSA','NPA','ASA','APA']

  verb_mode = {'VPR':'IND','VPS':'IND','VFT':'IND','VIN':'INF','VDM':'IMP','VCN':'CON'}
  verb_time = {'VPR':'PRESENT','VPS':'PAST','VFT':'FUTURE'}

  def __init__(self, conlu):
    self.vort = conlu[1]
    self.stem = conlu[2]
    self.pos = conlu[3]
    self.tag = conlu[4]

    if self.tag in self.sing_tag: self.count = 'SING'
    elif self.tag in self.plur_tag: self.count = 'PLUR'
    else:  self.count = 'UNDEF'

    if self.tag in self.nom_tag: self.case = 'NOM'
    elif self.tag in self.acc_tag: self.case = 'ACC'
    else:  self.case = 'UNDEF'
    
    if self.tag in self.verb_mode.keys(): self.mode = self.verb_mode[self.tag]
    else: self.mode = 'UNDEF'
      
    if self.tag in self.verb_time.keys(): self.time = self.verb_time[self.tag]
    else: self.time = 'UNDEF'

  def cc_match(self,v):
    """Match lau case and count"""
    return (self.count=='UNDEF' or v.count=='UNDEF' or self.count==v.count) and \
           (self.case=='UNDEF' or v.case=='UNDEF' or self.case==v.case) 
      
  def __str__(self):
    return self.vort
 
  def __getitem__(self, key):
    return self.__dict__[key]

  def __setitem__(self, key, value):
    self.__dict__[key] = value

def getsent(inp):
  for i in range(1,len(inp)):
    if inp[i][0]=='1':
      return inp[:i]
  return inp[:]

def t_in(i,listo,ind):
  """True, if listo[a][ind] = i for at least one element."""
  for a in listo:
    if a[ind]==i:
      return True
  return False

def partparse(inputo):
  def part(inputo):
    ret = [[]]
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
      ekz = []
      cur = []
      next = []
      cur_gram = []
      for w in p:
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

def main():
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
  
    cursent = Sent(getsent(inp))
    print(cursent.struct())
    inp = inp[len(cursent):]
  #  partparse(inputo)
  #  if parse(inputo,mag,outputo):
  #    print (makesent(inputo)+' - Sucess!')
  #   print(outputo)
  #    print(makegood(inputo, outputo))
  #  else:
  #    print (makesent(inputo)+' - Fail!')

if __name__=='__main__': main()
