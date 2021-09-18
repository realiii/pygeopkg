from setuptools import find_packages, setup
from os.path import join, dirname

with open(join(dirname(__file__), 'README.md')) as readme:
    README = readme.read()

setup(
    name='pygeopkg',
    version='0.1.2',
    author='Integrated Informatics Inc.',
    author_email='gis@integrated-informatics.com',
    description='A Python library that allows for the creation and population '
                'of OGC GeoPackage databases with write access',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/realiii/pygeopkg',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        # 'Development Status :: 5 - Production/Stable',
    ],
    packages=find_packages(exclude=('*tests',)),
)
