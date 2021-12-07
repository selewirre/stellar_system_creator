import pickle
from typing import Union
import blosc
import _pickle as cPickle
# https://stackoverflow.com/questions/57983431/whats-the-most-space-efficient-way-to-compress-serialized-python-data

from stellar_system_creator.stellar_system_elements.binary_system import BinarySystem
from stellar_system_creator.stellar_system_elements.planetary_system import PlanetarySystem
from stellar_system_creator.stellar_system_elements.stellar_system import StellarSystem
from stellar_system_creator.stellar_system_elements.stellar_body import StellarBody


def add_extension_if_necessary(filename, extension):
    if extension[0] != '.':
        extension = '.' + extension
    # finding if filename has ending same as extension and if not, it adds the extension ending to the file
    filename_ending = filename.split('.')[-1]
    if filename_ending != extension[1:]:
        filename = filename + extension

    return filename


def save(obj: Union[StellarBody, BinarySystem, PlanetarySystem, StellarSystem], filename: str) -> bool:
    """Saving object (can be any class) via pickling under filename with extension .scc"""
    supported_classes = [StellarBody, BinarySystem, PlanetarySystem, StellarSystem]

    if any([isinstance(obj, cl) for cl in supported_classes]):
        filename = add_extension_if_necessary(filename, 'ssc')
        pickled_data = cPickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)  # returns data as a bytes object
        compressed_pickle = blosc.compress(pickled_data)
        with open(filename, 'wb') as file:
            file.write(compressed_pickle)
            # pickle.dump(obj, file)
            # cPickle.dump(obj, file)
        return True
    else:
        print(f'Object class {obj.__class__} not supported... File {filename} was not saved...')
        return False


def load(filename: str) -> Union[StellarBody, BinarySystem, PlanetarySystem, StellarSystem]:
    """Loading scc pickled files"""
    # filename = add_extension_if_necessary(filename, 'ssc')

    with open(filename, "rb") as f:
        compressed_pickle = f.read()

    depressed_pickle = blosc.decompress(compressed_pickle)
    obj = cPickle.loads(depressed_pickle)  # turn bytes object back into data

    return obj
