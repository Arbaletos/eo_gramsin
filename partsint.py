#!/usr/bin/python3
#coding=utf-8

import sys
from copy import copy
from conlib import *
from time import time

def print_l(li,delim = ','):
  return delim.join([str(l) for l in li])

def kon(li):
  """Conjunction of list values"""
  return len(li)==sum([bool(x) for x in li])

def dnf(li):
  """count li as dnf and return result"""
  return sum([kon(x) for x in li])>0

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

  def parse(self):
    if not self.frazoj: return []
    par = self.frazoj[0].parse(None, True)
    return par
     
   # return self.frazoj[0].parse(None)
 
  def fragmentu(self, vortoj):
    def rule(vort):
      rules = [('vort',','), 
               ('pos','CCONJ'), 
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
    nret = [c for c in ret if c.tokens]
    ret = nret
    for f in range(len(ret)):
      curret = ret+[None]
      ret[f].pred = curret[f-1]
      ret[f].next = curret[f+1]
    return ret

class Frazo:
  """Phrase, consists of words"""
  
  def __init__(self,vortoj):
    self.simpligu(vortoj[:])

  def __str__(self):
    return print_l(self.tokens,' ')

  def struct(self):
    return ' '.join(['|'+str(t)+'|' for t in self.tokens])
    

  def parse(self,cont,simple = False):
    ret = []
    if not cont: cont = Context()
    adp = 0 
    for t in self.tokens:
      """Roles Putinismus!"""
      if t.pos == 'ADP':
        adp = 1
        cont.add(t,'COM')
      elif adp and t.type == 'NOUN':
        cont.add(t,'COM_NOUN')
        adp = 0
      elif adp and t.type == 'ADJ':
        cont.add(t,'COM_ADJ')
        adp = 0
      elif t.type == 'NOUN':
        if t.case=='ACC': cont.add(t,'OBJ')
        elif t.case=='NOM': cont.add(t,'SUBJ')
        else: return False
      elif t.type == 'ADJ': cont.add(t,'DESC')
      elif t.type == 'ADV': cont.add(t,'OBS')
      elif t.type == 'VERB':
        if t.mode == 'IND': cont.add(t,'ROOT')
        if t.mode == 'CON': cont.add(t,'ROOT')
        if t.mode == 'IMP': cont.add(t,'IMP')
        if t.mode == 'INF':  cont.add(t,'INF')

    if cont.validate():
      if self.next:
#        print('Context Enrich')
        next = self.next.parse(Context(cont),simple)
#        if next: print('Enrich True')
#        else: print('Enrich False')
        for n in next:
          ret.append(n)

        if cont.finished(simple):
#          print('Complex Fork')
          next = self.next.parse(None,False)
#          if next: print('Complex Fork True')
#          else: print('Complex Fork False')
          for n in next:
            ret.append([cont.finish()]+n)
        return ret
      if cont.finished(simple):    
        return [[cont.finish()]]
    return []
   
  def simpligu(self,vortoj):
    self.tokens = []
    cur = None
    t_id = 0
    print(print_l(vortoj,' '))
    for v in vortoj:
      new = True
      if v.type=='NOUN':
        if cur and cur.type in ['DET','ADJ'] and cur.cc_match(v):
          cur.add(v,True)
          new = False
      elif v.type=='ADJ':
        if cur and cur.type in ['NOUN','DET','ADJ'] and cur.cc_match(v) and not cur.full:
          cur.add(v,cur.pos!='NOUN')
          cur.full = True
          new = False
          cur.full = True
      if new and v.type in ['NOUN','ADJ','VERB','SCONJ','ADP','ADV','DET','PREP']:
        cur = Token(t_id,[v]) 
        t_id+=1
        self.tokens.append(cur)
        if v.type == 'ADJ': cur.full = True
        if v.type == 'DET': cur.det = True

class Context:
  """Phrase shit"""

  def __init__(self,copy=None):
    roles = ['OBJ','SUBJ','ROOT','DESC','COM','INF','COM_DESC','OBS']
    if copy:
      self.comps = {r:copy.comps[r][:] for r in roles}
      self.pat = copy.pat
      self.iva = copy.iva
      self.verb = copy.verb[:]
      self.imp = copy.imp
    else:
      self.comps = {r:[] for r in roles}
      self.pat = ''
      self.verb = ['TRAN','INTR','PRED']
      self.imp = False
      self.iva = 0

  def __str__(self):
    return self.pat + ';\n' + \
           '  '+self.print_key('ROOT')+"; TYPE:"+print_l(self.verb)+";\n" + \
           '  '+self.print_key('SUBJ')+';\n' + \
           '  '+self.print_key('OBJ')+';\n' + \
           '  '+self.print_key('OBS')+';\n' + \
           '  '+self.print_key('DESC')+';\n' + \
           '  '+self.print_key('COM')+';\n'
  
  def print_key(self,key):
    
    return key+':'+print_l(self.comps[key])

  def up_pat(self,arg):
    if not self.pat.endswith(arg):
      self.pat = self.pat+arg

  def add(self,t,role):
    try:
      if role=='IMP':
        role='ROOT'
        self.imp = True
      if role=='OBS' and self.iva == 2: self.iva = 3
      if role=='SUBJ': self.up_pat('N')
      if role=='ROOT': 
        if self.iva==1: self.iva = 2
        if self.pat=='NV': self.pat+='V'
        else: self.up_pat('V')
      if role=='INF' and not self.iva: self.iva = 1
      if role.startswith('COM_'):
        self.comps['COM'][-1].add(t)
      elif role.startswith('COM'):
        self.comps[role].append(Token(t.ind,t.vortoj[:]))
      else:
        self.comps[role].append(t)
    except:
      self.comps[role] = [t]

  def validate(self):
    obj = self.obj_est()
    #print(str(self))
    unvalid = [[obj,self.pat=='NVN'],
               [len(self.pat)>=3,self.pat not in ['NVV','VNV','NVN']]]
    return (not dnf(unvalid))
        
  def finished(self,simple=False):
    af = self.adj_full()
    obj = self.obj_est()
    root = bool(self.comps['ROOT'])
    subj = bool(self.comps['SUBJ'])
    inf = bool(self.comps['INF'])
    imp = self.imp

    self.fin = [['PRED',self.pat == 'NVN', 
                 af, not obj, root, subj or imp],
                ['PRED', not subj, not obj, root, self.iva],
                ['INTR',self.pat in ['NV','NVV','VN','VNV','V'], 
                 af, not obj, root,subj or imp],
                ['TRAN',self.pat in ['NV','VN','VNV','NVV','V'], 
                 af, obj, root, subj or imp]]

    if simple:
      self.fin.append(['STAT',af, not root])
      self.fin.append(['NAT', root, not subj, not obj, not inf])

    self.verb = [k[0] for k in self.fin if kon(k)]

    return self.validate() and dnf(self.fin)
 
  def finish(self):
    if not self.finished(): return []
    return self

  def obj_est(self):
    c = self.comps
    if c['OBJ']: return True
    for d in c['DESC']:
      if d.case=='ACC':
        return True
    return False

  def adj_full(self):
    c = self.comps
    for d in c['DESC']:
      case = 'SUBJ'
      if d.case=='ACC':
        case = 'OBJ'
      adj = self.adj_count(d.count,case)
      if not adj: return False
    return True

  def adj_count(self,count,case):
    if count=='SING' and not len([t for t in self.comps[case] if t.count=='SING']):
      return False 
    if count=='PLUR' and (len(self.comps[case])<1 or \
       self.comps[case][0].count != 'PLUR'):
      return False
    return True
 
class Token:
  """Word, consits of grammems"""

  def add(self, vort, mv=False):
    self.vortoj.append(vort)
    if mv:
      self.main = self.vortoj[-1]

  def cc_match(self,v):
    return self.main.cc_match(v)

  def __init__(self, t_id, vortoj, mvort=0):
    self.vortoj = vortoj
    self.main = vortoj[mvort]
    self.det = False
    self.full = False
    self.ind = t_id

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
  #dict for get grams from tagname
  gram_tag = {'PROPN':['SING','NOM','NOUN','UNDEF','UNDEF'],
              'PROPA':['SING','ACC','NOUN','UNDEF','UNDEF'],
              'NSN':['SING','NOM','NOUN','UNDEF','UNDEF'],
              'NPN':['PLUR','NOM','NOUN','UNDEF','UNDEF'],
              'NSA':['SING','ACC','NOUN','UNDEF','UNDEF'],
              'NPA':['PLUR','ACC','NOUN','UNDEF','UNDEF'],
              'ASN':['SING','NOM','ADJ','UNDEF','UNDEF'],
              'APN':['PLUR','NOM','ADJ','UNDEF','UNDEF'],
              'ASA':['SING','ACC','ADJ','UNDEF','UNDEF'],
              'APA':['PLUR','ACC','ADJ','UNDEF','UNDEF'],
              'PRSN':['SING','NOM','NOUN','UNDEF','UNDEF'],
              'PRPN':['PLUR','NOM','NOUN','UNDEF','UNDEF'],
              'PRUN':['UNDEF','NOM','NOUN','UNDEF','UNDEF'],
              'PRSA':['SING','ACC','NOUN','UNDEF','UNDEF'],
              'PRPA':['PLUR','ACC','NOUN','UNDEF','UNDEF'],
              'PRUA':['UNDEF','NOM','NOUN','UNDEF','UNDEF'],
              'PRSPSN':['SING','NOM','ADJ','UNDEF','UNDEF'],
              'PRPPSN':['SING','NOM','ADJ','UNDEF','UNDEF'],
              'PRUPSN':['SING','NOM','ADJ','UNDEF','UNDEF'],
              'PRSPPN':['PLUR','NOM','ADJ','UNDEF','UNDEF'],
              'PRPPPN':['PLUR','NOM','ADJ','UNDEF','UNDEF'],
              'PRUPPN':['PLUR','NOM','ADJ','UNDEF','UNDEF'],
              'PRSPSA':['SING','ACC','ADJ','UNDEF','UNDEF'],
              'PRPPSA':['SING','ACC','ADJ','UNDEF','UNDEF'],
              'PRUPSA':['SING','ACC','ADJ','UNDEF','UNDEF'],
              'PRSPPA':['PLUR','ACC','ADJ','UNDEF','UNDEF'],
              'PRPPPA':['PLUR','ACC','ADJ','UNDEF','UNDEF'],
              'PRUPPA':['PLUR','ACC','ADJ','UNDEF','UNDEF'],
              'INTDSN':['SING','NOM','NOUN','UNDEF','UNDEF'],
              'INTDPN':['PLUR','NOM','NOUN','UNDEF','UNDEF'],
              'INTDSA':['SING','ACC','NOUN','UNDEF','UNDEF'],
              'INTDPA':['PLUR','ACC','NOUN','UNDEF','UNDEF'],
              'INTPRUN':['UNDEF','NOM','NOUN','UNDEF','UNDEF'],
              'INTPRUA':['UNDEF','NOM','NOUN','UNDEF','UNDEF'],
              'INTASN':['SING','NOM','ADJ','UNDEF','UNDEF'],
              'INTAPN':['PLUR','NOM','ADJ','UNDEF','UNDEF'],
              'INTASA':['SING','ACC','ADJ','UNDEF','UNDEF'],
              'INTAPA':['PLUR','ACC','ADJ','UNDEF','UNDEF'], 
              'INDDSN':['SING','NOM','DET','UNDEF','UNDEF'],
              'INDDPN':['PLUR','NOM','DET','UNDEF','UNDEF'],
              'INDDSA':['SING','ACC','DET','UNDEF','UNDEF'],
              'INDDPA':['PLUR','ACC','DET','UNDEF','UNDEF'],
              'INDPRUN':['UNDEF','NOM','NOUN','UNDEF','UNDEF'],
              'INDPRUA':['UNDEF','NOM','NOUN','UNDEF','UNDEF'],
              'INDASN':['SING','NOM','ADJ','UNDEF','UNDEF'],
              'INDAPN':['PLUR','NOM','ADJ','UNDEF','UNDEF'],
              'INDASA':['SING','ACC','ADJ','UNDEF','UNDEF'],
              'INDAPA':['PLUR','ACC','ADJ','UNDEF','UNDEF'], 
              'DEMDSN':['SING','NOM','DET','UNDEF','UNDEF'],
              'DEMDPN':['PLUR','NOM','DET','UNDEF','UNDEF'],
              'DEMDSA':['SING','ACC','DET','UNDEF','UNDEF'],
              'DEMDPA':['PLUR','ACC','DET','UNDEF','UNDEF'],
              'DEMPRUN':['UNDEF','NOM','NOUN','UNDEF','UNDEF'],
              'DEMPRUA':['UNDEF','NOM','NOUN','UNDEF','UNDEF'],
              'DEMASN':['SING','NOM','ADJ','UNDEF','UNDEF'],
              'DEMAPN':['PLUR','NOM','ADJ','UNDEF','UNDEF'],
              'DEMASA':['SING','ACC','ADJ','UNDEF','UNDEF'],
              'DEMAPA':['PLUR','ACC','ADJ','UNDEF','UNDEF'], 
              'VPR':['UNDEF','UNDEF','VERB','IND','PRESENT'],
              'VPS':['UNDEF','UNDEF','VERB','IND','PAST'],
              'VFT':['UNDEF','UNDEF','VERB','IND','FUTURE'],
              'VIN':['UNDEF','UNDEF','VERB','INF','UNDEF'],
              'VDM':['UNDEF','UNDEF','VERB','IMP','UNDEF'],
              'VCN':['UNDEF','UNDEF','VERB','CON','UNDEF']
} 
             
  verb_mode = {'VPR':'IND','VPS':'IND','VFT':'IND','VIN':'INF','VDM':'IMP','VCN':'CON'}
  verb_time = {'VPR':'PRESENT','VPS':'PAST','VFT':'FUTURE'}
  counts = {'S':'SING','P':'PLUR','U':'UNDEF'}
  cases = {'N':'NOM','A':'ACC','U':'UNDEF'}

  def get_gram(s):
    try:
      return s.gram_tag[s.tag]
    except:
      ng = ['UNDEF','UNDEF',s.pos,'UNDEF','UNDEF']
      #      Count,  Case,   Type,   Mode,   Time
      s.gram_tag[s.tag] = ng
      return ng

  def __init__(self, conlu):
    self.vort = conlu[1]
    self.stem = conlu[2]
    self.pos = conlu[3]
    self.tag = conlu[4]

    self.count, self.case, self.type, self.mode, self.time = self.get_gram()

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


def main():
  now = time()
  if len(sys.argv)<2:  filename = 'nivelo3'
  else: filename = sys.argv[1]
  inp = parsecon('con/in/'+filename+'.con')
  #KOSTYL
  inputo = [('1','NUM'),('.','PUNCT')]
  outputo = []


  #print(rules)
  all = 0
  good = 0
  mul = 0
  shitlist = []
  while len(inp)>0:
    cursent = Sent(getsent(inp))
    print(cursent.struct())
    par = cursent.parse()
    if par:good+=1
    else:
      print('\tUnparsed!')
      shitlist.append(cursent) 
    all+=1
    if len(par)>1: mul += 1
    for i in range(len(par)):
      print('Variant '+str(i+1))
      print(print_l(par[i],'\n'))
    inp = inp[len(cursent):]
    #input()
  print(print_l(shitlist,'\n'))
  print('Time elapsed:'+str(time() - now))
  print('All Sents:'+str(all)+'; Good Sents:'+str(good)+'; Multiple sent:' + str(mul))
  print('Accuracy:' + str(100*good/all)+'%')
if __name__=='__main__': main()
