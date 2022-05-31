import numpy as np
from Bio import SeqIO
import pickle
# create file ready for bert embedding extraction from the mispredicted 4 eukaryotes
rest_of_seq = "TRATADAQSRMQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGVVGKLGRQDPPVATR"
seqs, lbls, ids = [], [], []
max_len = 70
for ind, seq_record in enumerate(SeqIO.parse("hard_mammal_seqs.fasta", "fasta")):
    seq_ = str(seq_record.seq)
    seq_ += rest_of_seq[:max_len-len(seq_)]
    seqs.append(seq_)
    ids.append("ID{}|EUKARYA|SP|0".format(ind))
    lbl_ = "S" * len(seq_record.seq)
    lbl_ += (max_len - len(lbl_)) * "I"
    lbls.append(lbl_)

dict = {}
for s, l, i in zip(seqs,lbls,ids):
    dict[s] = [np.array([1]), l, "EUKARYA", "SP"]

pickle.dump(dict, open("test_seqs.bin", "wb"))
