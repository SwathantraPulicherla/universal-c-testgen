from setuptools import setup, find_packages

setup(
    name="universal-c-testgen",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "google-generativeai>=0.3.0",
        "python-dotenv>=0.19.0",
    ],
    entry_points={
        'console_scripts': [
            'c-testgen=scripts.run_testgen:main',
        ],
    },
    python_requires='>=3.8',
)