# Installation

```bash
virtualenv python=python3 env
source env/bin/activate
pip install -r requirements.txt

./manage.py protoc # Generate protobuf files
./manage.py setup --import 2019.json # Generate database
./manage.py runserver
```

# Testing

```bash
./manage.py test # Launch all tests
./manage.py test TestBalance # Only launch test cases of TestBalance class
./manage.py test TestBalance.test_existing_user # Only test one method of TestBalance class
```