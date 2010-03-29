from distutils.core import setup


setup(
    name = "django-groups",
    version = "0.1.dev10",
    url = "http://pinaxproject.com/docs/dev/groups.html",
    description = "Django group support (extracted from Pinax)",
    long_description = open("README", "rb").read(),
    author = "Brian Rosner",
    author_email = "brosner@gmail.com",
    license = "MIT",
    packages = [
        "groups",
        "groups.templatetags",
    ],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ]
)
