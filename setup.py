from setuptools import find_packages, setup

setup(
    name="higher-health",
    version="0.0.1",
    url="http://github.com/praekeltfoundation/higher-health-django",
    license="BSD",
    author="Praekelt Foundation",
    author_email="dev@praekeltfoundation.org",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django~=3.0.0",
        "django-environ>=0.4.5,<0.5",
        "psycopg2-binary>=2.8.3,<2.9",
        "sentry-sdk==0.14.3",
        "django-filter==2.0.0",
        "pycountry==19.8.18",
        "phonenumberslite==8.9.15",
        "requests==2.22.0",
        "django-import-export==2.1.0",
        "django-compressor==2.4",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
