from setuptools import setup, find_packages

setup(
    name="omnidrive-cli",
    version="0.1.0",
    packages=find_packages(include=["omnidrive*"]),
    entry_points={
        "console_scripts": [
            "omnidrive=omnidrive.cli:cli",
        ],
    },
    python_requires=">=3.12,<3.14",
)
