import pathlib

from setuptools import setup

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.rst").read_text(encoding="utf-8")

setup(
    name="weighing-server",
    description="A Websocket server used to get weight for a weighing device.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author="Laurent Mignon",
    author_email="laurent.mignon@acsone.com",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    package_dir={"": "src"},
    packages=["weighing_server"],
    scripts=["weighingsrvd"],
    python_requires=">=3.6",
    install_requires=["fastapi", "pyserial", "uvicorn[standard]"],
)
