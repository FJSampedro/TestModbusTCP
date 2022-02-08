# -*- coding: utf-8 -*-
"""
Created on Wed Aug 18 03:02:43 2021

@author: PEM10
"""
import io,os
tags ={}

def fileLoader(url):
        with io.open(url, mode="r", encoding="utf-8") as f:
            return replaceMarks(replaceLoop(f.read()))
    
def replaceMarks(line):
    while line.find("{{") > 0:
        i=line.find("{{")
        j=line.find("}}")
        t=line[i+2:j]
        line=line.replace("{{"+t+"}}",tags[t])
    return line
    
def replaceIndex(line,index,si="{[index",ti="]}"):
    while line.find(si) > 0:
        i=line.find(si)
        j=line.find(ti)
        t=line[i+2:j]
        line=line.replace(si + ti,str(index))
    return line
    
def _repLoop(line,s="{[loop",t="]}",e="{[endloop]}",si="{[index",ti="]}"):
    while line.find(s) > 0:
        i=line.find(s)
        j=line.find(t)
        k=line.find(e)
        tx=line[i+len(s)-4:j]
        tx=replaceMarks(tx)
        r=int(tx[5:])
        bloque=""
        for p in range(1,r+1):
            bloque=bloque + replaceIndex(line[j+len(t):k],p,si,ti)
        line=line.replace(line[i:k+len(e)],bloque)
    return line

def replaceLoop(line):
    line=_repLoop(line,s="{[|||||loop",t="|||||]}",e="{[|||||endloop|||||]}",si="{[|||||",ti="|||||]}")
    line=_repLoop(line,s="{[||||loop",t="||||]}",e="{[||||endloop||||]}",si="{[||||",ti="||||]}")
    line=_repLoop(line,s="{[|||loop",t="|||]}",e="{[|||endloop|||]}",si="{[|||",ti="|||]}")
    line=_repLoop(line,s="{[||loop",t="||]}",e="{[||endloop||]}",si="{[||",ti="||]}")
    line=_repLoop(line,s="{[|loop",t="|]}",e="{[|endloop|]}",si="{[|index",ti="|]}")
    line=_repLoop(line,s="{[loop",t="]}",e="{[endloop]}",si="{[index",ti="]}")
    return line
        
def replaceLoopMarks(line):
    while line.find("{[loop") > 0:
        i=line.find("{[loop")
        j=line.find("]}")
        k=line.find("{[endloop]}")
        t=line[i+2:j]
        t=replaceMarks(t)
        r=int(t[5:])
        bloque=""
        for p in range(1,r+1):
            bloque=bloque + replaceIndex(line[j+2:k],p)
        line=line.replace(line[i:k+11],bloque)
    return line
    
def getFBParameters(url, comment="", name="",db="", parameters={}):
    with io.open(url, mode="r", encoding="utf-8") as f:
        line=f.read()
        i=line.find("VAR_INPUT")
        j=line.find("END_VAR")
        k=line.find("VAR_OUTPUT")
        l=line[k:].find("END_VAR")
    lines= (line[i+9:j]+line[k+10:k+l]).splitlines()
    lista=[]
    for l in lines:
        if l.find(":")>0:
            lista.append(l[:l.find(":")].replace(" ",""))
    return lista

def getFBCall(url, comment="", name="",db="", parameters={}):
    with io.open(url, mode="r", encoding="utf-8") as f:
        line=f.read()
        i=line.find("VAR_INPUT")
        j=line.find("END_VAR")
        k=line.find("VAR_OUTPUT")
        l=line[k:].find("END_VAR")
        if name=="":
            name=os.path.basename(f.name)[:-4]
        if db=="":
            db=name+"_DB"
    lines= (line[i+9:j]+line[k+10:k+l]).splitlines()
    lista=[]
    for l in lines:
        if l.find(":")>0:
            lista.append(l[:l.find(":")].replace(" ",""))
    r=""
    r+="NETWORK\n"
    r+="TITLE = " + comment + "\n" 
    r+="      CALL \"" + name + "\", \"" + db + "\""
    if parameters:
        r+="\n      (  "
        for l in lista:
            if l in parameters:
                r+=l + ":=\""+ parameters[l] + "\"\n"
        r+="      )"
    r+=";\n"
    return r