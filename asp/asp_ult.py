import json
import subprocess
import ast

clingo_path = 'clingo'
clingo_options = ['--outf=2', '-n 0']
clingo_command = [clingo_path] + clingo_options

drive_command = ['clingo', 'asp/drive55.py',
                 'asp/p1.lp', 'asp/p3.lp', '--outf=3']


def solve(program):
    input = program.encode()
    process = subprocess.Popen(clingo_command, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    output, error = process.communicate(input)
    result = json.loads(output.decode())
    if result['Result'] == 'SATISFIABLE' or result['Result'] == 'OPTIMUM FOUND':
        solutions = [value['Value'] for value in result['Call'][0]['Witnesses']]
        return union_all_solutions(solutions)
    else:
        return []


def solve_v2(program):
    # Write the program to a file
    with open('asp/p3.lp', 'w') as f:
        f.write(program)
    process = subprocess.Popen(drive_command, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    output, error = process.communicate()
    result = ast.literal_eval(output.decode().split('\n')[-2])
    return result


def union_all_solutions(solutions):
    union = set()
    for solution in solutions:
        for atom in solution:
            if not atom.startswith('nOfOKAtoms'):
                union.add(atom)
    return list(union)


def concat_facts(es, rs):
    output = []
    for e in es:
        output.append(e)
    for r in rs:
        output.append(r)
    return '\n'.join(output)


def hash_entity(tokens, entity, with_atom):
    etype = format_for_asp(entity[2], 'entity')
    eword = '_'.join(tokens[entity[0]:entity[1]])
    if with_atom:
        return 'atom({}("{}")).'.format(etype, eword)
    return '{}("{}").'.format(etype, eword)


def hash_relation(tokens, relation, with_atom):
    rtype = format_for_asp(relation[4], 'relation')
    headword = '_'.join(tokens[relation[0]:relation[1]])
    tailword = '_'.join(tokens[relation[2]:relation[3]])
    if with_atom:
        return 'atom({}("{}","{}")).'.format(rtype, headword, tailword)
    return '{}("{}","{}").'.format(rtype, headword, tailword)


def match_form(atom):
    open_pos = atom.index('(')
    if atom[:open_pos] in ['peop', 'loc', 'org', 'other']:
        return 'entity'
    return 'relation'


def polish_type(atom_type):
    if atom_type in ['peop', 'loc', 'org', 'other']:
        return atom_type.capitalize()
    if atom_type == 'liveIn':
        return 'Live_In'
    elif atom_type == 'locatedIn':
        return 'Located_In'
    elif atom_type == 'orgbasedIn':
        return 'OrgBased_In'
    elif atom_type == 'workFor':
        return 'Work_For'
    return 'Kill'


def extract_from_atom(atom, form_type):
    open_pos = atom.index('(')
    close_pos = atom.index(')')
    if form_type == 'entity':
        return atom[:open_pos], atom[open_pos + 1:close_pos].strip().strip('"')
    # count number of comma
    count = atom.count(',')
    if count == 1:
        comma_pos = atom.index(',')
    else:
        comma_pos = atom.index('",') + 1
    return atom[:open_pos], \
           atom[open_pos + 1:comma_pos].strip().strip('"'), \
           atom[comma_pos + 1:close_pos].strip().strip('"')


def format_for_asp(s, type):
    if type == 'entity':
        return s.lower()
    else:
        splits = s.split('_')
        if len(splits) > 1:
            return '{}{}'.format(splits[0].lower(), splits[1].capitalize())
        return splits[0].lower()


def convert_original_to_atoms(data, dtype):
    result = []
    for d in data:
        if dtype == 'entity':
            e = 'atom({}("{}")).'.format(format_for_asp(d[2], 'entity'),
                                         str(d[0]) + '+' + str(d[1]))
            result.append(e)
        else:
            r = 'atom({}("{}","{}")).'.format(format_for_asp(d[4], 'relation'),
                                         str(d[0]) + '+' + str(d[1]), str(d[2]) + '+' + str(d[3]))
            result.append(r)
    return result


def spert_to_twoone(entities, relations, dtype):
    if dtype == 'entity':
        new_entities = []
        for entity in entities:
            new_entities.append(
                [entity['start'], entity['end'], entity['type']]
            )
        return new_entities
    else:
        new_relations = []
        for relation in relations:
            new_relations.append(
                [entities[relation['head']][0],
                 entities[relation['head']][1],
                 entities[relation['tail']][0],
                 entities[relation['tail']][1],
                 relation['type']]
            )
        return new_relations


def twoone_to_spert(entities, relations, dtype):
    if dtype == 'entity':
        new_entities = []
        for entity in entities:
            new_entities.append(
                {
                    'start': entity[0],
                    'end': entity[1],
                    'type': entity[2]
                }
            )
        return new_entities
    else:
        new_relations = []
        for relation in relations:
            for i, h_entity in enumerate(entities):
                if relation[0] == h_entity[0] and relation[1] == h_entity[1]:
                    for j, t_entity in enumerate(entities):
                        if relation[2] == t_entity[0] and relation[3] == t_entity[1]:
                            new_relations.append(
                                {
                                    'head': i,
                                    'tail': j,
                                    'type': relation[4]
                                }
                            )
        return new_relations


def convert_position_to_word_atoms(tokens, atoms):
    word_atoms = []
    for atom in atoms:
        if match_form(atom) == 'entity':
            entity_type, word = extract_from_atom(atom, 'entity')
            start, end = word.split('+')
            _word = '_'.join(tokens[int(start):int(end)])
            word_atoms.append(
                f'{entity_type}("{_word}")'
            )
        else:
            relation_type, head_word, tail_word = extract_from_atom(atom, 'relation')
            hstart, hend = head_word.split('+')
            tstart, tend = tail_word.split('+')
            _head_word = '_'.join(tokens[int(hstart):int(hend)])
            _tail_word = '_'.join(tokens[int(tstart):int(tend)])
            word_atoms.append(
                f'{relation_type}("{_head_word}", "{_tail_word}")'
            )
    return word_atoms


def remove_wrap(atoms, wrap_type):
    assert wrap_type in ['atom', 'ok']
    new_atoms = []
    for atom in atoms:
        if wrap_type == 'atom':
            new_atoms.append(
                atom.replace('atom(', '')[:-1]
            )
        else:
            new_atoms.append(
                atom.replace('ok(', '')[:-1]
            )
    return new_atoms











