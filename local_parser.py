def none_or_str(value):
    if value == 'None':
        return None
    return value


def none_or_int(value):
    if value == 'None':
        return None
    return int(value)


def local_parse(parser):
    parser.add_argument('--mode',
                        default='train',
                        action='store', )

    parser.add_argument('--train_path',
                        default=None, type=none_or_str,
                        action='store', )

    parser.add_argument('--dataset_path',
                        default=None, type=none_or_str,
                        action='store', )

    parser.add_argument('--predictions_path',
                        default=None, type=none_or_str,
                        action='store', )
    return parser


def set_default_train_config(train_path):
    with open('configs/default_train.conf', 'w') as f:
        conf = f"""
[1]
label = conll04_train
model_type = spert
model_path = bert-base-cased
tokenizer_path = bert-base-cased
train_path = {train_path}
valid_path = data/datasets/conll04/conll04_dev.json
types_path = data/datasets/conll04/conll04_types.json
train_batch_size = 2
eval_batch_size = 1
neg_entity_count = 100
neg_relation_count = 100
epochs = 20
lr = 5e-5
lr_warmup = 0.1
weight_decay = 0.01
max_grad_norm = 1.0
rel_filter_threshold = 0.4
size_embedding = 25
prop_drop = 0.1
max_span_size = 10
store_predictions = true
store_examples = true
sampling_processes = 4
max_pairs = 1000
final_eval = true
log_path = data/log/
save_path = data/save/
        """
        f.write(conf)


def set_default_predict_config(dataset_path, predictions_path):
    with open('configs/default_predict.conf', 'w') as f:
        conf = f"""
[1]
model_type = spert
model_path = data/models/conll04
tokenizer_path = data/models/conll04
dataset_path = {dataset_path}
types_path = data/datasets/conll04/conll04_types.json
predictions_path = {predictions_path}
spacy_model = en_core_web_sm
eval_batch_size = 1
rel_filter_threshold = 0.4
size_embedding = 25
prop_drop = 0.1
max_span_size = 10
sampling_processes = 4
max_pairs = 1000
        """
        f.write(conf)


def set_default_eval_config(dataset_path):
    with open('configs/default_eval.conf', 'w') as f:
        conf = f"""
[1]
label = conll04_eval
model_type = spert
model_path = data/models/conll04
tokenizer_path = data/models/conll04
dataset_path = {dataset_path}
types_path = data/datasets/conll04/conll04_types.json
eval_batch_size = 1
rel_filter_threshold = 0.4
size_embedding = 25
prop_drop = 0.1
max_span_size = 10
store_predictions = true
store_examples = true
sampling_processes = 4
max_pairs = 1000
log_path = data/log/
        """
        f.write(conf)