import sys
from subprocess import Popen
import logging


def build(_):
    logging.basicConfig(level=logging.INFO)
    try:
        Popen(f"{sys.executable} ./protoc.py", shell=True).wait()
    except:
        logging.warning(
            "Could not generate prtobuf files. This is normal if you are installing from release package"
        )
