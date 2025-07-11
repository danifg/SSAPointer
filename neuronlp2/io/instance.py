__author__ = 'max'


class Sentence(object):
    def __init__(self, words, word_ids, lemmas, lemma_ids, char_seqs, char_id_seqs):
        self.words = words
        self.word_ids = word_ids
	self.lemmas = lemmas
        self.lemma_ids = lemma_ids
        self.char_seqs = char_seqs
        self.char_id_seqs = char_id_seqs

    def length(self):
        return len(self.words)


class DependencyInstance(object):
    def __init__(self, sentence, bert_embs, postags, pos_ids, heads, types, type_ids):
        self.sentence = sentence
        self.bert_embs = bert_embs
        self.postags = postags
        self.pos_ids = pos_ids
        self.heads = heads
        self.types = types
        self.type_ids = type_ids

    def length(self):
        return self.sentence.length()


class NERInstance(object):
    def __init__(self, sentence, postags, pos_ids, chunk_tags, chunk_ids, ner_tags, ner_ids):
        self.sentence = sentence
        self.postags = postags
        self.pos_ids = pos_ids
        self.chunk_tags = chunk_tags
        self.chunk_ids = chunk_ids
        self.ner_tags = ner_tags
        self.ner_ids = ner_ids

    def length(self):
        return self.sentence.length()
