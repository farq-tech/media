# Al Nafl Media Review

Static HTML page for Al Nafl District POI media review. Deploy to Vercel.

## Deploy to Vercel

### Option A: Deploy via GitHub

1. Push this folder to [farq-tech/media](https://github.com/farq-tech/media):

```bash
cd media-deploy
git init
git add .
git commit -m "Deploy Al Nafl media review"
git branch -M main
git remote add origin https://github.com/farq-tech/media.git
git push -u origin main --force
```

2. In [Vercel Dashboard](https://vercel.com/dashboard):
   - Import the `farq-tech/media` project (if not already)
   - Deploy → your site will be at `media-six-jade.vercel.app` or similar

### Option B: Deploy via Vercel CLI

```bash
cd media-deploy
npx vercel --yes
```

Add a custom domain `media-six-jade.vercel.app` in Project Settings → Domains.

## Links Note

- **Working online**: Google Maps links and POI images (lh3.googleusercontent.com)
- **Local only**: `file://` links to G:/ or C:/ paths do not work in browsers when served over HTTPS. To make them work, upload media to a CDN and replace URLs.
