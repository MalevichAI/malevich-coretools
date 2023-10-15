from setuptools import setup

version = open('malevich_coretools/VERSION').read().strip()
requirements = open('malevich_coretools/requirements.txt').read().split()

setup(
    name='malevich-coretools',
    version=version,
    author="Andrew Pogrebnoj",
    author_email="andrew@onjulius.co",
    package_dir={"malevich_coretools": "malevich_coretools"},
    install_requires=requirements,
)
