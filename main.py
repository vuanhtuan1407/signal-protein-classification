import pickle
import os
import datetime
from sp_data.data_utils import SPbinaryData
from train_scripts.cv_train_cs_predictors import train_cs_predictors
from train_scripts.cv_train_binary_sp_model import train_bin_sp_mdl
import argparse
import logging

def create_parameter_set():
    from sklearn.model_selection import ParameterGrid
    parameters = {"dos": [[0.1, 0.2], [0.3, 0.3]], "filters":[[100, 80, 60, 40],
                    [120, 100, 80, 60], [140, 120, 100, 80]], "lengths":[[3, 5, 9, 15],[5, 9, 15, 21]],
                  "lr":[0.001, 0.0001], "patience":[5], "use_aa_len":[100], "pos_weight":[1,5]}
    group_params = list(ParameterGrid(parameters))
    grpid_2_params = {}
    for i in range(len(group_params) // 5  + 1):
        grpid_2_params[i] = group_params[i*5:(i+1)*5]
    pickle.dump(grpid_2_params, open("param_groups_by_id.bin", "wb"))

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--use_aa_len", default=200, type=int)
    parser.add_argument("--lr", default=0.001, type=float)
    parser.add_argument("--data", default="mammal", type=str)
    parser.add_argument("--param_set_search_number", default=-1, type=int)
    parser.add_argument("--train_cs_predictor", default=False, action="store_true")
    parser.add_argument("--batch_size", default=16, type=int)
    parser.add_argument("--run_name", default="some_run", type=str)
    parser.add_argument("--epochs", default=20, type=int)

    return parser.parse_args()


if __name__ == "__main__":
    date_now = str(datetime.datetime.now()).split(".")[0].replace("-", "").replace(":", "").replace(" ", "")
    logging.getLogger('some_logger')
    args = parse_arguments()
    logging.basicConfig(filename=args.run_name + ".log", level=logging.INFO)
    if args.train_cs_predictor:
        a = train_cs_predictors(bs=args.batch_size, eps=args.epochs, run_name=args.run_name)
    else:
        if args.param_set_search_number != -1 and not os.path.exists("param_groups_by_id.bin"):
            create_parameter_set()
        run_name = args.run_name + "_" + date_now
        a = train_bin_sp_mdl(args.run_name, args.use_aa_len, args.lr, data=args.data, nested_cv=args.data == "mammal",)
