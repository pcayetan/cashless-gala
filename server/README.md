# Installation

```bash
poetry install
poetry shell

cash setup 2019.json # Generate database by importing 2019's database
cash runserver

# You can use custom settings by creating a settings_custom.py file
# You can also configure the location of those settings through the CFG env variable
```

# Testing

```bash
poetry install -E testing # Install testing dependencies
pytest  # Launch all tests
pytest -k "TestBalance" # Only launch test cases of TestBalance class
pytest -k "test_existing_user" # Only test one method of TestBalance class
# Generate html coverage report
pytest --cov-report=html --cov=cashless_server
```

# Developement

```bash
# Rebuild protobuf files
cash protoc
```
