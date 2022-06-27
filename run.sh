BASEDIR=$(dirname "$0")
cd $BASEDIR
source venv/bin/activate

python main.py

deactivate