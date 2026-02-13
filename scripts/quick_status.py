#!/usr/bin/env python3
"""Quick VPS status check"""
import paramiko

HOST = "62.72.46.228"
USER = "root"
PASSWORD = "sayalupa"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)

def run(cmd, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode().strip()

print("📊 System Load:")
print(run("uptime"))

print("\n📋 PM2 Status:")
print(run("pm2 list"))

print("\n🌐 API Health:")
print(f"  Port 8000: HTTP {run('curl -s -o /dev/null -w \"%{http_code}\" http://localhost:8000/ 2>&1')}")
print(f"  /listings: HTTP {run('curl -s -o /dev/null -w \"%{http_code}\" http://localhost:8000/listings 2>&1')}")
print(f"  /feed: HTTP {run('curl -s -o /dev/null -w \"%{http_code}\" http://localhost:8000/feed 2>&1')}")
print(f"  /api/agents: HTTP {run('curl -s -o /dev/null -w \"%{http_code}\" http://localhost:8000/api/agents 2>&1')}")

print("\n🌐 Frontend Health:")
print(f"  Port 3005: HTTP {run('curl -s -o /dev/null -w \"%{http_code}\" http://localhost:3005/ 2>&1')}")

print("\n🔌 Active Ports:")
print(run("ss -tlnp | grep -E '3005|8000'"))

ssh.close()
