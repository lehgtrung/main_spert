import glob, os
from shutil import copyfile

if __name__ == '__main__':
    newest_model = glob.glob('data/save/conll04_train/*')
    newest_model = sorted(newest_model)[-1]
    target = 'data/models/conll04/{}'
    for file in glob.glob(newest_model + '/final_model/*'):
        base_name = os.path.basename(file)
        copyfile(file, target.format(base_name))
    print('Newest model: {}'.format(newest_model))
    print('Finish copying newest model!')

