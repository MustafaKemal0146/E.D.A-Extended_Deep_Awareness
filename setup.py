"""
Setup script for E.D.A - Extended Deep Awareness MCP Tool
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="eda-extended-deep-awareness",
    version="1.0.0",
    author="EDA Development Team",
    description="Extended Deep Awareness MCP Tool for comprehensive data analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Data Scientists",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    license="MIT",
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "advanced": [
            "statsmodels>=0.14.0",
            "networkx>=3.1.0",
            "spacy>=3.6.0",
            "transformers>=4.30.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "eda-mcp-server=mcp_server:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)