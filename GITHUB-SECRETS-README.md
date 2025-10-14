# 🔐 GitHub Secrets Manager

A Python script to securely manage environment secrets between your local `.env` file and GitHub repository secrets.

## 📋 Overview

This tool helps you:
- ✅ **Push secrets** from local `.env` to GitHub repository secrets
- ✅ **Pull secrets** from GitHub to local (with manual instructions)
- ✅ **List secrets** in your local environment
- ✅ **Sync secrets** bidirectionally

## 🔒 Identified Secrets

The script automatically identifies these environment variables as secrets:

| Secret Variable | Description |
|-----------------|-------------|
| `N8N_ENCRYPTION_KEY` | N8N workflow encryption |
| `N8N_USER_MANAGEMENT_JWT_SECRET` | N8N user authentication |
| `POSTGRES_PASSWORD` | PostgreSQL database password |
| `JWT_SECRET` | Supabase JWT signing secret |
| `ANON_KEY` | Supabase anonymous access key |
| `SERVICE_ROLE_KEY` | Supabase service role key |
| `DASHBOARD_PASSWORD` | Supabase dashboard password |
| `NEO4J_AUTH` | Neo4j authentication (user:password) |
| `CLICKHOUSE_PASSWORD` | ClickHouse database password |
| `MINIO_ROOT_PASSWORD` | MinIO object storage password |
| `LANGFUSE_SALT` | Langfuse encryption salt |
| `NEXTAUTH_SECRET` | NextAuth.js session secret |
| `ENCRYPTION_KEY` | General encryption key |
| `SECRET_KEY_BASE` | Rails/Django style secret key |
| `VAULT_ENC_KEY` | HashiCorp Vault encryption key |
| `LOGFLARE_PUBLIC_ACCESS_TOKEN` | Logflare public API token |
| `LOGFLARE_PRIVATE_ACCESS_TOKEN` | Logflare private API token |
| `SMTP_PASS` | SMTP server password |

## 🚀 Quick Start

### Prerequisites
```bash
# Install required Python packages
pip install requests cryptography

# Set up GitHub token
export GITHUB_TOKEN=your_github_personal_access_token
```

### Basic Usage

```bash
# List all secrets in your .env file
python github-secrets-manager.py list

# Push all secrets to GitHub
python github-secrets-manager.py push

# Get instructions for pulling secrets
python github-secrets-manager.py pull

# Sync secrets (push + pull instructions)
python github-secrets-manager.py sync
```

## 📖 Detailed Usage

### 1. List Local Secrets
```bash
python github-secrets-manager.py list
```
Shows all secrets found in your `.env` file with masked values for security.

### 2. Push Secrets to GitHub
```bash
export GITHUB_TOKEN=your_token_here
python github-secrets-manager.py push
```
Uploads all secrets from your `.env` file to GitHub repository secrets.

### 3. Pull Secrets from GitHub
```bash
python github-secrets-manager.py pull
```
Provides instructions for manually retrieving secrets from GitHub (API doesn't allow direct retrieval for security).

### 4. Sync Secrets
```bash
python github-secrets-manager.py sync
```
Combines push and pull operations.

## 🔧 Configuration

### Environment Variables
- `GITHUB_TOKEN`: Your GitHub Personal Access Token (required)
- `GITHUB_REPOSITORY`: Repository in format `owner/repo` (defaults to `Brunwo/local-ai-packaged`)

### GitHub Token Setup
1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Generate a new token with `repo` scope
3. Set it as an environment variable:
   ```bash
   export GITHUB_TOKEN=your_token_here
   ```

## 🛡️ Security Features

### 1. **Encrypted Transmission**
- Secrets are encrypted using GitHub's public key before transmission
- Uses industry-standard cryptography (RSA-OAEP with SHA-256)

### 2. **Masked Display**
- Secret values are never displayed in full
- Only first 8 and last 4 characters shown in listings

### 3. **Selective Sync**
- Only identified secret variables are synced
- Configuration parameters stay in `.env` file

### 4. **GitHub Security**
- Leverages GitHub's built-in secret encryption
- Secrets are stored encrypted in GitHub's database
- Access controlled by repository permissions

## 📋 Workflow Integration

### GitHub Actions Usage
```yaml
- name: Sync Secrets
  run: |
    export GITHUB_TOKEN=${{ secrets.GITHUB_TOKEN }}
    python github-secrets-manager.py push
```

### Local Development
```bash
# After pulling latest code
python github-secrets-manager.py pull
# Follow instructions to update .env with latest secrets
```

## 🔍 Troubleshooting

### Common Issues

#### 1. "cryptography library is required"
```bash
pip install cryptography
```

#### 2. "GITHUB_TOKEN environment variable is required"
```bash
export GITHUB_TOKEN=your_github_token
```

#### 3. "Error getting public key"
- Check your GitHub token has `repo` scope
- Verify repository exists and you have access
- Check network connectivity

#### 4. "Failed to set GitHub secret"
- Ensure you have write access to the repository
- Check GitHub API rate limits
- Verify token hasn't expired

### Debug Mode
```bash
# Enable verbose output
export DEBUG=1
python github-secrets-manager.py push
```

## 📊 API Rate Limits

GitHub API has rate limits:
- **Authenticated requests**: 5,000 per hour
- **Secret operations**: Count toward your hourly limit
- **Public key requests**: Minimal impact

## 🔄 Best Practices

### 1. **Regular Sync**
```bash
# Weekly sync to keep secrets updated
python github-secrets-manager.py sync
```

### 2. **Backup Secrets**
```bash
# Before major changes
cp .env .env.backup
```

### 3. **Team Coordination**
- Communicate when secrets are updated
- Use consistent naming conventions
- Document secret purposes

### 4. **Security Reviews**
- Regularly audit secret access
- Rotate tokens periodically
- Monitor for unauthorized access

## 📝 Examples

### Complete Workflow
```bash
# 1. Set up token
export GITHUB_TOKEN=ghp_1234567890abcdef

# 2. Check what secrets you have
python github-secrets-manager.py list

# 3. Push to GitHub
python github-secrets-manager.py push

# 4. On another machine, pull secrets
python github-secrets-manager.py pull
```

### CI/CD Integration
```yaml
name: Sync Secrets
on: workflow_dispatch

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install requests cryptography
      - name: Sync secrets
        run: python github-secrets-manager.py push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 🤝 Contributing

When adding new secret variables:
1. Add them to the `SECRET_VARS` list in the script
2. Update this documentation
3. Test the changes locally
4. Ensure proper masking in output

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Verify your GitHub token permissions
3. Ensure network connectivity to GitHub API
4. Check GitHub status page for outages

---

**🎉 Keep your secrets secure and synchronized!** 🔐
