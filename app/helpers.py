from base64 import b64encode
from os import urandom

def generate_name() -> str: return b64encode(urandom(8)).decode("utf-8")[:-1]

