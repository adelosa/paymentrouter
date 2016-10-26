import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

requirements = [
    'Click', 'mongoengine', 'sqlalchemy'
]

if sys.version_info < (3, 4):
    # Backport of Python 3.4 enums to earlier versions
    requirements.append('enum34>=1.0.4')

test_requirements = [
    'mongomock', 'mock', 'testing.postgresql', 'psycopg2'
]


setup(
    name='paymentrouter',
    version='0.1',
    packages=['paymentrouter'],
    install_requires=requirements,
    test_requirements=test_requirements,
    entry_points={
        'console_scripts': [
            'pr_file_distribution = paymentrouter.cli.pr_file_distribution:pr_file_distribution',
            'pr_file_collection = paymentrouter.cli.pr_file_collection:pr_file_collection',
        ],
    },
    test_suite='tests'
)
