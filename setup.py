""" initial file for task_rest packege """

from setuptools import setup
setup(
    name="task_rest",
    packages=["poly"],
    include_package_data=True,
    install_requires=[
        "flask",
    ],
)
