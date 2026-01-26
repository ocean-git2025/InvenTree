"""Setup file for stock_threshold plugin."""

from setuptools import setup, find_packages
import os

# Read README.md content
with open(os.path.join(os.path.dirname(__file__), "README.md"), "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="inventree-stock-threshold",
    version="1.0.0",
    description="Stock threshold notification plugin for InvenTree",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="InvenTree Community",
    author_email="info@inventree.org",
    url="https://github.com/inventree/inventree-stock-threshold",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['*.md', '*.txt'],
        'stock_threshold': ['static/panels/*'],
    },
    install_requires=[
        "django>=3.2",
        "djangorestframework>=3.12",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Intended Audience :: Manufacturing",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "Topic :: System :: Inventory",
    ],
    python_requires=">=3.8",
) 
