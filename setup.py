"""Installer for densli
"""

import os
cwd = os.path.dirname(__file__)
__version__ = open(os.path.join(cwd, 'serverdensity', 'densli', 'version.txt'),
                                     'r').read().strip()

try:
        from setuptools import setup, find_packages
except ImportError:
        from ez_setup import use_setuptools
        use_setuptools()
        from setuptools import setup, find_packages
setup(
    name='densli',
    description='CLI tool for working with the ServerDensity.com API',
    long_description=open('README.rst').read(),
    version=__version__,
    author='Wes Mason',
    author_email='wes@serverdensity.com',
    url='https://github.com/serverdensity/densli',
    packages=find_packages(exclude=['ez_setup']),
    install_requires=open('requirements.txt').readlines(),
    package_data={'serverdensity/densli': ['version.txt', 'config.json']},
    include_package_data=True,
    license='BSD',
    entry_points={
        'console_scripts': [
            'densli = serverdensity.densli.app:main'
        ]
    }
)
