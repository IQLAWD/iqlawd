import paramiko
import os

HOST = "62.72.46.228"
USER = "root"
PASSWORD = "sayalupa"

def get_logs_sftp():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"Connecting to {HOST} via SFTP...")
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=20)
        sftp = ssh.open_sftp()
        
        target_files = [
            "/root/.pm2/logs/iqlawd-ui-v3-error.log",
            "/root/.pm2/logs/iqlawd-ui-v3-out.log"
        ]
        
        for remote_path in target_files:
            local_path = os.path.join("z:/CODINGAN/IQLAWD", os.path.basename(remote_path))
            try:
                print(f"Downloading {remote_path}...")
                sftp.get(remote_path, local_path)
                print(f"✅ Saved to {local_path}")
                # Read last lines of the downloaded file
                with open(local_path, "r", errors="ignore") as f:
                    lines = f.readlines()
                    print(f"--- Last 10 lines of {os.path.basename(remote_path)} ---")
                    print("".join(lines[-10:]))
            except Exception as e:
                print(f"Could not download {remote_path}: {e}")
                
        sftp.close()
        ssh.close()
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    get_logs_sftp()
