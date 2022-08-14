import os
import random


def get_local_random_id(byte_count: int = 8) -> str:
    if os.path.exists(f'.netautofsid_{byte_count}.conf'):
        with open(f'.netautofsid_{byte_count}.conf', 'r') as f:
            return f.read()
    else:
        with open(f'.netautofsid_{byte_count}.conf', 'w') as f:
            max_int = 2 ** (byte_count * 8)
            gen = '{:0>8x}'.format(random.randint(0, max_int))
            f.write(gen)
            return gen
