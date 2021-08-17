import os
import pickle
from Bio import SeqIO
import numpy as np


def get_cs_acc(life_grp, seqs, true_lbls, pred_lbls, v=False):
    def is_cs(predicted_cs_ind, true_lbl_seq):
        if true_lbl_seq[predicted_cs_ind] == "S" and true_lbl_seq[predicted_cs_ind + 1] != "S":
            return True
        return False

    def get_acc_for_tolerence(ind, t_lbl, v=False):
        true_cs = 0
        while t_lbl[true_cs] == "S" and true_cs < len(t_lbl):
            true_cs += 1
        if np.abs(true_cs - ind) == 0:
            return np.array([1, 1, 1, 1, 1])
        elif np.abs(true_cs - ind) == 1:
            return np.array([0, 1, 1, 1, 1])
        elif np.abs(true_cs - ind) == 2:
            return np.array([0, 0, 1, 1, 1])
        elif np.abs(true_cs - ind) == 3:
            return np.array([0, 0, 0, 1, 1])
        else:
            return np.array([0, 0, 0, 0, 1])

    # S = signal_peptide; T = Tat/SPI or Tat/SPII SP; L = Sec/SPII SP; P = SEC/SPIII SP; I = cytoplasm; M = transmembrane; O = extracellular;
    # order of elemnts in below list:
    # (eukaria_correct_tollerence_0, eukaria_correct_tollerence_1, eukaria_correct_tollerence_2, ..3, eukaria_total)
    # (negative_correct_tollerence_0, negative_correct_tollerence_1, negative_correct_tollerence_2, ..3, negative_total)
    # (positive_correct_tollerence_0, positive_correct_tollerence_1, positive_correct_tollerence_2, ..3, positive_total)
    # (archaea_correct_tollerence_0, archaea_correct_tollerence_1, archaea_correct_tollerence_2, ..3, archaea_total)
    grp2_ind = {"EUKARYA": 0, "NEGATIVE": 1, "POSITIVE": 2, "ARCHAEA": 3}
    predictions = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
    predictions = [np.array(p) for p in predictions]
    for l, s, t, p in zip(life_grp, seqs, true_lbls, pred_lbls):
        life_grp, sp_info = l.split("|")
        ind = 0
        if sp_info == "SP":
            # print(p,)
            # print(t)
            # print(s)
            # print("\n")
            while p[ind] == "S" and ind < len(p) - 1:
                ind += 1
            predictions[grp2_ind[life_grp]] += get_acc_for_tolerence(ind, t, v=p)
    all_preds = []
    totals = []

    for life_grp, ind in grp2_ind.items():
        current_preds = predictions[grp2_ind[life_grp]]
        if v:
            print("{}: {}".format(life_grp, [current_preds[i] / current_preds[-1] for i in range(len(current_preds) - 1)]))
        all_preds.append([current_preds[i]/current_preds[-1] for i in range(len(current_preds) -1)])
        totals.append(current_preds[-1])
    return all_preds, totals


def get_pred_accs_sp_vs_nosp(life_grp, seqs, true_lbls, pred_lbls, v=False):
    # S = signal_peptide; T = Tat/SPI or Tat/SPII SP; L = Sec/SPII SP; P = SEC/SPIII SP; I = cytoplasm; M = transmembrane; O = extracellular;
    # order of elemnts in below list:
    # (eukaria_correct, eukaria_total)
    # (negative_correct, negative_total)
    # (positive_correct, positive_total)
    # (archaea_correct, archaea_total)
    grp2_ind = {"EUKARYA": 0, "NEGATIVE": 1, "POSITIVE": 2, "ARCHAEA": 3}
    predictions = [[0, 0], [0, 0], [0, 0], [0, 0]]

    for l, s, t, p in zip(life_grp, seqs, true_lbls, pred_lbls):
        life_grp, sp_info = l.split("|")
        if sp_info == "SP":
            if "S" in p.replace("ES", ""):
                predictions[grp2_ind[life_grp]][0] += 1
                predictions[grp2_ind[life_grp]][1] += 1
            else:
                predictions[grp2_ind[life_grp]][1] += 1
        elif sp_info == "NO_SP":
            if "S" in p.replace("ES", ""):
                predictions[grp2_ind[life_grp]][1] += 1
            else:
                predictions[grp2_ind[life_grp]][0] += 1
                predictions[grp2_ind[life_grp]][1] += 1
    if v:
        for grp, id in grp2_ind.items():
            print("{}: {}".format(grp, predictions[grp2_ind[grp]][0] / predictions[grp2_ind[grp]][1]))
    return [predictions[grp2_ind[grp]][0] / predictions[grp2_ind[grp]][1] for grp, id in grp2_ind.items()]


def extract_seq_group_for_predicted_aa_lbls(filename="run_wo_lg_info.bin", test_fold=2):
    seq2preds = pickle.load(open(filename, "rb"))
    tested_seqs = set(seq2preds.keys())
    seq2id = {}
    life_grp, seqs, true_lbls, pred_lbls = [], [], [], []
    for seq_record in SeqIO.parse(get_data_folder() + "sp6_data/train_set.fasta", "fasta"):
        seq, lbls = seq_record.seq[:len(seq_record.seq) // 2], seq_record.seq[len(seq_record.seq) // 2:]
        if seq in tested_seqs:
            life_grp.append("|".join(str(seq_record.id).split("|")[1:-1]))
            seqs.append(seq)
            true_lbls.append(lbls)
            pred_lbls.append(seq2preds[seq])
    return life_grp, seqs, true_lbls, pred_lbls


def get_data_folder():
    if os.path.exists("/scratch/work/dumitra1"):
        return "/scratch/work/dumitra1/sp_data/"
    elif os.path.exists("/home/alex"):
        return "sp_data/"
    else:
        return "/scratch/project2003818/dumitra1/sp_data/"


def get_cs_and_sp_pred_results(filename="run_wo_lg_info.bin", v=False):
    life_grp, seqs, true_lbls, pred_lbls = extract_seq_group_for_predicted_aa_lbls(filename=filename)
    sp_pred_accs = get_pred_accs_sp_vs_nosp(life_grp, seqs, true_lbls, pred_lbls, v=v)
    all_cs_preds, totals = get_cs_acc(life_grp, seqs, true_lbls, pred_lbls, v=v)
    return sp_pred_accs, all_cs_preds, totals

def get_summary_sp_acc(sp_pred_accs):
    return np.mean(sp_pred_accs), sp_pred_accs[0]

def get_summary_cs_acc(all_cs_preds):
    return np.mean(np.array(all_cs_preds)), np.mean(all_cs_preds[0]), all_cs_preds[0][0]

if __name__ == "__main__":
    life_grp, seqs, true_lbls, pred_lbls = extract_seq_group_for_predicted_aa_lbls(filename="20ep_run_high_drop_w_lg.bin")
    get_pred_accs_sp_vs_nosp(life_grp, seqs, true_lbls, pred_lbls,v=True)
    get_cs_acc(life_grp, seqs, true_lbls, pred_lbls,v=True)
