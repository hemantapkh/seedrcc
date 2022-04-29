import setuptools

with open("README.md", "r") as fh:
    readme = fh.read()

setuptools.setup(
    name="seedrcc",
    version="0.0.1",
    author="Hemanta Pokharel",
    author_email="hemantapkh@yahoo.com",
    description="Python API wrapper of seedr.cc",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=["requests"],
    url="https://github.com/hemantapkh/seedrcc",
    project_urls={
        "Documentation": "https://seedrcc.readthedocs.io/en/latest/",
        "Issue tracker": "https://github.com/hemantapkh/seedrcc/issues",
      },
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    python_requires='>=3.0',
)
