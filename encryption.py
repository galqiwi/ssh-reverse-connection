import hashlib
import base64
import json
import argparse
import getpass


def xor(var, key):
    return bytes(a ^ b for a, b in zip(var, key))


def rep_hash(value, repetitions=16):
    out = [b'']
    for _ in range(repetitions):
        out.append(hashlib.sha512(out[-1] + value).digest())
    return b''.join(out)


def encrypt(string, password, repetitions=16):
    string_data = string.encode()
    string_data = string_data + hashlib.sha256(string_data).digest()
    password_data = rep_hash(password.encode(), repetitions=repetitions)
    if len(string_data) > len(password_data):
        raise ValueError(f'not enough repetitions, {len(string_data) = }, {len(password_data) = }')

    return json.dumps({
        'data': base64.b85encode(xor(string_data, password_data)).decode(),
        'repetitions': repetitions
    })


class BadPasswordError(Exception):
    pass


def decrypt(string, password):
    data_dict = json.loads(string)
    data = data_dict['data']
    repetitions = data_dict['repetitions']
    data = xor(base64.b85decode(data), rep_hash(password.encode(), repetitions=repetitions))
    if hashlib.sha256(data[:-256//8]).digest() != data[-256//8:]:
        raise BadPasswordError('password is incorrect')
    return data[:-256//8].decode()


def main():
    parser = argparse.ArgumentParser(description='Custom encryptor for reverse-ssh project.')
    parser.add_argument('--encrypt', action='store_true', help='encrypt a file (default: decrypt)')
    parser.add_argument('-i', help='input file', required=True)
    parser.add_argument('-o', help='output file', required=True)
    parser.add_argument('-r', action='store', type=int, default=16, help='# of repetitions in hash function')
    parser.add_argument('--password', help='password')
    args = parser.parse_args()
    password = args.password
    if password is None:
        password = getpass.getpass()

    with open(args.i, 'r') as file:
        input_str = file.read()

    if args.encrypt:
        output_str = encrypt(input_str, password, repetitions=args.r)
    else:
        output_str = decrypt(input_str, password)

    with open(args.o, 'w') as file:
        file.write(output_str)


if __name__ == '__main__':
    main()
