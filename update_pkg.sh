#!/bin/bash

pip3 uninstall scriptmonkey
rm -rf dist/
python3 setup.py sdist bdist_wheel
twine upload dist/*