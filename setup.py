"""The setup script."""

from setuptools import setup, find_packages
try:  # pip version >= 10.0
    from pip._internal.req import parse_requirements
    from pip._internal.download import PipSession
except ImportError:  # pip version < 10.0
    from pip.req import parse_requirements
    from pip.download import PipSession

install_reqs = parse_requirements('requirements.txt', session=PipSession())
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='neo-python',
    python_requires='>=3.6',
    version='0.0.1',
    description="Python Node and SDK for the NEO blockchain",
    # long_description=readme,
    author="suzumi49n",
    author_email='ganimata39@gmail.com',
    maintainer="suzumi49n",
    maintainer_email='chris@cityofzion.io',
    url='https://github.com/CityOfZion/neo-python',
    packages=find_packages(include=['bin']),
    entry_points={
        'console_scripts': [
            # 'np-prompt=neo.bin.prompt:main',
            'zp-api-server=bin.api_server:main'
        ],
    },
    include_package_data=True,
    install_requires=reqs,
    license="MIT license",
    zip_safe=False,
    keywords='neo, python, node',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
