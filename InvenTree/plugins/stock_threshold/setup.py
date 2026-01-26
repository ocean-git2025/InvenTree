"""Setup configuration for Stock Threshold plugin."""

from setuptools import setup, find_packages

setup(
    name="inventree-stock-threshold",
    version="1.0.0",
    description="Stock threshold management plugin for InvenTree",
    long_description="""Stock threshold management plugin for InvenTree that provides:
    - Background configuration of inventory thresholds
    - Reminder triggering on inventory changes
    - UI alerts for low thresholds in inventory lists
    - Batch import/export of thresholds
    """,
    url="https://github.com/inventree/inventree-stock-threshold",
    author="InvenTree Community",
    author_email="info@inventree.org",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'stock_threshold': ['static/panels/*']
    },
    zip_safe=False,
    install_requires=[
        "inventree>=0.12.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Manufacturing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
        "inventree_plugins": [
            "StockThreshold = stock_threshold.plugin:StockThresholdPlugin",
        ],
    },
)
