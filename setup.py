from setuptools import setup, find_packages

# Use find_packages to automatically discover all packages
setup(
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)