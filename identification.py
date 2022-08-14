import os
import random


def get_local_random_id() -> str:
    if os.path.exists('.netautofsid.conf'):
        with open('.netautofsid.conf', 'r') as f:
            return f.read()
    else:
        with open('.netautofsid.conf', 'w') as f:
            gen = hex(random.randint(0, 0xffffffffffffffff))[2:]
            f.write(gen)
            return gen
