import os
from setuptools import setup

setup(
    name='minidriver',
    packages=["minidriver"],
    version='10.9.8.7.6.5.4.3.2.1',
    entry_points={
        'console_scripts': [
            'rubberstamp = minidriver.rubberstamp:rubberstamp'
        ],
    },
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    description="Minimal Computing Interfaces to Google Drive",
    url="http://github.com/bmschmidt/minidriver",
    author="Benjamin Schmidt",
    author_email="bmschmidt@gmail.com",
    license="MIT",
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        "Natural Language :: English",
        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',
        "Operating System :: Unix",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    install_requires=["google-api-python-client", "google-auth-httplib2",
    "google-auth-oauthlib", "pyyaml", "openpyxl", "pypandoc"
    ]
)
