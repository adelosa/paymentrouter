from distutils.core import setup

setup(
    name='paymentrouter',
    version='0.1',
    packages=['paymentrouter'],
    install_requires=[
        'Click',
    ],
    entry_points="""
        [console_scripts]
        window_in=paymentrouter.cli.window_in:cli_entry
    """
)
