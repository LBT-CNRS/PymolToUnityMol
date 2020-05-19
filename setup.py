from setuptools import setup, find_packages


# Minimal setup.py

setup(
		name ='PymolToUnityMol',
		version ='1.0.0',
		author ='Amelys DEBIOL & Xavier MARTINEZ & Hubert SANTUZ',
		url ='https://github.com/LBT-CNRS/PymolToUnityMol',
		description ='Convert pymol session file to UnityMol commands',
		license ='Apache 2',
		packages = find_packages(),
		entry_points ={
			'console_scripts': [
				'pymoltoumol = PymolToUnityMol.pymolToUMol:main'
			]
		},
		classifiers =(
			"Programming Language :: Python :: 2",
			"Operating System :: OS Independent",
            'Intended Audience :: Science/Research',
            'Topic :: Scientific/Engineering :: Bio-Informatics',
            'Topic :: Scientific/Engineering :: Chemistry',
            'Topic :: Scientific/Engineering :: Physics',
		),
		zip_safe = False
)
