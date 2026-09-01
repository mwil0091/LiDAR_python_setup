# python3-quanergyM8
Python library to read live data from a Quanergy M8 LiDAR.

This library is stand-alone.  It does NOT require (or use) the Quanergy SDK.

![screenshot](/docs/quanergyLidar.jpg?raw=true)


## Hardware Requirements

* Quanergy M8 LiDAR

## Software Requirements

* Numpy
* The example viewer requires Open3d, but you can make your own viewer

## Clone Repo and Setup Virtaul Environement:
```bash
git clone https://github.com/mwil0091/LiDAR_python_setup.git
cd LiDAR_python_setup

python -m venv .venv

.venv\Scripts\activate

python --version
python -m pip install --upgrade pip
python -m pip install numpy setuptools matplotlib

```

## Getting started:
### Example IP Address: 130.194.128.144 (MSI Lab)

```bash
python setup.py install --user
pip install open3d --user

cd examples

# E.g python lidar_with_open3d.py 130.194.128.144
python lidar_with_open3d.py ip_address_of_lidar  # Replace with the IP Addres
```
