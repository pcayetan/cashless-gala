from subprocess import Popen
import sys
import fileinput


def build_protoc():
    p = Popen(
        "%s -m grpc_tools.protoc -I%s --python_out=%s --grpc_python_out=%s %s"
        % (
            sys.executable,
            "../protos",
            "./cashless_server/",
            "./cashless_server/",
            "../protos/com.proto",
        ),
        shell=True,
    )
    p.wait()
    # Fix import path issues
    with fileinput.FileInput("cashless_server/com_pb2_grpc.py", inplace=True) as file:
        for line in file:
            print(
                line.replace("import com_pb2", "import cashless_server.com_pb2"),
                end="",
            )


if __name__ == "__main__":
    build_protoc()
