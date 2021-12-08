import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="stellar_system_creator",
    version="0.0.3.1",
    author="Selewirre Iskvary",
    author_email="selewirre@gmail.com",
    description="A tool for creating custom, scientifically plausible stellar systems.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/selewirre/stellar_system_creator",
    packages=setuptools.find_packages(),
    package_dir={'stellar_system_creator': 'stellar_system_creator'},
    package_data={'stellar_system_creator': ['astrothings/data/*.csv',
                                             'documentation/*.pdf',
                                             'examples/output_files/*',
                                             'visualization/default_images/*.png']},
    install_requires=['matplotlib',
                      'numpy',
                      'pandas',
                      'pint',
                      'pyqt5',
                      'scipy'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: GNU GPL v3 license",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)

