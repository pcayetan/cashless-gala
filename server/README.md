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
cash test # Launch all tests
cash test TestBalance # Only launch test cases of TestBalance class
cash test TestBalance.test_existing_user # Only test one method of TestBalance class
```

# Developement

```bash
# Rebuild protobuf files
cash protoc
```
