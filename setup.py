# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from pathlib import Path

versionfile = Path("./version")
version = versionfile.read_text().split("\n")[0]
[mainv,modulev,minorv] = version.split(".")

VERSION = (int(mainv), int(modulev), int(minorv))
__version__ = '.'.join(map(str, VERSION[0:3]))
__description__ = '''this is a description'''
__author__ = 'zk'
__author_email__ = 'liuzq7@gmail.com'
__homepage__ = 'https://github.com/zk4/m3u8_dl'
__download_url__ = '%s/archive/master.zip' % __homepage__
__license__ = 'BSD'


if __name__ == '__main__':
    setup(
        # used in pip install and uninstall 
        # pip install modulename
        name='m3_dl',
        version=__version__,
        author=__author__,
        author_email=__author_email__,
        url=__homepage__,
        description=__description__,
        long_description=open('README.md', 'r', encoding='utf-8').read().strip(),
        long_description_content_type='text/markdown',
        download_url=__download_url__,
        license=__license__,
        python_requires='>3.7.0',
        zip_safe=False,
        packages=find_packages(exclude=['tests', 'tests.*']),
        package_data={'m3_dl.logx':
            ['logging.yaml'],
            'm3_dl':
            ['../version']
            }
        ,
        install_requires=open('requirements.txt', 'r').read().strip().split(),
        entry_points={
            'console_scripts': [
                'm3_dl = m3_dl:entry_point'
            ]
        },
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console'
        ],
        keywords=(
            'best practice for python project'
        )
    )
