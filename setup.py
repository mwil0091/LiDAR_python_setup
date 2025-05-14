import numpy as np
import sys
from setuptools import setup, Extension  # Using setuptools instead of distutils

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

# Define libraries and extra compile args for Windows
libraries = []
if sys.platform == 'win32':
    libraries = ['ws2_32']  # Link against Winsock2

module = Extension(
    'cQuanergyM8',
    sources=['cpp/cQuanergyM8_module.cpp'],
    include_dirs=[np.get_include()],  # NumPy headers
    libraries=libraries,  # Link ws2_32.lib on Windows
    extra_compile_args=['-DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION']  # Avoid NumPy deprecation warnings
)

setup(
    name='QuanergyM8',
    version='0.1',
    description='Parser for the Quanergy M8 LiDAR',
    packages=['quanergyM8'],
    ext_modules=[module],
)

