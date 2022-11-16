import argparse
import IPython
from traitlets.config import Config

parser = argparse.ArgumentParser(
  description='Open interactive shell where you can perform asynchronous operations'
)

args = parser.parse_args()

IPython.start_ipython(config=Config())
