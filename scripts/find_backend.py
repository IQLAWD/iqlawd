import paramiko
import sys

HOST = "62.72.46.228"
USER = "root"
PASSWORD = "sayalupa"

def check_backend_path():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=10)
        
        commands = [
            "pm2 show iqlawd-api",
            "ls -F /root/iq_lawd_v2/iq_lawd/"
        ]
        
        for cmd in commands:
            print(f"--- Running: {cmd} ---")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            print(stdout.read().decode())
            print(stderr.read().decode())
            
        ssh.close()
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    check_backend_path()
