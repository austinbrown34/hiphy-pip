import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hiphy",
    version="0.0.1",
    author="Austin Brown",
    author_email="austinbrown34@gmail.com",
    description="A python package making videos dance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/austinbrown34/hiphy-pip",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ),
    scripts=['scripts/hiphy'],
)