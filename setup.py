from setuptools import setup

setup(
    name='TSKPRIO',  # Nom de ton projet
    version='0.1.0',  # Version du projet
    packages=['TSKPRIO'],  # Assure-toi que ton dossier de code s'appelle bien 'TSKPRIO' ou change ce nom
    install_requires=[
        'pandas>=1.3.3',
        'numpy',
        'matplotlib',
        'gitpython',
        'streamlit==1.15.0',
        'gdown==4.4.0',
    ],
)
