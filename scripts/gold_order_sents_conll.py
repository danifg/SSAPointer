import sys
import re


filepath = sys.argv[1]
filepath2 = sys.argv[2]

f = open(filepath)

f2 = open(filepath2)

gold_order=dict()
current_sent=''



gold_words=''
gold=dict()
pos=0

gold_repeated=dict()

for line in f2:
    line = line.strip()#.encode('utf-8')
    
    if len(line) == 0:
        if gold_words in gold_repeated:
            gold_repeated[gold_words]+=1
                
        
        else:
            gold_repeated[gold_words]=1

        if gold_repeated[gold_words] > 1:
            gold_words=gold_words+str(gold_repeated[gold_words])
            
        gold[gold_words]=pos

        
        pos+=1
        gold_words=''
    else:
        gold_words+=line+'@&'
        
            



        
pred_words=''

pred_repeated=dict()

for line in f:
    line = line.strip()#.encode('utf-8')
    if len(line) == 0:
        if pred_words in pred_repeated:
            pred_repeated[pred_words]+=1
            
        else:
            pred_repeated[pred_words]=1

        if pred_repeated[pred_words] > 1:
            
            pred_words=pred_words+str(pred_repeated[pred_words])
            
        gold_order[gold[pred_words]]=current_sent
        current_sent=''
        pred_words=''
        
    else:
        fields = line.split('\t')
        word = fields[1]

        
        
        sent='\t'.join(fields)
        current_sent+=sent+'@&'
        pred_words+=word+'@&'

        
for elto in range(len(gold_order)):
    current_sent=gold_order[elto].strip()
    lines=current_sent.split('@&')
    for l in lines:
        print(l)
 

    

f.close()
