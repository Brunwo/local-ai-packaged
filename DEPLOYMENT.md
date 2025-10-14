# 🚀 GitHub Actions Deployment Guide

This guide explains how to set up automated deployment from your GitHub repository to your production server using GitHub Actions.

## 📋 Prerequisites

- GitHub repository with your code
- Server with Docker and Docker Compose installed
- SSH access to your server
- Domain configured (st3p.org in this case)

## 🔧 Server Setup (Already Completed)

The following has been set up on your server:

### 1. Deployment User
- **User**: `deploy`
- **Home**: `/home/deploy`
- **Permissions**: Sudo access for Docker commands

### 2. SSH Keys Generated
- **Public Key**: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINBmjgp254xNu2G2SjhYVS1Uc0HpLHHZ/TshTJ4Ixijs deploy@st3p.org`
- **Location**: `/home/deploy/.ssh/id_ed25519`

### 3. Directory Structure
```
/home/deploy/
├── app/           # Deployment directory
├── backups/       # Automatic backups
└── .ssh/          # SSH keys
```

## 🔐 GitHub Repository Setup

### Step 1: Add Deploy Key to GitHub

1. Go to your GitHub repository
2. Navigate to **Settings** → **Deploy keys**
3. Click **Add deploy key**
4. **Title**: `Production Server`
5. **Key**: Paste the public key from above
6. ✅ **Allow write access** (uncheck this for security if you don't need it)
7. Click **Add key**

### Step 2: Add Repository Secrets

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add the following secrets:

#### Required Secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `DEPLOY_SSH_PRIVATE_KEY` | Private SSH key content | The private key for deployment |
| `SERVER_HOST` | Your server IP or domain | Server hostname/IP |

#### How to get the private key:
```bash
# On your server, as root or bruno user:
sudo cat /home/deploy/.ssh/id_ed25519
```

Copy the entire output (including `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----`)

## 📁 Files Created

### 1. GitHub Actions Workflow (`.github/workflows/deploy.yml`)
- Triggers on push to `main` or `master` branch
- Manual trigger available via GitHub UI
- Handles file transfer, deployment, and verification

### 2. Deployment Script (`deploy.sh`)
- Automated deployment with error handling
- Service health checks
- Backup creation
- Colored logging output

## 🚀 Deployment Process

### Automatic Deployment
1. **Push to main branch** → GitHub Actions triggers automatically
2. **Files sync** to server via rsync
3. **Services restart** with new configuration
4. **Health checks** verify everything works
5. **Backup created** automatically

### Manual Deployment
1. Go to **Actions** tab in GitHub
2. Select **🚀 Deploy to Production** workflow
3. Click **Run workflow**
4. Select branch and run

## 🔍 Monitoring Deployment

### Check Deployment Status
```bash
# On your server:
sudo -u deploy tail -f /home/deploy/app/deploy.log
```

### View Service Status
```bash
# On your server:
cd /home/deploy/app
sudo docker-compose ps
sudo docker-compose logs
```

### Check Web Accessibility
```bash
# Test HTTP
curl -I http://localhost:80

# Test HTTPS
curl -I https://localhost:443
```

## 🛡️ Security Features

### 1. **Isolated Deployment User**
- Separate `deploy` user with limited permissions
- No shell access, only SSH key authentication
- Sudo access restricted to Docker commands only

### 2. **File Exclusions**
- `.env` files handled securely
- `node_modules` excluded from transfer
- `.git` directory not transferred

### 3. **Automatic Backups**
- Environment files backed up before deployment
- Timestamped backup directories
- Easy rollback capability

### 4. **Health Verification**
- Service status checks after deployment
- Web accessibility tests
- Automatic failure detection

## 🔧 Troubleshooting

### Deployment Fails
```bash
# Check GitHub Actions logs
# Check server logs:
sudo -u deploy tail -f /home/deploy/app/deploy.log

# Check Docker logs:
cd /home/deploy/app
sudo docker-compose logs
```

### SSH Connection Issues
```bash
# Test SSH connection:
ssh -i /path/to/private/key deploy@your-server-ip

# Check SSH service:
sudo systemctl status ssh
```

### Service Won't Start
```bash
# Check Docker status:
sudo systemctl status docker

# Check disk space:
df -h

# Check Docker resources:
sudo docker system df
```

## 📊 Deployment Logs

All deployments are logged with timestamps and can be found in:
- **GitHub Actions**: Repository → Actions tab
- **Server logs**: `/home/deploy/app/deploy.log`
- **Docker logs**: `sudo docker-compose logs`

## 🔄 Rollback Procedure

If deployment fails:
```bash
# On server:
cd /home/deploy/app
sudo docker-compose logs  # Check what went wrong

# Restore from backup:
cp /home/deploy/backups/LATEST_BACKUP_DATE/.env .env
sudo docker-compose up -d
```

## 📈 Performance Optimization

### 1. **Parallel Builds**
The deployment script uses `--parallel` flag for faster builds

### 2. **Resource Cleanup**
Automatic cleanup of unused Docker resources

### 3. **Incremental Updates**
Only changed files are transferred via rsync

## 🎯 Best Practices

1. **Test Locally First**: Test changes locally before pushing
2. **Use Feature Branches**: Develop on branches, merge to main when ready
3. **Monitor Logs**: Regularly check deployment logs
4. **Keep Secrets Secure**: Never commit secrets to repository
5. **Regular Backups**: The system creates automatic backups

## 📞 Support

If deployment issues occur:
1. Check GitHub Actions logs
2. Review server logs in `/home/deploy/app/`
3. Verify network connectivity
4. Check Docker service status

---

**🎉 Your automated deployment system is now ready!**

Push to `main` branch and watch your changes deploy automatically to production.
