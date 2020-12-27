from setuptools import find_packages, setup

install_requires = ['certifi']
raven_requires = [
    'raven',
]
tests_require = [
    'aiohttp',
    'gevent'
    'mock',
    'pytest',
    'pytest-asyncio',
    'pytest-mock',
    'requests'
] + raven_requires

setup(
    name='notifire',
    version='0.1.1',
    url='https://github.com/Notifire/notifire-python',
    author='Notifire team',
    author_email='notifire@memonil.com',
    description='Python client for Notifire (https://notifire.dvdblk.com)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=('tests', 'tests.*')),
    license='BSD',
    install_requires=install_requires,
    extras_require={
        'raven': raven_requires,
    },
    tests_require=tests_require,
    entry_points={
        'console_scripts': ['notifire-cli=notifire.cli:main']
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
