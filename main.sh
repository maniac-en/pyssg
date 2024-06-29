export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python3 src/main.py
python3 server.py --dir public
