from asp.asp_main import curriculum_training

if __name__ == '__main__':
    LABELED_PATH = 'data/datasets/conll04/conll04_train_30_labeled.json'
    UNLABELED_PATH = 'data/datasets/conll04/conll04_train_30_unlabeled.json'
    RAW_PSEUDO_LABELED_PATH = 'data/datasets/conll04/raw.conll04_train_30.json'
    SELECTED_PSEUDO_LABELED_PATH = 'data/datasets/conll04/selected.conll04_train_30.json'
    UNIFIED_PSEUDO_LABELED_PATH = 'data/datasets/conll04/unified.conll04_train_30.json'

    curriculum_training(labeled_path=LABELED_PATH,
                        unlabeled_path=UNLABELED_PATH,
                        raw_pseudo_labeled_path=RAW_PSEUDO_LABELED_PATH,
                        selected_pseudo_labeled_path=SELECTED_PSEUDO_LABELED_PATH,
                        unified_pseudo_labeled_path=UNIFIED_PSEUDO_LABELED_PATH)


