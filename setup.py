import sys
from setuptools import setup, find_packages

#Distribute py wheels
#python3 setup.py bdist_wheel sdist
#twine check dist/*
#cd dist 
#twine upload *

#Basic GIT
#git init/clone
#git add --all
#git commit -m "made some changes"
#git push origin master

with open("README.md", "r") as fh:
    long_description = fh.read()


REQUIREMENTS = []
if sys.platform.startswith('linux'):
	REQUIREMENTS = ['whichcraft']
    


setup(
	name="flaskwebgui",
	version="0.3.0",
	description="Create desktop applications with Flask/Django/FastAPI!",
	url="https://github.com/ClimenteA/flaskwebgui",
	author="Climente Alin",
	author_email="climente.alin@gmail.com",
	license='MIT',
	py_modules=["flaskwebgui"],
	install_requires=REQUIREMENTS,
	packages=find_packages(),
	long_description=long_description,
    long_description_content_type="text/markdown",
	package_dir={"":"src"}
)
