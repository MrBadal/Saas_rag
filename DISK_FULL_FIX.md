# 🚨 URGENT: Disk Full - Immediate Fix Required

## Problem
Your AWS server disk is full (`no space left on device`). Docker cannot build new images.

## ⚡ Quick Fix (Run These Commands)

SSH into your server and run these commands immediately:

```bash
# 1. SSH to your server
ssh -i your-key.pem ubuntu@13.233.168.67

# 2. Run the emergency cleanup script
chmod +x cleanup-docker.sh
./cleanup-docker.sh
```

**If that doesn't free enough space, run this aggressive cleanup:**

```bash
# EMERGENCY CLEANUP - Will remove ALL containers and images
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker system prune -af --volumes
docker builder prune -af

# Also clean apt cache
sudo apt-get clean
sudo apt-get autoremove -y

# Check disk space
df -h
```

## 📊 Check Disk Space

```bash
# See what's using space
df -h
du -sh /var/lib/docker/*
docker system df -v
```

## 🔧 Root Causes & Solutions

### 1. **Docker Images Too Large**
**Solution**: I've optimized the Dockerfiles to:
- Clean up apt cache in same layer
- Remove pip cache after install
- Use `--no-cache-dir` flag

### 2. **Old Images Accumulating**
**Solution**: Run cleanup weekly
```bash
# Add to crontab (runs every Sunday at 2 AM)
crontab -e
# Add this line:
0 2 * * 0 /home/ubuntu/SaaS_rag/cleanup-docker.sh
```

### 3. **Build Cache Too Large**
**Solution**: Clear build cache regularly
```bash
docker builder prune -af
```

### 4. **Container Logs Filling Disk**
**Solution**: Limit log size in docker-compose

Add to `docker-compose.prod.yml` under each service:
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## 🚀 Deploy After Cleanup

Once disk is cleaned:

```bash
cd ~/SaaS_rag
git pull origin main
chmod +x deploy-with-cleanup.sh
./deploy-with-cleanup.sh
```

## 💾 Long-term Solution: Expand Disk

If you keep running out of space, expand your AWS EBS volume:

```bash
# 1. In AWS Console:
#    - Go to EC2 → Volumes
#    - Select your instance's volume
#    - Actions → Modify Volume
#    - Increase size (e.g., from 8GB to 20GB)

# 2. SSH into server and expand filesystem
sudo growpart /dev/nvme0n1 1
sudo resize2fs /dev/nvme0n1p1

# 3. Verify
df -h
```

## 🧹 Automated Cleanup Files Added

I've created these scripts for you:

1. **cleanup-docker.sh** - Aggressive cleanup (removes everything)
2. **quick-cleanup.sh** - Safe cleanup (keeps running containers)
3. **deploy-with-cleanup.sh** - Deploys with automatic cleanup

## 📁 Files Modified to Reduce Size

✅ `backend/Dockerfile` - Optimized to clean up caches
✅ `backend/embedding_service/Dockerfile` - Removed pip caches
✅ `backend/.dockerignore` - Reduces build context
✅ `docker-compose.prod.yml` - Added build hints

## ⚠️ Prevention Tips

1. **Weekly Cleanup**: Run `./cleanup-docker.sh` every week
2. **Monitor Disk**: Set up CloudWatch alarm at 80% disk usage
3. **Use ECR**: Store images in AWS ECR instead of building locally
4. **Expand Disk**: Increase EBS volume to at least 20GB

## 🆘 Still Not Working?

If disk is still full after cleanup:

```bash
# Find large files
sudo du -h / | grep -E "^\s*[0-9]+G" | head -20

# Check Docker directory
sudo du -sh /var/lib/docker/*

# Clear more space
sudo rm -rf /tmp/*
sudo rm -rf /var/tmp/*
sudo journalctl --vacuum-time=3d
```

## ✅ Checklist

- [ ] Ran cleanup-docker.sh
- [ ] Disk usage below 80%
- [ ] Rebuilt with optimized Dockerfiles
- [ ] Set up weekly cleanup cron job
- [ ] Consider expanding EBS volume

---

**Push to GitHub**: ✅ All fixes pushed  
**GitHub URL**: https://github.com/MrBadal/Saas_rag  
**Status**: Ready to deploy after cleanup
