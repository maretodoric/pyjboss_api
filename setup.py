import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyjboss_api",
    version="2023.5.0b1",
    license="GNU General Public License v3.0",
    author="Marko Todorić",
    author_email="maretodoric@gmail.com",
    description="Python module that provides connection to WildFly API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/maretodoric/pyjboss_api",
    #py_modules=['pyjboss'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires = ['requests', 'jmespath'],
    python_requires='>=3.6',
)
