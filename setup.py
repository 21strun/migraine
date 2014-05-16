import setuptools
from os.path import join, dirname

setuptools.setup(
    name="migraine",
    version="0.0.1",
    packages=["migraine"],
    install_requires=["django"],
    author="21 strun",
    author_email="adm@21s.pl",
    url="http://github.com/21strun/migraine",
    license="MIT",
    description="Migraine helps with painful data migrations.",
    long_description=open(join(dirname(__file__), "README.rst")).read(),
    keywords=['django', 'migration', 'database'],
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Database',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
)
