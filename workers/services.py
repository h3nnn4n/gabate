import json
from subprocess import PIPE, Popen


def run_agent():
    payload_str = json.dumps(payload)
    print(payload_str)
    print(type(payload_str))
    args = ["../gabate", "../roms/tetris.gb", payload_str]
    print(args)
    with Popen(args, stdout=PIPE, stderr=PIPE) as proc:
        output = proc.stdout.read()
        print(proc.stderr.read())

    return output.decode()


payload = {
    "agent": {
        "weights": [
            1.8323,
            4.1721,
            0.5793,
            -1.1937,
            -7.0811,
            -5.8301,
            -1.8678,
            1.4194,
            -5.4499,
            -1.5089,
            -5.5489,
            6.0940,
            -6.7862,
            6.7634,
            -1.2399,
            1.6776,
            -6.6206,
            3.2301,
            2.9444,
            3.5875,
            6.7551,
            0.1202,
            3.9286,
            -7.2551,
            -1.2929,
            4.4366,
            -2.5105,
            2.3231,
            -3.2543,
            -5.1079,
            -0.3359,
            -1.8405,
            4.4073,
            5.1667,
            -7.0309,
            0.9505,
            2.1215,
            -2.0938,
            -4.4883,
            3.9653,
            -4.8069,
            -6.4642,
        ]
    }
}
