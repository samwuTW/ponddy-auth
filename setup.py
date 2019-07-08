import os
from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='ponddy-auth',
    version=os.environ['VERSION'],
    description='The Ponddy Auth SSO authentication library',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ],
    keywords='Ponddy Auth SSO',
    url='https://github.com/samwuTW/ponddy-auth',
    author='lambdaTW',
    author_email='lambda@lambda.tw',
    license='MIT',
    packages=['ponddy_auth'],
    install_requires=[
        'Django', 'djangorestframework', 'python-jose'
    ],
    zip_safe=False
)
