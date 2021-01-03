from gm import start_simulation as gm_sim
from fgm_ols import start_simulation as fgm_sim
from centralized import start_simulation as central_sim
from data_evaluation import run_evaluation as evaluate
from constants import Constants
from dataset import create_dataset, create_dataset_custom2, create_dataset_custom
import time
import winsound
import argparse


def boolean_string(s):
    if s not in {'False', 'True'}:
        raise ValueError('Not a valid boolean string')
    return s == 'True'


def avg_error(norm):
    if isinstance(norm, list):
        sum_error = 0
        for n in norm:
            sum_error += n[0] * const.ERROR
        return sum_error / const.EPOCH
    else:
        return norm * const.ERROR


parser = argparse.ArgumentParser()
parser.add_argument("choice", help="Choose algorithm ~1: central, ~2: gm, ~3:fgm", type=int)
parser.add_argument("new_dataset", help="Create dataset option -'old','fixed','drift'", type=str)
parser.add_argument("k", help="Integer - Number of nodes", type=int)
parser.add_argument("points", help="Integer - Number of data points", type=int)
parser.add_argument("epoch", help="Integer - Number of epochs used to create drift dataset", type=int)
parser.add_argument("var", help="Float - Variance used for bias on dataset creation", type=float)
parser.add_argument("features", help="Integer - Features used for dataset creation", type=int)
parser.add_argument("vper", help="Float - Persentage of test data vs train data", type=float)
parser.add_argument("error", help=" Float - FGM and GM threshold", type=float)
parser.add_argument("win_size", help="Integer - The sliding window size", type=int)
parser.add_argument("win_step", help="Integer - The size of slider of sliding window", type=int)
parser.add_argument("test", help="Boolean - True if on testing mode", type=boolean_string)
parser.add_argument("debug", help="Bolean - True if on debug mode", type=boolean_string)
parser.add_argument("in_file", help="String - Name of input file (without format)", type=str)
parser.add_argument("med_name", help="String - Part of name of output file(without format)", type=str)
parser.add_argument("start_name", help="String - Part of name of output file(without format)", type=str)

args = parser.parse_args()

if __name__ == "__main__":
    # Choose algorithm
    choice = args.choice  # ~1: central, ~2: gm, ~3:fgm

    # Update constants:
    const = Constants(points=args.points,
                      epoch=args.epoch,
                      var=args.var,
                      k=args.k,
                      features=args.features,
                      error=args.error,
                      vper=0 if args.new_dataset == "drift" else args.vper,
                      win_size=args.win_size,
                      win_step=args.win_step,
                      test=args.test,
                      debug=args.debug,
                      in_file=args.in_file,
                      med_name=args.med_name,
                      start_name=args.start_name)
    # Choose dataset
    new_dataset = args.new_dataset
    norma = None

    if new_dataset == 'old':
        norma = input("Please enter norma:")
    elif new_dataset == 'fixed':
        norma = create_dataset(points=const.POINTS,
                               features=const.FEATURES,
                               noise=const.VAR,
                               test=const.VPER,
                               file_name=const.IN_FILE)

    elif new_dataset == 'drift':
        norma = create_dataset_custom(points=const.POINTS,
                                      features=const.FEATURES,
                                      nodes=const.K,
                                      noise=const.VAR,
                                      epochs=const.EPOCH,
                                      file_name=const.IN_FILE)
    else:
        raise Exception("new_dataset input is not valid")

    start_time = time.time()
    print("Start running, wait until finished:")
    if choice == 1:
        central_sim(const)
        evaluate(const, (const.EPOCH <= 1), norma)
    elif choice == 2:
        # const.ERROR = norma*const.ERROR
        if gm_sim(const):
            evaluate(const, (const.EPOCH <= 1), norma)
    elif choice == 3:
        fgm_sim(const)
        evaluate(const, (const.EPOCH <= 1), norma)
    elif choice == 4:
        evaluate(const, (const.EPOCH <= 1), norma)

    print("\n\nSECONDS: %2f" % (time.time() - start_time))
    duration = 2000  # milliseconds
    freq = 440  # Hz
    # winsound.Beep(freq, duration)
