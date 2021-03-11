"""Setup script."""
from setuptools import setup

long_description = open("README.md").read()

setup(
    name="pyatag",
    license="MIT",
    url="https://github.com/MatsNl/pyatag",
    author="@MatsNL",
    description="Python module to talk to Atag One.",
    packages=["pyatag"],
    zip_safe=True,
    platforms="any",
    install_requires=list(val.strip() for val in open("requirements.txt")),
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
