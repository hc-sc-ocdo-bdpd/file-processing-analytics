from setuptools import setup

# Function to read dependencies from the requirements.txt file
def read_requirements():
    with open("requirements.txt") as req_file:
        return req_file.readlines()

setup(
    name="file-processing-analytics",
    version="1.0.0",
    install_requires=read_requirements(), # Dependencies listed in requirements.txt
)
