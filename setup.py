import setuptools
import os


def package_files(directory):
    # https://stackoverflow.com/questions/27664504/how-to-add-package-data-recursively-in-python-setup-py/27664856
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


doc_files = package_files('stellar_system_creator/documentation')


with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="stellar_system_creator",
    version='0.4.4.0',
    author="Selewirre Iskvary",
    author_email="selewirre@gmail.com",
    description="A tool for creating custom, scientifically plausible stellar systems.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/selewirre/stellar_system_creator",
    packages=setuptools.find_packages(),
    package_dir={'stellar_system_creator': 'stellar_system_creator'},
    package_data={'stellar_system_creator': ['astrothings/data/*.csv',
                                             'examples/output_files/*',
                                             'visualization/default_images/*.png',
                                             'visualization/more_images/*.png',
                                             'gui/*.ico', 'gui/*.png',
                                             'gui/gui_icons/*'] + doc_files},
    install_requires=['bidict==0.21.4',
                      'blosc==1.10.6',
                      'bs4==0.0.2',
                      'cairocffi==1.3.0',
                      'fpdf2==2.5.0',
                      'numpy==1.21.5',
                      'pandas==1.3.5',
                      'pillow==8.4.0',
                      'pint==0.18',
                      'pycairo==1.20',
                      'pyqt5==5.15.6',
                      'pyqtwebengine==5.15.5',
                      'scipy==1.7.3'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: GNU GPL v3 license",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)

