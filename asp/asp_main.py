import random
from .asp_ult import *
from tqdm import tqdm
import glob, os


def conll04_script():
    train_script = """
        python -u ./main.py \
        --mode train \
        --train_path {train_path}
        """
    predict_script = """
            python -u ./main.py \
            --mode predict \
            --dataset_path {dataset_path} \
            --predictions_path {predictions_path}
            """
    eval_script = """
            python -u ./main.py \
            --mode eval \
            --dataset_path {dataset_path}
    """
    CONLL04_SCRIPT = {
        'train': train_script,
        'eval': eval_script,
        'predict': predict_script
    }
    return CONLL04_SCRIPT


def convert_solution_to_data(tokens, solution):
    data_point = {
        'tokens': tokens,
        'entities': [],
        'relations': []
    }
    for atom in solution:
        if match_form(atom) == 'entity':
            entity_type, word = extract_from_atom(atom, 'entity')
            start, end = word.split('+')
            data_point['entities'].append([
                int(start),
                int(end),
                polish_type(entity_type)
            ])
        else:
            relation_type, head_word, tail_word = extract_from_atom(atom, 'relation')
            hstart, hend = head_word.split('+')
            tstart, tend = tail_word.split('+')
            data_point['relations'].append([
                int(hstart),
                int(hend),
                int(tstart),
                int(tend),
                polish_type(relation_type)
            ])
    return data_point


def convert_solutions_back(solution):
    es = []
    rs = []
    for atom in solution:
        atom = atom.replace('ok(', '', 1).replace(')', '', 1) + '.'
        if atom.startswith('loc(') or atom.startswith('peop(') or \
                atom.startswith('org(') or atom.startswith('other('):
            es.append(atom)
        else:
            rs.append(atom)
    return es, rs


def verify_and_infer(entities, relations, inference_program):
    final_outputs = []
    # Convert spert format to twoone format
    entities = spert_to_twoone(entities, relations, 'entity')
    relations = spert_to_twoone(entities, relations, 'relation')

    es = convert_original_to_atoms(entities, 'entity')
    rs = convert_original_to_atoms(relations, 'relation')
    program = concat_facts(es, rs)
    answer_sets = solve_v2(program)
    for answer_set in answer_sets:
        es, rs = convert_solutions_back(answer_set)
        program = inference_program + '\n' + concat_facts(es, rs)
        solution = solve(program)
        if not solution:
            continue
        solution = ['ok(' + atom + ')' for atom in solution]
        es, rs = convert_solutions_back(solution)
        final_outputs.append(es + rs)
    return final_outputs


def verify_and_infer_file(input_path, output_path):
    with open(input_path, 'r') as f:
        input_data = json.load(f)
    with open('asp/inference.lp') as f:
        inference_program = f.read()
    data_points = []
    for i, row in tqdm(enumerate(input_data), total=len(input_data)):
        tokens = row['tokens']
        entities = row['entities']
        relations = row['relations']

        if i in [577]:
            continue

        final_outputs = verify_and_infer(entities, relations, inference_program)
        united_atoms = answer_sets_intersection(final_outputs)

        data_point = convert_solution_to_data(tokens, united_atoms)
        data_point = {
            'tokens': data_point['tokens'],
            'entities': twoone_to_spert(data_point['entities'], data_point['relations'], 'entity'),
            'relations': twoone_to_spert(data_point['entities'], data_point['relations'], 'relation'),
            'id': i
        }
        data_points.append(data_point)
    with open(output_path, 'w') as f:
        json.dump(data_points, f)


def answer_sets_randomly_selection(answer_sets):
    # Number of times an atom appears in each answer_set / total number of answer sets
    if not answer_sets:
        return []
    return random.choice(answer_sets)


def answer_sets_intersection(answer_sets):
    # Number of times an atom appears in each answer_set / total number of answer sets
    if not answer_sets:
        return []
    inter = set(answer_sets[0])
    for answer_set in answer_sets:
        inter = inter.intersection(answer_set)
    return list(inter)


def check_coverage(iteration):
    if iteration == 2:
        return True
    return False


def labeled_model_exists(path):
    if 'done.txt' in glob.glob(os.path.dirname(path)):
        return True
    return False


def unify_two_datasets(first_path, second_path, output_path):
    with open(first_path, 'r') as f:
        first = json.load(f)
    with open(second_path, 'r') as f:
        second = json.load(f)
    with open(output_path, 'w') as f:
        json.dump(first + second, f)


def curriculum_training(labeled_path,
                        unlabeled_path,
                        raw_pseudo_labeled_path,
                        selected_pseudo_labeled_path,
                        unified_pseudo_labeled_path
                        ):
    SCRIPT = conll04_script()
    TRAIN_SCRIPT = SCRIPT['train']
    PREDICT_SCRIPT = SCRIPT['predict']
    COPY_NEW_MODEL = 'python cop_model.py'

    # Step 1: Train on labeled data
    script = TRAIN_SCRIPT.format(train_path=labeled_path)
    print('Train on labeled data')
    # subprocess.run(script, shell=True, check=True)

    iteration = 1
    while True:
        # Step 0: Copy new model
        print('Round #{}: Copy new model'.format(iteration))
        subprocess.run(COPY_NEW_MODEL, shell=True, check=True)

        # Step 2: Predict on unlabeled data
        script = PREDICT_SCRIPT.format(dataset_path=unlabeled_path,
                                       predictions_path=raw_pseudo_labeled_path)
        print('Round #{}: Predict on unlabeled data'.format(iteration))
        subprocess.run(script, shell=True, check=True)

        # Step 3: For each sentence, verify and infer => list of answer sets (ASs)
        print('Round #{}: Verify, Infer and Select on pseudo-labeled data'.format(iteration))
        verify_and_infer_file(input_path=raw_pseudo_labeled_path,
                              output_path=selected_pseudo_labeled_path)

        # Step 3.5 Unify labeled and selected pseudo labels
        print('Round #{}: Unify labels and pseudo labels'.format(iteration))
        unify_two_datasets(first_path=selected_pseudo_labeled_path,
                           second_path=labeled_path,
                           output_path=unified_pseudo_labeled_path)

        # Step 4: Retrain on labeled and pseudo-labeled data
        print('Round #{}: Retrain on selected pseudo labels'.format(iteration))
        script = TRAIN_SCRIPT.format(train_path=unified_pseudo_labeled_path)
        subprocess.run(script, shell=True, check=True)

        exit()

        iteration += 1

        # Step 5: return to Step 2 while not converge
        if check_coverage(iteration):
            break




