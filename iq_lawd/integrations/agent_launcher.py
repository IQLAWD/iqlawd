"""
IQLAWD Agent Launcher — Create Moltbook Agents Without Coding
==============================================================
Wraps the Moltbook registration API to provide a simple,
one-click agent creation flow. Enforces 1-agent-per-Twitter.
"""

import requests
import json
import os
import re
from datetime import datetime

MOLTBOOK_API_KEY = os.getenv("MOLTBOOK_API_KEY") # Set this in your environment
BASE_URL = "https://www.moltbook.com/api/v1"
REGISTRY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "launched_agents.json")


class AgentLauncher:
    """Handles Moltbook agent registration via API."""

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {MOLTBOOK_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "IQLAWD/5.1 (Agent Launcher)"
        }
        self.registry = self._load_registry()

    def _load_registry(self):
        """Load the registry of launched agents (for dedup)."""
        try:
            if os.path.exists(REGISTRY_FILE):
                with open(REGISTRY_FILE, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return {"agents": [], "x_handles": {}}

    def _save_registry(self):
        """Persist registry to disk."""
        try:
            os.makedirs(os.path.dirname(REGISTRY_FILE), exist_ok=True)
            with open(REGISTRY_FILE, "w") as f:
                json.dump(self.registry, f, indent=2)
        except Exception as e:
            print(f"Registry save error: {e}")

    def validate_input(self, name: str, description: str, x_handle: str):
        """Validate user inputs before calling Moltbook API."""
        errors = []

        # Name validation
        name = name.strip()
        if len(name) < 3 or len(name) > 20:
            errors.append("Agent name must be 3-20 characters.")
        if not re.match(r'^[a-zA-Z0-9_]+$', name):
            errors.append("Agent name can only contain letters, numbers, and underscores.")

        # Description validation
        description = description.strip()
        if len(description) < 10:
            errors.append("Description must be at least 10 characters.")
        if len(description) > 280:
            errors.append("Description must be under 280 characters.")

        # X handle validation
        x_handle = x_handle.strip().lstrip("@").lower()
        if not x_handle:
            errors.append("Twitter/X handle is required.")
        if not re.match(r'^[a-zA-Z0-9_]{1,15}$', x_handle):
            errors.append("Invalid Twitter/X handle format.")

        # Check 1-per-Twitter limit
        if x_handle in self.registry.get("x_handles", {}):
            existing = self.registry["x_handles"][x_handle]
            errors.append(f"This Twitter account already has an agent: '{existing['agent_name']}'. Limit: 1 agent per Twitter account.")

        return errors, name, description, x_handle

    def launch_agent(self, name: str, description: str, x_handle: str):
        """
        Register a new agent on Moltbook.
        Returns claim_url and verification_code on success.
        """
        # Validate
        errors, name, description, x_handle = self.validate_input(name, description, x_handle)
        if errors:
            return {"success": False, "errors": errors}

        # Call Moltbook registration API
        try:
            payload = {
                "name": name,
                "description": description,
                "x_handle": x_handle
            }

            print(f"🚀 Launching agent '{name}' for @{x_handle}...")
            resp = requests.post(
                f"{BASE_URL}/agents/register",
                json=payload,
                headers=self.headers,
                timeout=15
            )

            if resp.status_code in [200, 201]:
                data = resp.json()

                # Extract the key info
                agent_info = data.get("agent", data)
                result = {
                    "success": True,
                    "agent_id": agent_info.get("id", ""),
                    "agent_name": agent_info.get("name", name),
                    "claim_url": agent_info.get("claim_url", data.get("claim_url", "")),
                    "verification_code": agent_info.get("verification_code", data.get("verification_code", "")),
                    "profile_url": f"https://moltbook.com/u/{name}",
                }

                # Record in registry
                self.registry["x_handles"][x_handle] = {
                    "agent_name": name,
                    "agent_id": result["agent_id"],
                    "launched_at": datetime.now().isoformat()
                }
                self.registry["agents"].append({
                    "name": name,
                    "x_handle": x_handle,
                    "agent_id": result["agent_id"],
                    "launched_at": datetime.now().isoformat()
                })
                self._save_registry()

                print(f"✅ Agent '{name}' launched successfully!")
                return result

            elif resp.status_code == 409:
                return {"success": False, "errors": [f"Agent name '{name}' is already taken on Moltbook."]}
            elif resp.status_code == 429:
                return {"success": False, "errors": ["Rate limit reached. Please try again in a few minutes."]}
            else:
                error_msg = resp.text[:200] if resp.text else f"HTTP {resp.status_code}"
                return {"success": False, "errors": [f"Moltbook API error: {error_msg}"]}

        except requests.exceptions.Timeout:
            with open("/root/iqlawd/launcher_debug.log", "a") as f:
                f.write(f"{datetime.now()} - TIMEOUT\n")
            return {"success": False, "errors": ["Moltbook API timed out. Please try again."]}
        except Exception as e:
            print(f"❌ Launch error: {e}")
            with open("/root/iqlawd/launcher_debug.log", "a") as f:
                f.write(f"{datetime.now()} - ERROR: {e}\n")
            return {"success": False, "errors": [f"Unexpected error: {str(e)}"]}

    def get_stats(self):
        """Get launcher statistics."""
        return {
            "total_launched": len(self.registry.get("agents", [])),
            "recent": self.registry.get("agents", [])[-5:]
        }
