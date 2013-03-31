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
    install_requires=[
        'beautifulsoup4', 'bottle', 'SQLAlchemy', 'Jinja2', 'beaker',
        'psycopg2', 'pytz'
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ]
)

try:
    import html5lib
except ImportError:
    print()
    print("You also need to install html5lib to parse games.")
    print("Get it from: https://github.com/puzzlet/python3-html5lib")
    print("(git clone https://github.com/puzzlet/python3-html5lib.git)")
