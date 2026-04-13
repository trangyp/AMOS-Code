"""Setup script for AMOS Brain + ClawSpring integration."""
from setuptools import setup, find_packages

with open("README.MD", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="amos-brain-clawspring",
    version="1.0.0",
    author="Trang Phan (Trang Q. Phan)",
    author_email="trang@amos-project.dev",
    description="AMOS Brain cognitive architecture integrated with ClawSpring agent runtime",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/trangyp/AMOS-Code",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        # Core dependencies
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
        # Optional clawspring integration
        # "clawspring>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "web": [
            "fastapi>=0.100.0",
            "uvicorn>=0.23.0",
        ],
        "mcp": [
            # MCP protocol support
        ],
    },
    entry_points={
        "console_scripts": [
            "amos=amos:main",
            "amos-clawspring=amos_clawspring:main",
            "amos-mcp-server=amos_mcp_server:main",
            "amos-demo=demo_amos_brain:main",
        ],
    },
    include_package_data=True,
    package_data={
        "amos_brain": ["*.json"],
        "_AMOS_BRAIN": ["**/*.json"],
    },
)
