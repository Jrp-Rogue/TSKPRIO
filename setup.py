from setuptools import setup, find_packages

setup(
    name='TSKPRIO',  # Nom de ton projet
    version='0.1.0',  # Version du projet
    description='Un projet pour gérer des tâches et des priorités',  # Description de ton projet
    author='Jrp-Rogue',  # Ton nom
    author_email='rhogini@gmail.com',  # Ton email
    url='https://github.com/Jrp-Rogue/TSKPRIO',  # L'URL de ton dépôt GitHub
    packages=find_packages(),  # Trouve automatiquement tous les packages Python dans ton projet
    install_requires=[  # Liste des dépendances de ton projet
        'pandas>=1.3.3',
        'numpy',
        'matplotlib',
        'gitpython',
        'streamlit==1.15.0',
        'gdown==4.4.0',
        'rich>=10.14.0',
    ],
    classifiers=[  # Classificateurs de ton projet
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Version minimale de Python requise
)

