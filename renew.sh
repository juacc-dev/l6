#!/bin/bash

printf "y\n" | pip uninstall pylabo
mkdir pylabo && cp -r ../pylabo/* pylabo
pip install ./pylabo
rm -rf ./pylabo
