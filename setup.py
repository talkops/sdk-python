from setuptools import setup, find_packages

setup(
    name='talkops',
    version='1.2.1',
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
    install_requires=['aiosseclient', 'jinja2', 'nest_asyncio', 'requests'],
    keywords=['sdk'],
    classifiers=[
      "Programming Language :: Python :: 3",
      "Operating System :: OS Independent",
    ],
    include_package_data=True,
)
