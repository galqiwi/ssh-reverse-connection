import subprocess
import os
from pathlib import Path
import requests
import tempfile
import getpass
import argparse
from encryption import decrypt, BadPasswordError


parser = argparse.ArgumentParser(description='setup for reverse ssh connection')
parser.add_argument('--my-public-key', default=os.path.expanduser('~/.ssh/id_rsa.pub'))
parser.add_argument('--key-url', default='https://galqiwi.ru/id_rsa.decrypted')
parser.add_argument('--server-ip', default='localhost')
parser.add_argument('--server-port', default='2222')
parser.add_argument('--password')
args = parser.parse_args()

ssh_flags = '-o UserKnownHostsFile=/dev/null ' \
            '-o StrictHostKeyChecking=no'

pub_file = args.my_public_key
ssh_dir = os.path.expanduser('~/.ssh/')
authorized_keys_path = os.path.join(ssh_dir, 'authorized_keys')

os.makedirs(ssh_dir, exist_ok=True, mode=0o700)
Path(authorized_keys_path).touch(mode=0o700)
print(f'touched {authorized_keys_path}')

with open(authorized_keys_path, 'r') as file:
    authorized_keys = [_.strip() for _ in file.readlines()]

with open(pub_file, 'r') as file:
    public_key = file.read().strip()

if public_key not in authorized_keys:
    with open(authorized_keys_path, 'a') as file:
        file.write(f'{public_key}\n')
    print(f'set up your autologin')
else:
    print(f'your autologin is already set up')

password = args.password
if password is None:
    password = getpass.getpass('Enter your password for the cloud key: ')

key_fd, key_filename = tempfile.mkstemp()

try:
    with os.fdopen(key_fd, 'w') as file:
        file.write(decrypt(requests.get(args.key_url).text, password))

    print('password is correct')

    subprocess.run(f'ssh-copy-id -f -i "{pub_file}" {ssh_flags} -o "IdentityFile {key_filename}" \
                   {args.server_ip} -p {args.server_port}',
                   shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    subprocess.run(f'ssh {args.server_ip} {ssh_flags} -p {args.server_port} "echo done!"', stderr=subprocess.DEVNULL,
                   shell=True)
except BadPasswordError:
    print('password is incorrect')
finally:
    os.remove(key_filename)
