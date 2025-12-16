# Deploying to Streamlit Community Cloud

This guide walks you through deploying your Wagtail Stress Tester to Streamlit Community Cloud.

## Prerequisites

- GitHub account
- Code pushed to a GitHub repository
- Python 3.8+ (for local testing)

## Step 1: Prepare Your Repository

Ensure your repository structure looks like this:

```
your-repo/
├── streamlit_app.py
├── requirements.txt
├── README.md
└── .streamlit/
    └── config.toml
```

## Step 2: Push to GitHub

If you haven't already, initialize git and push to GitHub:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Wagtail Stress Tester"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/your-repo.git

# Push to GitHub
git push -u origin main
```

## Step 3: Deploy to Streamlit Community Cloud

1. **Go to Streamlit Community Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

2. **Create New App**
   - Click "New app" button
   - Select your repository from the dropdown
   - Select the branch (usually `main` or `master`)
   - Set "Main file path" to: `streamlit_app.py`
   - Optionally set an app URL (e.g., `wagtail-stress-tester`)

3. **Deploy**
   - Click "Deploy" button
   - Wait for the deployment to complete (usually 1-2 minutes)

4. **Access Your App**
   - Your app will be available at: `https://your-app-name.streamlit.app`
   - Bookmark this URL for easy access

## Step 4: Verify Deployment

1. Open your deployed app URL
2. Test the app functionality
3. Verify all features work correctly
4. Check that dependencies are installed correctly

## Step 5: Update Your App

To update your app after making changes:

```bash
# Make your changes locally
# ...

# Commit changes
git add .
git commit -m "Update: description of changes"

# Push to GitHub
git push

# Streamlit Community Cloud will automatically redeploy
# Wait 1-2 minutes for the update to complete
```

## Configuration

### Environment Variables (Optional)

If you need to set environment variables:

1. Go to your app settings on Streamlit Community Cloud
2. Click "Secrets" in the sidebar
3. Add secrets in TOML format:

```toml
[secrets]
WAGTAIL_API_URL = "https://your-wagtail-site.com"
WAGTAIL_API_TOKEN = "your-token-here"
```

Access in your app:
```python
import streamlit as st

api_url = st.secrets.get("WAGTAIL_API_URL", "default-value")
```

### Custom Domain (Optional)

1. Go to app settings
2. Click "Custom domain"
3. Follow the instructions to set up your domain

## Troubleshooting

### Deployment Fails

**Error: "Module not found"**
- Check `requirements.txt` includes all dependencies
- Ensure all imports are available

**Error: "File not found"**
- Verify `streamlit_app.py` exists in the root directory
- Check the main file path is correct

**Error: "Timeout"**
- Check for infinite loops in your code
- Verify network requests have timeouts

### App Doesn't Load

1. Check the deployment logs in Streamlit Community Cloud
2. Look for error messages
3. Test locally first: `streamlit run streamlit_app.py`

### Performance Issues

- Streamlit Community Cloud has resource limits
- For heavy stress testing, consider:
  - Reducing concurrent workers
  - Adding delays between requests
  - Testing in smaller batches

## Best Practices

1. **Keep requirements.txt minimal**: Only include necessary packages
2. **Test locally first**: Always test before pushing
3. **Use secrets for sensitive data**: Never hardcode API keys
4. **Monitor usage**: Check Streamlit Community Cloud usage limits
5. **Version control**: Use meaningful commit messages

## Limits and Quotas

Streamlit Community Cloud has some limits:
- Free tier: Limited compute resources
- Apps may sleep after inactivity
- Rate limiting may apply for external API calls

For production use, consider:
- Streamlit Cloud for Teams (paid)
- Self-hosting on your own infrastructure

## Next Steps

After deployment:
1. Test your app thoroughly
2. Embed it in Wagtail (see `WAGTAIL_EMBEDDING.md`)
3. Use it to stress test your Wagtail integration!

## Support

- [Streamlit Community Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit Forum](https://discuss.streamlit.io/)
- [GitHub Issues](https://github.com/streamlit/streamlit/issues)

