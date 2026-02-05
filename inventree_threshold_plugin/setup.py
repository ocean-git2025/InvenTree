"""Setup configuration for InvenTree Stock Threshold Plugin."""

from setuptools import setup, find_packages

from inventree_threshold_plugin.version import PLUGIN_VERSION

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='inventree-threshold-plugin',
    version=PLUGIN_VERSION,
    description='InvenTree plugin for stock threshold warnings',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='InvenTree Community',
    author_email='',
    license='MIT',
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.9',
    install_requires=[
        'Django>=4.2.0',
        'djangorestframework>=3.14.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Manufacturing',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    entry_points={
        'inventree_plugins': [
            'StockThresholdPlugin = inventree_threshold_plugin.plugin:StockThresholdPlugin'
        ]
    },
)
