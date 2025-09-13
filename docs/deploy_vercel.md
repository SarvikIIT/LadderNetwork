# 🚀 Deploy to Vercel

## Quick Deploy (One-Click)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-username/network-ladder)

## Manual Deploy

### Prerequisites
- Vercel account (free at [vercel.com](https://vercel.com))
- Git repository with your code
- Vercel CLI (optional but recommended)

### Method 1: Vercel Dashboard (Easiest)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Deploy to Vercel"
   git push origin main
   ```

2. **Import Project**
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will auto-detect it's a Python project

3. **Configure Build Settings**
   - Framework Preset: `Other`
   - Build Command: Leave empty (auto-detected)
   - Output Directory: Leave empty
   - Install Command: `pip install -r requirements.txt`

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Your app will be live at `https://your-app-name.vercel.app`

### Method 2: Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel
   ```

4. **Follow the prompts**
   - Link to existing project or create new
   - Choose your settings
   - Deploy!

### Method 3: GitHub Integration

1. **Connect GitHub**
   - Go to Vercel dashboard
   - Click "New Project"
   - Connect your GitHub account
   - Select your repository

2. **Auto-Deploy**
   - Every push to main branch auto-deploys
   - Pull requests get preview deployments

## Project Structure for Vercel

```
network-ladder/
├── api/
│   └── index.py          # Serverless API endpoint
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
├── README.md
└── static/              # Static files (if any)
```

## Configuration Files

### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

### requirements.txt
```
Flask==2.3.3
Flask-CORS==4.0.0
pandas==2.0.3
schemdraw==0.15
matplotlib==3.7.2
Werkzeug==2.3.7
```

## Environment Variables

Set these in Vercel dashboard under Settings > Environment Variables:

- `PYTHONPATH`: `.`
- `FLASK_ENV`: `production`

## Custom Domain

1. **Add Domain**
   - Go to Project Settings > Domains
   - Add your custom domain
   - Follow DNS configuration instructions

2. **SSL Certificate**
   - Automatically provided by Vercel
   - HTTPS enabled by default

## Troubleshooting

### Build Failures
- Check `requirements.txt` has all dependencies
- Ensure Python version compatibility
- Check build logs in Vercel dashboard

### Runtime Errors
- Check function logs in Vercel dashboard
- Ensure all imports are available
- Test locally first

### Performance Issues
- Vercel has cold start delays for serverless
- Consider upgrading to Pro plan for better performance
- Optimize your code for serverless execution

## Monitoring

- **Analytics**: Built-in analytics in Vercel dashboard
- **Logs**: Real-time function logs
- **Performance**: Function execution metrics

## Cost

- **Hobby Plan**: Free for personal projects
- **Pro Plan**: $20/month for commercial use
- **Enterprise**: Custom pricing

## Features

✅ **Automatic HTTPS**  
✅ **Global CDN**  
✅ **Auto-scaling**  
✅ **GitHub Integration**  
✅ **Preview Deployments**  
✅ **Custom Domains**  
✅ **Environment Variables**  
✅ **Function Logs**  

## Example URLs

After deployment, your app will be available at:
- `https://your-app-name.vercel.app` (main domain)
- `https://your-app-name-git-main.vercel.app` (Git branch)
- `https://your-custom-domain.com` (if configured)

## Next Steps

1. **Test your deployment**
2. **Set up custom domain** (optional)
3. **Configure environment variables**
4. **Set up monitoring**
5. **Share your app!**

---

**Need help?** Check the [Vercel Documentation](https://vercel.com/docs) or [Community Forum](https://github.com/vercel/vercel/discussions).
