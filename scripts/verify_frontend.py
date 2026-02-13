import paramiko
import time

HOST = "62.72.46.228"
USER = "root"
PASSWORD = "sayalupa"

def verify_frontend():
    print(f"🔌 Connecting to {HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD)
        
        print("\n🔍 Checking PM2 List...")
        stdin, stdout, stderr = ssh.exec_command("pm2 list")
        print(stdout.read().decode())
        
        print("\n🔍 CURL localhost:3005...")
        stdin, stdout, stderr = ssh.exec_command("curl -I http://localhost:3005")
        print(stdout.read().decode())
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    verify_frontend()
