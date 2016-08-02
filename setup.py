try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='paymentrouter',
    version='0.1',
    packages=['paymentrouter'],
    install_requires=[
        'Click', 'mock', 'peewee', 'pymongo'
    ],
    entry_points={
        'console_scripts': [
            'pr_file_distribution = paymentrouter.cli.pr_file_distribution:pr_file_distribution',
            'pr_file_collection = paymentrouter.cli.pr_file_collection:pr_file_collection',
        ],
    },
    test_suite='tests'
)
