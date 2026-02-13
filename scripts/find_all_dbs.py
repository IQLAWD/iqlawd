import paramiko

HOST = "62.72.46.228"
USER = "root"
PASSWORD = "sayalupa"

def find_dbs():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=15)
        
        print("Searching for .db files in /root...")
        stdin, stdout, stderr = ssh.exec_command("find /root -name '*.db'")
        db_files = stdout.read().decode().strip().split('\n')
        
        for db in db_files:
            if not db: continue
            print(f"\nChecking {db}...")
            stdin, stdout, stderr = ssh.exec_command(f"sqlite3 {db} 'SELECT COUNT(*) FROM agents;' 2>/dev/null")
            count = stdout.read().decode().strip()
            print(f"Agent Count: {count if count else 'Table not found'}")
            
            if count and count != "0":
                print(f"✅ FOUND DATA IN {db}")
                
        ssh.close()
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    find_dbs()
