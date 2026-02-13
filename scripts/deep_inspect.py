import paramiko

HOST = "62.72.46.228"
USER = "root"
PASSWORD = "sayalupa"

def deep_inspect():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASSWORD)
    
    print("🔍 Inspecting sockets...")
    stdin, stdout, stderr = ssh.exec_command("ss -lptn 'sport = :3005'")
    print(stdout.read().decode())
    
    print("🔍 Fetching HTML for any hint of current version...")
    stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:3005 | head -n 50")
    print(stdout.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    deep_inspect()
