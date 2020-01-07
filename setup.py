import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="clive_log",
    version="0.0.1",
    author="Nathan",
    author_email="strigusconsilium@gmail.com",
    description="A CLI live logging package",
    url="https://github.com/heidtn/clive_log",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.6',
)
