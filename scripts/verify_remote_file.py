import paramiko
import time

HOST = "62.72.46.228"
USER = "root"
PASSWORD = "sayalupa"

def verify_remote():
    print(f"🔌 Connecting to {HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD)
        
        print("\n🔍 Checking remote verification_service.py content...")
        cmd = "grep -A 5 'HARDCODED' /root/iqlawd/backend/iq_lawd/verification/verification_service.py"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode())
        
        print("\n🔍 Checking UI Error Log specifically...")
        cmd_err = "cat /root/.pm2/logs/iqlawd-ui-error.log | tail -n 20"
        stdin, stdout, stderr = ssh.exec_command(cmd_err)
        print(stdout.read().decode())
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    verify_remote()
