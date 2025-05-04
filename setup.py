from setuptools import setup, find_packages

setup(
    name='talkops',
    version='1.0.7',
    author='PicoUX',
    description="TalkOps SDK",
    long_description=open('README.md',encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    packages=find_packages(),
    url='https://github.com/talkops/sdk-python',
    python_requires='>=3.9',
    project_urls={
        "Homepage":'https://talkops.app',
        'Issues': 'https://github.com/talkops/sdk-python/issues',
        'Source': 'https://github.com/talkops/sdk-python',
    },
    install_requires=['jinja2', 'requests', 'sseclient-py'],
    keywords=['sdk'],
    classifiers=[
      "Programming Language :: Python :: 3",
      "Operating System :: OS Independent",
    ],
    include_package_data=True,
)
