#!/bin/bash

BASE_DIR="$(dirname $0)"
python -m grpc_tools.protoc -I"$BASE_DIR/../../protos" --python_out="$BASE_DIR/../src/managers/com" --grpc_python_out="$BASE_DIR/../src/managers/com" "$BASE_DIR/../../protos/com.proto"