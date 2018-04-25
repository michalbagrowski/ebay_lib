#from pip.download import PipSession
from pip.req import parse_requirements
from setuptools import find_packages, setup

setup(
    name='ebay_lib',
    author="Michał Bagrowski",
    author_email="michal@bagrowski.com",
    version='0.0.7',
    include_package_data=True,
    description="trollol",
    packages=find_packages(),
    dependency_links=[]
)
