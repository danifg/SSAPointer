__author__ = 'max'

import numpy as np
import torch
from torch.autograd import Variable
from .conllx_data import _buckets, PAD_ID_WORD, PAD_ID_CHAR, PAD_ID_TAG, UNK_ID
from .conllx_data import NUM_SYMBOLIC_TAGS
from .conllx_data import create_alphabets
from . import utils
#from .reader import CoNLLXReader
from .semantic_reader import CoNLLXReader


def _obtain_child_index_for_left2right(heads):
    child_ids = [[] for _ in range(len(heads))]
    # skip the symbolic root.
    for child in range(1, len(heads)):
        head = heads[child]
        child_ids[head].append(child)
    return child_ids


def _obtain_child_index_for_inside_out(heads):
    child_ids = [[] for _ in range(len(heads))]
    for head in range(len(heads)):
        # first find left children inside-out
        for child in reversed(range(1, head)):
            if heads[child] == head:
                child_ids[head].append(child)
        # second find right children inside-out
        for child in range(head + 1, len(heads)):
            if heads[child] == head:
                child_ids[head].append(child)
    return child_ids


def _obtain_child_index_for_depth(heads, reverse):
    def calc_depth(head):
        children = child_ids[head]
        max_depth = 0
        for child in children:
            depth = calc_depth(child)
            child_with_depth[head].append((child, depth))
            max_depth = max(max_depth, depth + 1)
        child_with_depth[head] = sorted(child_with_depth[head], key=lambda x: x[1], reverse=reverse)
        return max_depth

    child_ids = _obtain_child_index_for_left2right(heads)
    child_with_depth = [[] for _ in range(len(heads))]
    calc_depth(0)
    return [[child for child, depth in child_with_depth[head]] for head in range(len(heads))]



def _order_heads_for_inside_out(heads, current_node):
    print '=======ENTRA HEADS', heads, current_node
    new_heads = []# [[] for _ in range(len(heads)-1)]
    heads = heads[:len(heads)-1]
    print 'sacamos ultimo', heads
    left_heads=[]
    right_heads=[]
    for head in heads:
	if head<current_node: 
		left_heads.append(head)
	else:
		right_heads.append(head)
    
    for i in reversed(range(len(left_heads))):
	new_heads.append(left_heads[i])
    for i in range(len(right_heads)):
	new_heads.append(right_heads[i])	
    	
	
    new_heads.append(current_node)
    print 'new_heads', new_heads


    return new_heads



def _generate_stack_inputs(heads, types, prior_order):
    #child_ids = _obtain_child_index_for_left2right(heads)

    debug=False


    
    
    stacked_heads = []
    children = []#[0 for _ in range(len(heads)-1)]
    siblings = []
    previous = []
    next = []	
    stacked_types = []
    skip_connect = []
    prev = [0 for _ in range(len(heads))]
    sibs = [0 for _ in range(len(heads))]
    #newheads = [-1 for _ in range(len(heads))]
    #newheads[0]=0	
    #stack = [0]
    stack = [1]
    position = 1

    grandpa=[0,0]
    previous_head=[]
    previous_secondhead=[]

    for child in range(len(heads)):
        if child == 0: continue

	#ordered_heads=heads[child]
	#if prior_order == 'inside_out':
	#	ordered_heads=_order_heads_for_inside_out(heads[child], child)

	
        for h in heads[child]:#ordered_heads:
            stacked_heads.append(child)
            if child == len(heads)-1:
                next.append(0)
            else:
                next.append(child+1)
            previous.append(child-1)
            #head=heads[child]
            head=h
            #newheads[child]=head
            siblings.append(sibs[head])
            skip_connect.append(prev[head])
            prev[head] = position
            children.append(head)
            sibs[head] = child

            previous_head.append(grandpa[-1])
            previous_secondhead.append(grandpa[-2])
            grandpa.append(head)
            if child == head:
                grandpa=[0,0]

            
        for t in types[child]:    
            #stacked_types.append(types[child])
            stacked_types.append(t)
        position += 1
        if debug: 
                print '________________________________________'			
                print 'stckhead', stacked_heads
                print 'children', children
                print 'prevhead', previous_head
                print 'prevhed2', previous_secondhead
                print 'stacked_types', stacked_types
                print 'siblings', siblings
                print 'sibs', sibs
                
                print 'prev', prev
                print 'heads', heads
                #print 'newheads', newheads
                print 'next', next
                print 'previous', previous

    #Vamos a usar next para pasarle info de los children (usease heads) al metodo _get_decoder_output que usa el loss durante el training
    previous = []
    next = []
    for x in previous_head:
	previous.append(x)
	#previous.append(0)
    for x in previous_secondhead:
        next.append(x)
        
    if debug: 
	#print 'childrenAA', children
	#print 'previousAA', previous
        print 'childrenAA', children
        print 'headssssss', previous_head
        print 'previousss', previous
        print 'headssss22', previous_secondhead
        print 'nexttttttt', next
    #if len(previous)!=len(children): exit(0)
    if debug:exit(0)
    return stacked_heads, children, siblings, stacked_types, skip_connect, previous, next


def read_stacked_data(source_path, bert_path, bert_dim, word_alphabet, char_alphabet, pos_alphabet, type_alphabet, lemma_alphabet, max_size=None, normalize_digits=True, prior_order='deep_first'):
    data = [[] for _ in _buckets]
    max_char_length = [0 for _ in _buckets]
    print('Reading data from %s' % source_path)
    counter = 0
    reader = CoNLLXReader(source_path, bert_path, bert_dim, word_alphabet, char_alphabet, pos_alphabet, type_alphabet, lemma_alphabet)
    inst = reader.getNext(normalize_digits=normalize_digits, symbolic_root=True, symbolic_end=False)
    while inst is not None and (not max_size or counter < max_size):
        counter += 1
        if counter % 10000 == 0:
            print("reading data: %d" % counter)

        inst_size = inst.length()
        sent = inst.sentence
        for bucket_id, bucket_size in enumerate(_buckets):
            if inst_size < bucket_size:
                stacked_heads, children, siblings, stacked_types, skip_connect, previous, next = _generate_stack_inputs(inst.heads, inst.type_ids, prior_order)
                data[bucket_id].append([sent.word_ids, sent.lemma_ids, sent.char_id_seqs, inst.bert_embs, inst.pos_ids, inst.heads, inst.type_ids, stacked_heads, children, siblings, stacked_types, skip_connect, previous, next])
                max_len = max([len(char_seq) for char_seq in sent.char_seqs])
                if max_char_length[bucket_id] < max_len:
                    max_char_length[bucket_id] = max_len
                break

        inst = reader.getNext(normalize_digits=normalize_digits, symbolic_root=True, symbolic_end=False)
    reader.close()
    print("Total number of data: %d" % counter)
    return data, max_char_length


def read_stacked_data_to_variable(source_path, bert_path, bert_dim, word_alphabet, char_alphabet, pos_alphabet, type_alphabet, lemma_alphabet,
                                  max_size=None, normalize_digits=True, prior_order='deep_first', use_gpu=False, volatile=False):
    data, max_char_length = read_stacked_data(source_path, bert_path, bert_dim, word_alphabet, char_alphabet, pos_alphabet, type_alphabet, lemma_alphabet, max_size=max_size, normalize_digits=normalize_digits, prior_order=prior_order)
    bucket_sizes = [len(data[b]) for b in range(len(_buckets))]

    data_variable = []

    for bucket_id in range(len(_buckets)):
        bucket_size = bucket_sizes[bucket_id]
        if bucket_size == 0:
            data_variable.append((1, 1))
            continue

        bucket_length = _buckets[bucket_id]
        char_length = min(utils.MAX_CHAR_LENGTH, max_char_length[bucket_id] + utils.NUM_CHAR_PAD)
        wid_inputs = np.empty([bucket_size, bucket_length], dtype=np.int64)
	lid_inputs = np.empty([bucket_size, bucket_length], dtype=np.int64)#lemma
        cid_inputs = np.empty([bucket_size, bucket_length, char_length], dtype=np.int64)
        pid_inputs = np.empty([bucket_size, bucket_length], dtype=np.int64)
        bert_inputs = np.empty([bucket_size, bucket_length, bert_dim], dtype=np.float32)#BERT 

	#Modificamos para ampliar una tercera dimension los heads y types
        #hid_inputs = np.empty([bucket_size, bucket_length], dtype=np.int64)
	hid_inputs = np.empty([bucket_size, bucket_length, 16], dtype=np.int64)
        #tid_inputs = np.empty([bucket_size, bucket_length], dtype=np.int64)
	tid_inputs = np.empty([bucket_size, bucket_length, 16], dtype=np.int64)

        #MASK AND LENGTH ENCODING
        masks_e = np.zeros([bucket_size, bucket_length], dtype=np.float32)
        single = np.zeros([bucket_size, bucket_length], dtype=np.int64)
	lemma_single = np.zeros([bucket_size, bucket_length], dtype=np.int64)
        lengths_e = np.empty(bucket_size, dtype=np.int64)

	""" L2RParser
        stack_hid_inputs = np.empty([bucket_size, 2 * bucket_length - 1], dtype=np.int64)
        chid_inputs = np.empty([bucket_size, 2 * bucket_length - 1], dtype=np.int64)
        ssid_inputs = np.empty([bucket_size, 2 * bucket_length - 1], dtype=np.int64)
        stack_tid_inputs = np.empty([bucket_size, 2 * bucket_length - 1], dtype=np.int64)
        skip_connect_inputs = np.empty([bucket_size, 2 * bucket_length - 1], dtype=np.int64)

        masks_d = np.zeros([bucket_size, 2 * bucket_length - 1], dtype=np.float32)
	"""
        
        """ StackPointer
        stack_hid_inputs = np.empty([bucket_size, bucket_length - 1], dtype=np.int64)
        chid_inputs = np.empty([bucket_size, bucket_length - 1], dtype=np.int64)
        ssid_inputs = np.empty([bucket_size, bucket_length - 1], dtype=np.int64)
        stack_tid_inputs = np.empty([bucket_size, bucket_length - 1], dtype=np.int64)
        skip_connect_inputs = np.empty([bucket_size, bucket_length - 1], dtype=np.int64)
	    previous_inputs = np.empty([bucket_size, bucket_length - 1], dtype=np.int64)
	    next_inputs = np.empty([bucket_size, bucket_length - 1], dtype=np.int64)
        """
        #Del train hemos sacado que el numero maximo de heads por nodo es 17
        #ADDED MAX 17 heads per node as long as the length of the sentence is higher
        final_length=16*(bucket_length - 1)
        if bucket_length < 15: final_length=bucket_length*(bucket_length - 1)
        
	debug=False
	if debug: print 'bucket length', bucket_length, final_length
	

        stack_hid_inputs = np.empty([bucket_size, final_length], dtype=np.int64)
        chid_inputs = np.empty([bucket_size, final_length], dtype=np.int64)
        ssid_inputs = np.empty([bucket_size, final_length], dtype=np.int64)
        stack_tid_inputs = np.empty([bucket_size, final_length], dtype=np.int64)
        skip_connect_inputs = np.empty([bucket_size, final_length], dtype=np.int64)
	previous_inputs = np.empty([bucket_size, final_length], dtype=np.int64)
	next_inputs = np.empty([bucket_size, final_length], dtype=np.int64)	

        #MASK AND LENGTH DECODING
        masks_d = np.zeros([bucket_size, final_length], dtype=np.float32)
        
        
        
        lengths_d = np.empty(bucket_size, dtype=np.int64)

        for i, inst in enumerate(data[bucket_id]):
            wids, lids, cid_seqs, bert, pids, hids, tids, stack_hids, chids, ssids, stack_tids, skip_ids, previous_ids, next_ids = inst
            inst_size = len(wids)
            lengths_e[i] = inst_size


	    if debug: 
		print 'SIZEEEE ', inst_size
	    	print 'heads', hids
	    	print 'types', tids	
	    	print 'stack_hids', stack_hids	

            # word ids
            wid_inputs[i, :inst_size] = wids
            wid_inputs[i, inst_size:] = PAD_ID_WORD
	    #lemma ids
	    lid_inputs[i, :inst_size] = lids
            lid_inputs[i, inst_size:] = PAD_ID_WORD
            for c, cids in enumerate(cid_seqs):
                cid_inputs[i, c, :len(cids)] = cids
                cid_inputs[i, c, len(cids):] = PAD_ID_CHAR
            cid_inputs[i, inst_size:, :] = PAD_ID_CHAR

            #BERT
            if len(wids)!=len(bert):
                print(len(bert_inputs[i, :inst_size]),len(bert),len(wids))
                print(wids)
                print(chids)
                for a in wids:
                    print(word_alphabet.get_instance(a).encode('utf-8'))
                exit(0)
            bert_inputs[i, :inst_size] = bert
            bert_inputs[i, inst_size:] = PAD_ID_WORD
            
            # pos ids
            pid_inputs[i, :inst_size] = pids
            pid_inputs[i, inst_size:] = PAD_ID_TAG
            # type ids
            #tid_inputs[i, :inst_size] = tids
            #tid_inputs[i, inst_size:] = PAD_ID_TAG
	    for k,t in enumerate(tids):
		#print k, t
		tid_inputs[i, k, :len(t)] = t
		tid_inputs[i, k, len(t):] = PAD_ID_TAG
	    

            # heads
            #hid_inputs[i, :inst_size] = hids
            #hid_inputs[i, inst_size:] = PAD_ID_TAG
	    for k,h in enumerate(hids):	
	    	hid_inputs[i, k, :len(h)] = h
		hid_inputs[i, k, len(h):] = PAD_ID_TAG


            # masks_e
            masks_e[i, :inst_size] = 1.0
            for j, wid in enumerate(wids):
                if word_alphabet.is_singleton(wid):
                    single[i, j] = 1

	    #Hacemos lo mismo para lemmas
	    for j, lid in enumerate(lids):
                if lemma_alphabet.is_singleton(lid):
                    lemma_single[i, j] = 1

            #inst_size_decoder = 2 * inst_size - 1 #StackPointer
	    #inst_size_decoder = inst_size - 1	#L2R

	    #inst_size_decoder = 17*(inst_size - 1)	
	    #if inst_size<17: inst_size_decoder = inst_size*(inst_size - 1)
	    
	    #Como parece que hace padding hasta llenar la longitud del bucket, entonces usamos la longitud de los datos stacked como longitud de decoding, a saber si es correcto
	    inst_size_decoder = len(stack_hids)

	    if debug: print 'inst size decoder', inst_size_decoder

	    #lengths_d[i] = final_length
            lengths_d[i] = inst_size_decoder


            # stacked heads
            stack_hid_inputs[i, :inst_size_decoder] = stack_hids
            stack_hid_inputs[i, inst_size_decoder:] = PAD_ID_TAG
	    if debug: print 'SHI', stack_hid_inputs[i]	
            # children
            chid_inputs[i, :inst_size_decoder] = chids
            chid_inputs[i, inst_size_decoder:] = PAD_ID_TAG
            # siblings
            ssid_inputs[i, :inst_size_decoder] = ssids
            ssid_inputs[i, inst_size_decoder:] = PAD_ID_TAG
            # stacked types
            stack_tid_inputs[i, :inst_size_decoder] = stack_tids
            stack_tid_inputs[i, inst_size_decoder:] = PAD_ID_TAG
            # skip connects
            skip_connect_inputs[i, :inst_size_decoder] = skip_ids
            skip_connect_inputs[i, inst_size_decoder:] = PAD_ID_TAG
            # ADDED
            previous_inputs[i, :inst_size_decoder] = previous_ids
            previous_inputs[i, inst_size_decoder:] = PAD_ID_TAG
	    next_inputs[i, :inst_size_decoder] = next_ids
            next_inputs[i, inst_size_decoder:] = PAD_ID_TAG
            # masks_d
            masks_d[i, :inst_size_decoder] = 1.0
	    if debug: print 'maskd', masks_d[i]
		

        words = Variable(torch.from_numpy(wid_inputs), volatile=volatile)
	lemmas = Variable(torch.from_numpy(lid_inputs), volatile=volatile)
        berts = Variable(torch.from_numpy(bert_inputs), volatile=volatile)
        chars = Variable(torch.from_numpy(cid_inputs), volatile=volatile)
        pos = Variable(torch.from_numpy(pid_inputs), volatile=volatile)
        heads = Variable(torch.from_numpy(hid_inputs), volatile=volatile)
        types = Variable(torch.from_numpy(tid_inputs), volatile=volatile)
        masks_e = Variable(torch.from_numpy(masks_e), volatile=volatile)
        single = Variable(torch.from_numpy(single), volatile=volatile)
	lemma_single = Variable(torch.from_numpy(lemma_single), volatile=volatile)
        lengths_e = torch.from_numpy(lengths_e)

        stacked_heads = Variable(torch.from_numpy(stack_hid_inputs), volatile=volatile)
        children = Variable(torch.from_numpy(chid_inputs), volatile=volatile)
        siblings = Variable(torch.from_numpy(ssid_inputs), volatile=volatile)
        stacked_types = Variable(torch.from_numpy(stack_tid_inputs), volatile=volatile)
        skip_connect = torch.from_numpy(skip_connect_inputs)
	previous = Variable(torch.from_numpy(previous_inputs), volatile=volatile)
	next = Variable(torch.from_numpy(next_inputs), volatile=volatile)

        masks_d = Variable(torch.from_numpy(masks_d), volatile=volatile)
        lengths_d = torch.from_numpy(lengths_d)

        if use_gpu:
            words = words.cuda()
	    lemmas = lemmas.cuda()
            chars = chars.cuda()
            berts = berts.cuda()
            pos = pos.cuda()
            heads = heads.cuda()
            types = types.cuda()
            masks_e = masks_e.cuda()
            single = single.cuda()
	    lemma_single = lemma_single.cuda()
            lengths_e = lengths_e.cuda()
            stacked_heads = stacked_heads.cuda()
            children = children.cuda()
            siblings = siblings.cuda()
            stacked_types = stacked_types.cuda()
            skip_connect = skip_connect.cuda()
            masks_d = masks_d.cuda()
            lengths_d = lengths_d.cuda()
	    previous = previous.cuda()
	    next = next.cuda()

        data_variable.append(((words, lemmas, chars, berts, pos, heads, types, masks_e, single, lemma_single, lengths_e),
                              (stacked_heads, children, siblings, stacked_types, skip_connect, previous, next, masks_d, lengths_d)))

    #exit(0)	
    return data_variable, bucket_sizes


def get_batch_stacked_variable(data, batch_size, unk_replace=0.):
    data_variable, bucket_sizes = data
    total_size = float(sum(bucket_sizes))
    # A bucket scale is a list of increasing numbers from 0 to 1 that we'll use
    # to select a bucket. Length of [scale[i], scale[i+1]] is proportional to
    # the size if i-th training bucket, as used later.
    buckets_scale = [sum(bucket_sizes[:i + 1]) / total_size for i in range(len(bucket_sizes))]

    # Choose a bucket according to data distribution. We pick a random number
    # in [0, 1] and use the corresponding interval in train_buckets_scale.
    random_number = np.random.random_sample()
    bucket_id = min([i for i in range(len(buckets_scale)) if buckets_scale[i] > random_number])
    bucket_length = _buckets[bucket_id]

    data_encoder, data_decoder = data_variable[bucket_id]
    words, lemmas, chars, berts, pos, heads, types, masks_e, single, lemma_single, lengths_e = data_encoder
    stacked_heads, children, siblings, stacked_types, skip_connect, previous, next, masks_d, lengths_d = data_decoder
    bucket_size = bucket_sizes[bucket_id]
    batch_size = min(bucket_size, batch_size)
    index = torch.randperm(bucket_size).long()[:batch_size]
    if words.is_cuda:
        index = index.cuda()

    words = words[index]
    if unk_replace:
        ones = Variable(single.data.new(batch_size, bucket_length).fill_(1))
        noise = Variable(masks_e.data.new(batch_size, bucket_length).bernoulli_(unk_replace).long())
        words = words * (ones - single[index] * noise)


    lemmas = lemmas[index]
    if unk_replace:
        ones = Variable(lemma_single.data.new(batch_size, bucket_length).fill_(1))
        noise = Variable(masks_e.data.new(batch_size, bucket_length).bernoulli_(unk_replace).long())
        lemmas = lemmas * (ones - lemma_single[index] * noise)


    return (words, lemmas, chars[index], berts[index], pos[index], heads[index], types[index], masks_e[index], lengths_e[index]), \
           (stacked_heads[index], children[index], siblings[index], stacked_types[index], skip_connect[index], previous[index], next[index], masks_d[index], lengths_d[index])


def iterate_batch_stacked_variable(data, batch_size, unk_replace=0., shuffle=False):
    data_variable, bucket_sizes = data

    bucket_indices = np.arange(len(_buckets))
    if shuffle:
        np.random.shuffle((bucket_indices))

    for bucket_id in bucket_indices:
        bucket_size = bucket_sizes[bucket_id]
        bucket_length = _buckets[bucket_id]
        if bucket_size == 0:
            continue
        data_encoder, data_decoder = data_variable[bucket_id]
        words, lemmas, chars, berts, pos, heads, types, masks_e, single, lemma_single, lengths_e = data_encoder
        stacked_heads, children, siblings, stacked_types, skip_connect, previous, next, masks_d, lengths_d = data_decoder
        if unk_replace:
            ones = Variable(single.data.new(bucket_size, bucket_length).fill_(1))
            noise = Variable(masks_e.data.new(bucket_size, bucket_length).bernoulli_(unk_replace).long())
            words = words * (ones - single * noise)

	if unk_replace:
            ones = Variable(lemma_single.data.new(bucket_size, bucket_length).fill_(1))
            noise = Variable(masks_e.data.new(bucket_size, bucket_length).bernoulli_(unk_replace).long())
            lemmas = lemmas * (ones - lemma_single * noise)



        indices = None
        if shuffle:
            indices = torch.randperm(bucket_size).long()
            if words.is_cuda:
                indices = indices.cuda()
        for start_idx in range(0, bucket_size, batch_size):
            if shuffle:
                excerpt = indices[start_idx:start_idx + batch_size]
            else:
                excerpt = slice(start_idx, start_idx + batch_size)
            yield (words[excerpt], lemmas[excerpt], chars[excerpt], berts[excerpt], pos[excerpt], heads[excerpt], types[excerpt], masks_e[excerpt], lengths_e[excerpt]), \
                  (stacked_heads[excerpt], children[excerpt], siblings[excerpt], stacked_types[excerpt], skip_connect[excerpt], previous[excerpt], next[excerpt], masks_d[excerpt], lengths_d[excerpt])
