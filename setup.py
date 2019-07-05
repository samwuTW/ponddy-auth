import os
from setuptools import setup


setup(
    name='ponddy-auth',
    version=os.environ['CIRCLE_TAG'],
    description='The Ponddy Auth SSO authentication library',
    long_description="""
    Provide the class for the Django restful framework authentication.
    Provide the Django model permission class compatible with the restful
    framework, let it can support valid the permission what in this request
    contains the API's permission validation.
    """,
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
