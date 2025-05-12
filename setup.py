from setuptools import setup, find_packages
import os

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements文件
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# 读取版本号
about = {}
with open(os.path.join("biokg_builder", "__version__.py"), "r", encoding="utf-8") as f:
    exec(f.read(), about)

setup(
    name="biokg-builder",
    version=about["__version__"],
    author="Zaoqu Liu",
    author_email="liuzaoqu@163.com",
    description="AI-driven biomedical literature knowledge graph generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Zaoqu-Liu/biokg-builder",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.910",
        ],
    },
    entry_points={
        "console_scripts": [
            "biokg-builder=biokg_builder.cli:main",
        ],
    },
    include_package_data=True,
    keywords="bioinformatics knowledge-graph pubmed nlp",
    project_urls={
        "Bug Reports": "https://github.com/Zaoqu-Liu/biokg-builder/issues",
        "Source": "https://github.com/Zaoqu-Liu/biokg-builder",
        "Documentation": "https://biokg-builder.readthedocs.io/",
    },
)