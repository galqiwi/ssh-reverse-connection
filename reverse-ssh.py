import subprocess
import os
from pathlib import Path
import requests
import tempfile
import getpass
import argparse
import uuid

ssh_flags = '-o UserKnownHostsFile=/dev/null ' \
            '-o StrictHostKeyChecking=no'


parser = argparse.ArgumentParser(description='reverse ssh connection script')
parser.add_argument('--server-ip', default='localhost')
parser.add_argument('--server-username', default='galqiwi')
parser.add_argument('--server-port', default='2222')
parser.add_argument('--exposed-port', default='2223')
parser.add_argument('--local-port', default='22')
args = parser.parse_args()

file_check = os.path.join(tempfile.gettempdir(), f'{uuid.uuid4().hex}.check')
subprocess.run(f'ssh {ssh_flags} {args.server_ip} -p {args.exposed_port} "touch {file_check}"', shell=True,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if os.path.isfile(file_check):
    print('connection is online')
    os.remove(file_check)
else:
    print('connection is offline')
    subprocess.run(f'ssh {ssh_flags} \
                   -R {args.exposed_port}:localhost:{args.local_port} \
                   {args.server_username}@{args.server_ip} -p {args.server_port} -N &', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                   shell=True)
