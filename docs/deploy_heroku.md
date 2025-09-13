# 🚀 Deploy to Heroku

## Quick Deploy (One-Click)

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/your-username/network-ladder)

## Manual Deploy

### Prerequisites
- Heroku CLI installed
- Git repository

### Steps

1. **Login to Heroku**
   ```bash
   heroku login
   ```

2. **Create Heroku App**
   ```bash
   heroku create network-ladder-app
   ```

3. **Set Buildpacks**
   ```bash
   heroku buildpacks:add heroku/python
   heroku buildpacks:add --index 1 https://github.com/heroku/heroku-buildpack-apt
   ```

4. **Create Aptfile for system dependencies**
   ```bash
   echo "g++" > Aptfile
   echo "build-essential" >> Aptfile
   ```

5. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

6. **Open your app**
   ```bash
   heroku open
   ```

### Environment Variables (Optional)
```bash
heroku config:set FLASK_ENV=production
```

## Troubleshooting

- **Build fails**: Check that all C++ files are included
- **App crashes**: Check logs with `heroku logs --tail`
- **Memory issues**: Upgrade to a higher dyno type
