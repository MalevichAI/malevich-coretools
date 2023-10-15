from setuptools import setup

setup(
    name='malevich-coretools',
    version='0.2.0',
    author="Andrew Pogrebnoj",
    author_email="andrew@onjulius.co",
    package_dir={"malevich_coretools": "malevich_coretools"},
    install_requires=[
        'requests',
        'pydantic',
        'pandas',
        'aiohttp',
        'setuptools'
    ]
)
