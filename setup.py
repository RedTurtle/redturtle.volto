# -*- coding: utf-8 -*-
"""Installer for the redturtle.volto package."""

from setuptools import find_packages
from setuptools import setup


long_description = "\n\n".join(
    [
        open("README.rst").read(),
        open("CONTRIBUTORS.rst").read(),
        open("CHANGES.rst").read(),
    ]
)


setup(
    name="redturtle.volto",
    version="4.1.1",
    description="Helper package to setup a RedTurtle's Plone site ready to work with Volto.",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone",
    author="RedTurtle Technology",
    author_email="sviluppo@redturtle.it",
    url="https://github.com/collective/redturtle.volto",
    project_urls={
        "PyPI": "https://pypi.python.org/pypi/redturtle.volto",
        "Source": "https://github.com/RedTurtle/redturtle.volto",
        "Tracker": "https://github.com/RedTurtle/redturtle.volto/issues",
        # 'Documentation': 'https://redturtle.volto.readthedocs.io/en/latest/',
    },
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["redturtle"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=[
        "setuptools",
        "collective.volto.cookieconsent",
        "collective.monkeypatcher",
        "collective.purgebyid",
        "kitconcept.seo>=2.0.0",
        "plone.volto>3.1.0",
        "plone.restapi>=8.16.1",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            "plone.testing>=5.0.0",
            "plone.app.contenttypes",
            "plone.app.robotframework[debug]",
            "collective.MockMailHost",
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = redturtle.volto.locales.update:update_locale
    """,
)
