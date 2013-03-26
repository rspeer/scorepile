from setuptools import setup

setup(
    name='scorepile',
    version='0.1',
    maintainer='Rob Speer',
    maintainer_email='rob@scorepile.org',
    license='MIT',
    url='http://github.com/rspeer/scorepile',
    platforms='any',
    description='Analyzes, searches, and hosts Innovation game logs',
    packages=['scorepile'],
    install_requires=['beautifulsoup4', 'bottle', 'SQLAlchemy'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ]
)

