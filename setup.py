from setuptools import setup, find_packages

setup(
    name='autopolarizer',
    version='1.1.0',
    description='Control the automatic polarizer holder with Python',
    url='https://github.com/elerac/autopolarizer',
    author='Ryota Maeda',
    author_email='maeda.ryota.elerac@gmail.com',
    license='MIT',
    install_requires=['pyserial'],
    entry_points={'console_scripts': ['autopolarizer= autopolarizer.autopolarizer:main']},
    packages=find_packages()
)
