# Always prefer setuptools over distutils
import setuptools

setuptools.setup(
    name="ec2_control",
    version="0.1.0",
    author="Ben Snyder",
    author_email="johnbensnyder@gmail.com",
    description="Simple control tools for EC2",
    long_description_content_type="text/markdown",
    url="https://github.com/johnbensnyder/ec2_control",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=[
        "boto3 >= 1.12.46",
        "PyYAML >= 5.3.1",
        "paramiko >= 2.5.1",
        "scp >= 0.13.2",
        "s3fs >= 0.4.2"
    ]
)