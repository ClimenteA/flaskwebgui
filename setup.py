from setuptools import setup, find_packages

#python setup.py bdist_wheel sdist
#cd dist 
#twine upload *


with open("README.md", "r") as fh:
    long_description = fh.read()


setup (
	name="flaskwebgui",
	version="0.0.2",
	description="Freeze web apps made in Flask as desktop apps with flaskwebgui and pyinstaller",
	url="https://github.com/ClimenteA/flaskwebgui",
	author="Climente Alin",
	author_email="climente.alin@gmail.com",
	license='MIT',
	py_modules=["flaskwebgui"],
	packages=find_packages(),
	long_description=long_description,
    long_description_content_type="text/markdown",
	package_dir={"":"src"}
)