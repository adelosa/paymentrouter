try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

requirements = [
    'Click', 'peewee', 'mongoengine'
]

test_requirements = [
    'mongomock', 'mock'
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
