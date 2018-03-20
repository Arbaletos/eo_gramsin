#!/usr/bin/python3
#coding=utf-8

import sys

def parse(sent):
  #grammatically parses la verbum.
  adp_mod = ['INTDSN','INTDPN',NSN,NPN,PRNa
  adpstack = []
  for v in range(len(sent)):
    if sent[v][3] == 'ADP':
      adpstack = ['ADP']+adpstack
    if sent[v][3] in adp_mod:
  print(sent)
  print('')

filename = 'sint_in/ekzemplo.con'
if len(sys.argv)>1:
  filename = 'sint_in/'+sys.argv[1]+'.con'

in_file=open(filename,'r')

curs = []
for l in in_file:
  line = l[:-1]
  if line.startswith('1\t'):
    parse(curs)
    curs.clear()
  curs.append(line.split('\t'))   

    
      


      
