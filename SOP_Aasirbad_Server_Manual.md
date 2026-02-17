# Aasirbad Server SOP & Admin Manual

**Project:** Aasirbad Voice Preservation Platform  
**Server:** DigitalOcean Droplet (`165.227.51.121`)  
**Domain:** `aasirbad.works`  
**Stack:** Docker, FastAPI, Next.js, PostgreSQL, Redis, Nginx, SSL

---

## 1. Server Access

### SSH Access
- Command:
  ```bash
  ssh root@165.227.51.121
  ```
- SSH key must be present on your Mac (`~/.ssh/id_ed25519` or `~/.ssh/id_rsa`).

---

## 2. Directory Structure
- `/opt/aasirbad` — App root
- `docker-compose.yml` — Service definitions
- `.env` — Environment variables
- `frontend/` — Next.js frontend
- `backend/` — FastAPI backend
- `nginx/` — Nginx config

---

## 3. Routine Operations

### Pull Latest Code & Deploy
```bash
ssh root@165.227.51.121
cd /opt/aasirbad
git pull origin master
docker compose build
docker compose up -d
```

### Check Service Status
```bash
docker ps
docker compose ps
```

### View Logs
```bash
docker compose logs --tail 50
docker compose logs api --tail 50
docker compose logs frontend --tail 50
```

### Restart a Service
```bash
docker compose restart api
docker compose restart frontend
```

---

## 4. Database Management

### Access PostgreSQL Shell
```bash
docker compose exec -T postgres psql -U aasirbad -d aasirbad
```

### Backup Database
```bash
docker compose exec -T postgres pg_dump -U aasirbad aasirbad > /opt/aasirbad/backup.sql
```

### Restore Database
```bash
cat backup.sql | docker compose exec -T postgres psql -U aasirbad -d aasirbad
```

---

## 5. Nginx & SSL

### Test Nginx Config
```bash
nginx -t
```

### Reload Nginx
```bash
systemctl reload nginx
```

### Renew SSL Certificate
```bash
certbot renew --dry-run
```

---

## 6. User Management

### Reset User Password (as admin)
1. Login to get admin token:
    ```bash
    curl -X POST https://aasirbad.works/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"email":"YOUR_ADMIN_EMAIL","password":"YOUR_PASSWORD"}'
    ```
2. Generate reset link:
    ```bash
    curl -X POST https://aasirbad.works/api/auth/admin/reset \
      -H "Authorization: Bearer <TOKEN>" \
      -H "Content-Type: application/json" \
      -d '{"email":"user@example.com"}'
    ```
3. Send the returned link to the user.

---

## 7. Monitoring & Maintenance

### Check Resource Usage
```bash
htop         # (if installed)
free -h      # RAM usage
df -h        # Disk usage
docker stats # Container resource usage
```

### Reboot Droplet
```bash
reboot
```

---

## 8. Security
- Keep your SSH private key safe.
- Never share `.env` or database passwords.
- Update system regularly:
  ```bash
  apt update && apt upgrade -y
  ```

---

## 9. Disaster Recovery

### Take Snapshot (DigitalOcean Dashboard)
- Go to Droplets → Snapshots → Take Snapshot

### Restore from Snapshot
- Create new droplet from snapshot if needed.

---

## 10. Frontend/iOS App (Capacitor)

### Build iOS App
```bash
cd /opt/aasirbad/frontend
npx cap sync ios
npx cap open ios
# Build and run from Xcode
```

---

## 11. Quick Reference Table

| Task                     | Command/Action                                  |
|--------------------------|-------------------------------------------------|
| SSH in                   | `ssh root@165.227.51.121`                       |
| Update code & deploy     | `git pull && docker compose build && docker compose up -d` |
| View logs                | `docker compose logs --tail 50`                 |
| Restart API              | `docker compose restart api`                    |
| DB shell                 | `docker compose exec -T postgres psql -U aasirbad -d aasirbad` |
| Nginx reload             | `systemctl reload nginx`                        |
| SSL renew                | `certbot renew --dry-run`                       |
| Resource usage           | `htop`, `free -h`, `df -h`, `docker stats`      |
| Backup DB                | `docker compose exec -T postgres pg_dump -U aasirbad aasirbad > /opt/aasirbad/backup.sql` |
| Restore DB               | `cat backup.sql | docker compose exec -T postgres psql -U aasirbad -d aasirbad` |
| iOS build (Capacitor)    | `cd frontend && npx cap sync ios && npx cap open ios` |

---

**Keep this SOP/manual as your master reference for all server and app operations!**
