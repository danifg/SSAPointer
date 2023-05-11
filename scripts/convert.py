import sys



if __name__ == "__main__":
	source_file = open(sys.argv[1], 'r')
	target_file = open(sys.argv[2], 'w')
	debug=False
        max_heads=0
	while True:
		line = source_file.readline()
		if len(line) > 0 and line[0] == '#': continue
		while len(line) > 0 and len(line.strip()) == 0:
		    line = source_file.readline()
		if len(line) == 0:
		    break

		lines = []
		while len(line.strip()) > 0:
		    line = line.strip()
		    line = line.decode('utf-8')
		    lines.append(line.split('\t'))
		    line = source_file.readline()

		length = len(lines)
		if length == 0:
		    break

		predicates = []
                frame_predicates = []



		for tokens in lines:
			if debug: print tokens[0], '\t', tokens[1].encode('utf-8'), '\t', tokens[2].encode('utf-8'), '\t', tokens[4],

			target_file.write('%s\t%s\t%s\t%s' % (tokens[0].encode('utf-8'), tokens[1].encode('utf-8'), tokens[2].encode('utf-8'), tokens[4].encode('utf-8') ))
                        

                        
			num_heads=0
			types=[]
			for i in range(length+1):
				types.append('_')


                        if tokens[10]!='_':
                                edges=tokens[10].split('|')
                                num_heads=len(edges)
                                for edge in edges:
                                        head=edge.split(':')[0]
                                        label=edge.split(':')[1]
                                        if types[int(head)]!='_':
                                                types[int(head)]=types[int(head)]+'#'+label
                                        else:
                                                types[int(head)]=label


                        
                        if num_heads>max_heads:
                                max_heads=num_heads

			
			for t in types:
                                
				
				if debug: print '\t', t,
				target_file.write('\t%s' % (t.encode('utf-8')))
			if debug: print
			target_file.write('\n')




		if debug: print
		target_file.write('\n')
	target_file.close()

	

			
	
		
