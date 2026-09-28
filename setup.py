from setuptools import setup, find_packages
with open('requirments.txt') as f:
    req = f.read().splitlines()
setup(
    name="BulkMate Packages",
    author="DC",
    author_email="mallickdurgacharan188@gmail.com",
    packages=find_packages(),
    install_requires=req,)