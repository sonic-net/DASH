from setuptools import setup, find_packages

setup(
    name='dash-pipeline-utils',
    version='1.0',
    packages=find_packages(),
    py_modules = ['dash_pipeline_utils'],
    install_requires = [
        'protobuf>=3.20.1',
        'p4runtime'
    ],
    setup_requires = [
        'wheel'
    ],
    description='A Python package of dash pipeline utils',
    license='Apache 2.0',
    author='Junhua Zhai',
    author_email='junhua.zhai@outlook.com',
    url='https://github.com/sonic-net/DASH/tree/main/dash-pipeline/utils',
)
