# ssh-reverse-connection

scripts for establishing reverse ssh connection

## setup
```
pip install requests --user
python3 setup.py --server-ip <server_ip> --server-port <server_port> --server-username galqiwi --password <password>

```

## crontab scrypt
```
python3 reverse-ssh.py --exposed-port <client_port> --server-ip <server_ip> --server-port <server_port>
```