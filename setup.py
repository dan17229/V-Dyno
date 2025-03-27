from setuptools import setup, find_packages

setup(
    name="VDyno",
    version="1.0.0",
    description="A PyQt6-based application for a VESC-based dynamometer control, as well as some misc data logging and analysis.",
    author="Daniel Muir",
    author_email="danielmuir167@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PyQt6",
        "pyqtgraph",
        "numpy",
        "cantools",
        "python-can",
        "pyserial"
    ],
    entry_points={
        "gui_scripts": [
            "vdyno=VDyno.VDyno:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)