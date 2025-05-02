from setuptools import setup, find_packages

setup(
  name="talkops",
  version="0.1.0",
  description="TalkOps SDK",
  author="PicoUX",
  license="MIT",
  packages=find_packages(),
  install_requires=[
    "jinja2>=3.1.6",
    "requests>=2.32.3",
    "sseclient-py>=1.8.0",
  ],
  python_requires=">=3.7",
)
