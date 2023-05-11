import sys
if __name__ == "__main__":
    source_file = open(sys.argv[1], 'r')
    target_file = open(sys.argv[2], 'w')
    num_sents=1
    while True:
        line = source_file.readline()
        if len(line) > 0 and line[0] == '#': continue
        while len(line) > 0 and len(line.strip()) == 0:
            line = source_file.readline()
        if len(line) == 0:break
        lines = []
        while len(line.strip()) > 0:
            line = line.strip()
            line = line.decode('utf-8')
            lines.append(line.split('\t'))
            line = source_file.readline()

        length = len(lines)
        if length == 0:break
        num_sents+=1
        for tokens in lines:
            target_file.write('%s\t%s\t%s\t%s\t%s\t_\t0\tdep\t_\t_\t' % (tokens[0].encode('utf-8'), tokens[1].encode('utf-8'), tokens[2].encode('utf-8'), tokens[3].encode('utf-8'), tokens[3].encode('utf-8')))
            deps=[]
            for i in range(len(lines)+1):
                if tokens[i+4]!='_' and tokens[i+4]!='_<PAD>':
                    edges=tokens[i+4].split('#')
                    for edge in edges:
                        deps.append(str(i)+':'+edge)
            if len(deps)==0:target_file.write('_')
            else:
                cad=deps[0]
                deps[0]='REMOVED'
                for dep in deps:
                    if dep=='REMOVED':continue
                    cad=cad+'|'+dep
                target_file.write(cad)
            target_file.write('\n')
        target_file.write('\n')
    target_file.close()
