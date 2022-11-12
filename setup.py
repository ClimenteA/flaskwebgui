from setuptools import setup, find_packages

# Distribute py wheels
# python3 setup.py bdist_wheel sdist
# twine check dist/*
# cd dist
# twine upload *

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="flaskwebgui",
    version="1.0.0",
    description="Create desktop applications with Flask/Django/FastAPI!",
    url="https://github.com/ClimenteA/flaskwebgui",
    author="Climente Alin",
    author_email="climente.alin@gmail.com",
    license="MIT",
    py_modules=["flaskwebgui"],
    install_requires=["psutil==5.9.4"],
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
)
