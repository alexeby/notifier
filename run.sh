#!/bin/bash
cd $PWD

# Get the directory of the script
BASEDIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-$0}"; )" &> /dev/null && pwd 2> /dev/null; )";

cd $BASEDIR
source venv/bin/activate

python main.py

deactivate