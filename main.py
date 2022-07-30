
from local_parser import *
import argparse
import subprocess


def train(args):
    set_default_train_config(args.train_path)
    script = 'python ./spert.py train --config configs/default_train.conf'
    subprocess.run(script, shell=True, check=True)


def evaluate(args):
    set_default_eval_config(args.dataset_path)
    script = 'python ./spert.py eval --config configs/default_eval.conf'
    subprocess.run(script, shell=True, check=True)


def predict(args):
    set_default_predict_config(args.dataset_path, args.predictions_path)
    script = 'python ./spert.py predict --config configs/default_predict.conf'
    subprocess.run(script, shell=True, check=True)


parser = argparse.ArgumentParser(description='Arguments for training.')
parser = local_parse(parser)
args = parser.parse_args()


if __name__ == '__main__':
    if args.mode == 'train':
        train(args)
    elif args.mode == 'eval':
        evaluate(args)
    elif args.mode == 'predict':
        predict(args)
    else:
        raise RuntimeError('Invalid mode (only accept train/eval/test')


