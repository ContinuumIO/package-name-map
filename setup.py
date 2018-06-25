from setuptools import setup
import versioneer

requirements = [
    # package requirements go here
    "sqlalchemy",
    "six",
    "toml"
]

setup(
    name='package-name-map',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="A name-mapping database to help unify package managers",
    author="Anaconda, Inc.",
    author_email='conda@anaconda.com',
    url='https://github.com/continuumIO/package-name-map',
    packages=['package_name_map'],
    entry_points={
        'console_scripts': [
            'name-map=package_name_map.cli:main'
        ]
    },
    install_requires=requirements,
    keywords=['packaging', 'package management', 'package names'],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ]
)
