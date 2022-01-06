import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

tests_require = [
    "pytest>=6.2.5",
    "isort>=5.10.1",
    "black>=21.12b0",
]
setup_requires = ['pytest-runner']
dev_requires = ['pre-commit>=2.16.0']

setuptools.setup(
    name="declarative-faker",
    version="0.0.1",
    author="Franek Jemiolo <f.jemiolo@gmail.com>",
    description="Declarative faker allows you to generate synthetic data from schema definitions using faker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FranekJemiolo/declarative-faker",
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    extras_require={
        "dev": tests_require + dev_requires,
    },
    include_package_data=True,
    packages=setuptools.find_packages(where=".", include=["declarative_faker*"]),
    entry_points={'console_scripts': ["gen_fake = declarative_faker.generate:main"]},
    python_requires='>=3.9',
)
