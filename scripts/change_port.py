import paramiko

HOST = "62.72.46.228"
USER = "root"
PASSWORD = "sayalupa"

def change_port():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD)
        print("\n🔌 Changing Frontend Port to 3005...")
        
        # 1. Stop existing process
        print("Stopping old process...")
        ssh.exec_command("pm2 delete iqlawd-ui")
        
        # 2. Update package.json
        print("Updating package.json...")
        package_json = """
{
  "name": "iqlawd-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start -p 3005",
    "lint": "next lint"
  },
  "dependencies": {
    "react": "^18",
    "react-dom": "^18",
    "next": "14.1.0",
    "framer-motion": "^11.0.3",
    "lucide-react": "^0.330.0",
    "recharts": "^2.12.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.1"
  },
  "devDependencies": {
    "typescript": "^5",
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "autoprefixer": "^10.0.1",
    "postcss": "^8",
    "tailwindcss": "^3.3.0",
    "eslint": "^8",
    "eslint-config-next": "14.1.0"
  }
}
"""
        cmd_update_pkg = f"echo '{package_json}' > /root/iqlawd/frontend/package.json"
        stdin, stdout, stderr = ssh.exec_command(cmd_update_pkg)
        if stdout.channel.recv_exit_status() != 0:
            print(f"Error updating package.json: {stderr.read().decode()}")
            return

        # 3. Start new process
        print("Starting process on port 3005...")
        cmd_start = "cd /root/iqlawd/frontend && pm2 start 'npm start' --name 'iqlawd-ui'"
        stdin, stdout, stderr = ssh.exec_command(cmd_start)
        print(stdout.read().decode())
        
        # 4. Save PM2
        ssh.exec_command("pm2 save")
        
        # 5. Verify
        print("Verifying port 3005...")
        stdin, stdout, stderr = ssh.exec_command("curl -I http://localhost:3005")
        print(stdout.read().decode())
        
    except Exception as e:
        print(e)
    finally:
        ssh.close()

if __name__ == "__main__":
    change_port()
