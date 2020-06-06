# Installation

```bash
virtualenv python=python3 env
source env/bin/activate
pip install -r requirements.txt

./manage.py protoc # Generate protobuf files
./manage.py setup # Generate database
./manage.py runserver
```