from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="grape-variety-extractor",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Extract, parse, and translate grape variety information from PDF files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/grape-variety-extractor",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing",
    ],
    python_requires=">=3.10",
    install_requires=[
        "pdfplumber>=0.10.0",
        "openai>=1.0.0",
        "anthropic>=0.18.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "grape-extractor=grape_extractor.main:main",
        ],
    },
)
