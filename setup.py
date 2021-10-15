from setuptools import setup

setup(
    name='RavePY',
    version='0.0.1',
    description='A framework for analyzing music in real time using python',
    url='git@github.com:slenderman00/Pip-Grindr-Web-Access.git',
    author='Joar Heimonen',
    author_email='joarheimonen@live.no',
    license='mit',
    packages=['RavePy'],
    zip_safe=False,
    install_requires=[
        'numpy==1.21.2',
        'PyAudio==0.2.11',
    ]
)