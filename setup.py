"""
Setup script for Arduino Firmata Controller
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="arduino-firmata-controller",
    version="1.0.0",
    author="Dustin Jonker",
    author_email="your.email@example.com",
    description="A GUI application for controlling Arduino boards via Firmata protocol",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/arduino-firmata-controller",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: System :: Hardware",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "arduino-controller=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)