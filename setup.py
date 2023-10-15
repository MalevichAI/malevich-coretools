from setuptools import setup

version = open('VERSION').read().strip()
requirements = open('requirements.txt').read().split()

setup(
    name='malevich-coretools',
    version=version,
    author="Andrew Pogrebnoj",
    author_email="andrew@onjulius.co",
    package_dir={"malevich_coretools": "malevich_coretools"},
    package_data={"": ["VERSION", "requirements.txt", "README.md"]},
    install_requires=requirements,
)
