import sys
import re


filepath = sys.argv[1]
filepath2 = sys.argv[2]

f = open(filepath)

f2 = open(filepath2)

gold_order=dict()
current_sent=''

sent_id=[]
sent_text=[]

current_sent_id=''
current_sent_text=''



for line in f:
    line = line.strip()#.encode('utf-8')
    
    if len(line) == 0:

        sent_id.append(current_sent_id)
        sent_text.append(current_sent_text)


        
        current_sent_id=''
        current_sent_text=''

        
    else:

        if line[0]=='#' and line.split(' ')[1]=='sent_id':
            current_sent_id=line
            continue
        
        if line[0]=='#' and line.split(' ')[1]=='text':
            current_sent_text=line
            continue

        
            



        
pred_words=''

pred_repeated=dict()






elto=0
print(sent_id[elto])
print(sent_text[elto]) 
elto+=1
for line in f2:
    line = line.strip()#.encode('utf-8')
    if len(line) == 0:
        print(line)
        if(elto<len(sent_id)):
            print(sent_id[elto])
            print(sent_text[elto])
        elto+=1
        
        
    else:
        print(line)

 

    

f.close()
