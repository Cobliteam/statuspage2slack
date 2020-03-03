from setuptools import find_packages, setup

setup(
    name='statuspage2slack',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask',
        'python-dotenv',
        'requests',
        'python-dateutil>=2.7'
    ],
)
