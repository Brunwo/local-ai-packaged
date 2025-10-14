#!/usr/bin/env python3
"""
GitHub Secrets Manager for Local AI Packaged
Manages environment secrets between local .env file and GitHub repository secrets

Usage:
  python github-secrets-manager.py push    # Push secrets to GitHub
  python github-secrets-manager.py pull    # Pull secrets from GitHub
  python github-secrets-manager.py list    # List all secrets
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional

class GitHubSecretsManager:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_repo = os.getenv('GITHUB_REPOSITORY', 'Brunwo/local-ai-packaged')
        self.env_file = Path('.env')

        if not self.github_token:
            print("❌ Error: GITHUB_TOKEN environment variable is required")
            print("   Set it with: export GITHUB_TOKEN=your_github_token")
            sys.exit(1)

        # Extract owner/repo from repository string
        if '/' in self.github_repo:
            self.owner, self.repo = self.github_repo.split('/', 1)
        else:
            print("❌ Error: Invalid GITHUB_REPOSITORY format")
            sys.exit(1)

        self.base_url = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        self.headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }

    # List of environment variables that are secrets (not parameters)
    SECRET_VARS = [
        'N8N_ENCRYPTION_KEY',
        'N8N_USER_MANAGEMENT_JWT_SECRET',
        'POSTGRES_PASSWORD',
        'JWT_SECRET',
        'ANON_KEY',
        'SERVICE_ROLE_KEY',
        'DASHBOARD_PASSWORD',
        'NEO4J_AUTH',
        'CLICKHOUSE_PASSWORD',
        'MINIO_ROOT_PASSWORD',
        'LANGFUSE_SALT',
        'NEXTAUTH_SECRET',
        'ENCRYPTION_KEY',
        'SECRET_KEY_BASE',
        'VAULT_ENC_KEY',
        'LOGFLARE_PUBLIC_ACCESS_TOKEN',
        'LOGFLARE_PRIVATE_ACCESS_TOKEN',
        'SMTP_PASS'
    ]

    def load_env_file(self) -> Dict[str, str]:
        """Load environment variables from .env file"""
        env_vars = {}

        if not self.env_file.exists():
            print(f"❌ Error: {self.env_file} not found")
            return env_vars

        with open(self.env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()

        return env_vars

    def save_env_file(self, env_vars: Dict[str, str]):
        """Save environment variables to .env file"""
        if not self.env_file.exists():
            print(f"❌ Error: {self.env_file} not found")
            return

        # Read current content
        with open(self.env_file, 'r') as f:
            content = f.read()

        # Update secret variables
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '=' in line and not line.startswith('#'):
                key = line.split('=', 1)[0].strip()
                if key in env_vars:
                    lines[i] = f"{key}={env_vars[key]}"

        # Write back
        with open(self.env_file, 'w') as f:
            f.write('\n'.join(lines))

        print(f"✅ Updated {self.env_file} with {len(env_vars)} secrets")

    def get_github_secrets(self) -> Dict[str, str]:
        """Get all secrets from GitHub repository"""
        url = f"{self.base_url}/actions/secrets"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            print(f"❌ Error fetching GitHub secrets: {response.status_code}")
            print(f"   Response: {response.text}")
            return {}

        data = response.json()
        secrets = {}

        for secret in data.get('secrets', []):
            name = secret['name']
            # Get individual secret value
            secret_url = f"{self.base_url}/actions/secrets/{name}"
            secret_response = requests.get(secret_url, headers=self.headers)

            if secret_response.status_code == 200:
                secret_data = secret_response.json()
                # Note: GitHub API doesn't return secret values, only metadata
                # We'll need to handle this differently
                pass

        print("⚠️  Note: GitHub API doesn't expose secret values for security reasons")
        print("   Use 'pull' command to interactively retrieve secrets")
        return secrets

    def set_github_secret(self, name: str, value: str) -> bool:
        """Set a secret in GitHub repository using libsodium encryption"""
        try:
            import base64
            import nacl.secret
            import nacl.utils
            from nacl.public import SealedBox, PublicKey
        except ImportError:
            print("❌ Error: PyNaCl library is required for GitHub secret encryption")
            print("   Install with: pip install PyNaCl")
            return False

        # Get public key from GitHub
        pub_key_response = requests.get(f"{self.base_url}/actions/secrets/public-key", headers=self.headers)
        if pub_key_response.status_code != 200:
            print(f"❌ Error getting public key: {pub_key_response.status_code}")
            print(f"   Response: {pub_key_response.text}")
            return False

        pub_key_data = pub_key_response.json()
        public_key_b64 = pub_key_data['key']
        key_id = pub_key_data['key_id']

        # Decode the public key
        public_key_bytes = base64.b64decode(public_key_b64)

        # Create SealedBox for encryption
        sealed_box = SealedBox(PublicKey(public_key_bytes))

        # Encrypt the secret value
        encrypted = sealed_box.encrypt(value.encode())

        # Create the secret
        url = f"{self.base_url}/actions/secrets/{name}"
        data = {
            'encrypted_value': base64.b64encode(encrypted).decode(),
            'key_id': key_id
        }

        response = requests.put(url, headers=self.headers, json=data)

        if response.status_code in [201, 204]:
            print(f"✅ Set GitHub secret: {name}")
            return True
        else:
            print(f"❌ Failed to set GitHub secret {name}: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    def push_secrets(self):
        """Push local secrets to GitHub"""
        print("🚀 Pushing secrets to GitHub...")

        env_vars = self.load_env_file()
        secrets_to_push = {k: v for k, v in env_vars.items() if k in self.SECRET_VARS}

        if not secrets_to_push:
            print("❌ No secrets found in .env file")
            return

        print(f"📋 Found {len(secrets_to_push)} secrets to push:")
        for name in secrets_to_push.keys():
            print(f"   • {name}")

        success_count = 0
        for name, value in secrets_to_push.items():
            if self.set_github_secret(name, value):
                success_count += 1

        print(f"\n✅ Successfully pushed {success_count}/{len(secrets_to_push)} secrets to GitHub")

    def pull_secrets(self):
        """Pull secrets from GitHub (interactive)"""
        print("📥 Pulling secrets from GitHub...")
        print("⚠️  This will overwrite local secret values in .env")
        print()

        # For security, GitHub doesn't allow retrieving secret values via API
        # We'll provide instructions for manual retrieval
        print("🔐 For security reasons, GitHub doesn't allow retrieving secret values via API")
        print("   Please retrieve secrets manually from GitHub and update your .env file:")
        print()
        print("   1. Go to: https://github.com/{}/settings/secrets/actions".format(self.github_repo))
        print("   2. Copy each secret value")
        print("   3. Update your .env file with the values")
        print()
        print("   Or use the 'sync' command if you have the values available locally")

    def list_secrets(self):
        """List all secrets in local .env file"""
        print("📋 Local Environment Secrets:")

        env_vars = self.load_env_file()
        secrets_found = {k: v for k, v in env_vars.items() if k in self.SECRET_VARS}

        if not secrets_found:
            print("❌ No secrets found in .env file")
            return

        for name, value in secrets_found.items():
            # Mask the value for security
            masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"   • {name}: {masked_value}")

        print(f"\n📊 Total secrets: {len(secrets_found)}")

    def sync_secrets(self):
        """Sync secrets between local and GitHub (bidirectional)"""
        print("🔄 Syncing secrets...")
        print("⚠️  This will:")
        print("   1. Push all local secrets to GitHub")
        print("   2. Pull latest values from GitHub")
        print()

        # First push local secrets
        self.push_secrets()
        print()

        # Then pull (with instructions)
        self.pull_secrets()

def main():
    if len(sys.argv) < 2:
        print("Usage: python github-secrets-manager.py <command>")
        print("Commands:")
        print("  push   - Push local secrets to GitHub")
        print("  pull   - Pull secrets from GitHub (instructions)")
        print("  list   - List local secrets")
        print("  sync   - Sync secrets bidirectionally")
        sys.exit(1)

    command = sys.argv[1].lower()

    manager = GitHubSecretsManager()

    if command == 'push':
        manager.push_secrets()
    elif command == 'pull':
        manager.pull_secrets()
    elif command == 'list':
        manager.list_secrets()
    elif command == 'sync':
        manager.sync_secrets()
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()
