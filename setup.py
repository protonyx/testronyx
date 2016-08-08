"""
Setuptools build file
"""
__author__ = 'kkennedy'

from setuptools import setup, find_packages

import build

def build_package():
    # Generate version file
    #version, full_version = build.generate_ver()

    # Setup Metadata
    setup_meta = dict(
        # Application name
        name='Testronyx',

        # Version number
        #version=full_version,

        # Application author details
        author="Kevin Kennedy",
        author_email="protonyx@users.noreply.github.com",

        # License
        license="MIT",

        # Details
        url="https://github.com/protonyx/testronyx",

        # Description
        description='Testronyx Test Automation',

        # Platforms
        platforms=["Windows", "Mac OS-X", "Linux"],

        # Long Description
        long_description=open("README.rst").read(),

        # Classifiers
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX :: Linux",
            "Operating System :: MacOS :: MacOS X",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.7",
            "Topic :: Software Development :: Libraries :: Python Modules"
        ],

        # Packages
        packages=find_packages(exclude=['tests']),

        # Package data - e.g. non-python modules
        # package_data = {},
        # Include additional files into the package
        include_package_data=True,

        # Dependencies
        install_requires=['flask', 'requests', 'pyzmq',
                          'python-dateutil', 'appdirs'],

        extras_require={},

        # Script entry points
        entry_points={},

        # Can the project run from a zip file?
        zip_safe=False
    )

    # Setuptools
    setup(**setup_meta)

if __name__ == '__main__':
    build_package()