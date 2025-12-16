# Embedding Streamlit App in Wagtail

This guide explains how to embed your Streamlit app (deployed on Streamlit Community Cloud) into a Wagtail page.

## Prerequisites

- Streamlit app deployed on Streamlit Community Cloud
- Wagtail site with access to edit templates
- Basic knowledge of Wagtail page models and templates

## Step 1: Deploy to Streamlit Community Cloud

1. Push your code to GitHub (if not already done)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with your GitHub account
4. Click "New app"
5. Select your repository and branch
6. Set the main file path to `streamlit_app.py`
7. Click "Deploy"
8. Wait for deployment to complete
9. Copy your app URL (e.g., `https://your-app-name.streamlit.app`)

## Step 2: Create Wagtail Page Model (if needed)

If you don't already have a dashboard page model, create one:

```python
# models.py
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.blocks import CharBlock, URLBlock
from wagtail.admin.panels import FieldPanel

class DashboardPage(Page):
    streamlit_app_url = models.URLField(
        help_text="URL of the Streamlit app (e.g., https://your-app.streamlit.app)"
    )
    
    content_panels = Page.content_panels + [
        FieldPanel('streamlit_app_url'),
    ]
    
    class Meta:
        verbose_name = "Dashboard Page"
```

## Step 3: Create Wagtail Template

Create a template for your dashboard page (e.g., `dashboard_page.html`):

```html
{% extends "base.html" %}
{% load wagtailcore_tags %}

{% block content %}
<div class="container">
    <h1>{{ page.title }}</h1>
    
    {% if page.streamlit_app_url %}
        <div class="streamlit-embed-container" style="width: 100%; height: 800px; border: none;">
            <iframe 
                src="{{ page.streamlit_app_url }}" 
                style="width: 100%; height: 100%; border: none;"
                frameborder="0"
                allow="clipboard-read; clipboard-write"
                title="Streamlit Dashboard">
            </iframe>
        </div>
    {% else %}
        <p>Please configure the Streamlit app URL in the page settings.</p>
    {% endif %}
</div>

<style>
    .streamlit-embed-container {
        margin: 20px 0;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .streamlit-embed-container iframe {
        display: block;
    }
</style>
{% endblock %}
```

## Step 4: Alternative - Using StreamField Block

If you want more flexibility, create a StreamField block:

```python
# blocks.py
from wagtail.blocks import StructBlock, URLBlock, CharBlock
from wagtail.blocks.field_block import RichTextBlock

class StreamlitAppBlock(StructBlock):
    app_url = URLBlock(required=True, help_text="Streamlit app URL")
    height = CharBlock(
        required=False, 
        default="800px",
        help_text="Height of the iframe (e.g., 800px or 100vh)"
    )
    title = CharBlock(required=False, help_text="Optional title above the app")
    
    class Meta:
        icon = 'code'
        label = 'Streamlit App'
        template = 'blocks/streamlit_app_block.html'
```

Create the template `blocks/streamlit_app_block.html`:

```html
{% if value.title %}
    <h2>{{ value.title }}</h2>
{% endif %}

<div class="streamlit-embed-container" style="width: 100%; height: {{ value.height|default:'800px' }}; border: none;">
    <iframe 
        src="{{ value.app_url }}" 
        style="width: 100%; height: 100%; border: none;"
        frameborder="0"
        allow="clipboard-read; clipboard-write"
        title="Streamlit Dashboard">
    </iframe>
</div>
```

## Step 5: Configure Streamlit for Embedding

To ensure your Streamlit app works well when embedded:

1. **Update your Streamlit app** to handle embedding:
   ```python
   # In streamlit_app.py
   st.set_page_config(
       page_title="Your App",
       layout="wide",
       initial_sidebar_state="collapsed"  # Optional: collapse sidebar when embedded
   )
   ```

2. **Enable iframe embedding** (Streamlit Community Cloud allows this by default)

3. **Test responsiveness** - ensure your app works on different screen sizes

## Step 6: Security Considerations

1. **CSP Headers**: If your Wagtail site uses Content Security Policy, add:
   ```
   frame-src https://*.streamlit.app;
   ```

2. **X-Frame-Options**: Streamlit Community Cloud allows embedding by default, but verify if you have custom security headers

3. **Authentication**: If your Streamlit app requires authentication, consider:
   - Using Streamlit's built-in authentication
   - Passing tokens via URL parameters (less secure)
   - Using session-based authentication

## Step 7: Testing

1. Create a test page in Wagtail
2. Add the Streamlit app URL
3. Publish the page
4. Visit the page and verify the app loads correctly
5. Test on different devices and browsers
6. Use the stress tester to test the embedded page!

## Troubleshooting

### App doesn't load
- Check the Streamlit app URL is correct
- Verify the app is deployed and accessible
- Check browser console for errors
- Verify CSP headers allow iframe embedding

### App loads but looks broken
- Check iframe height is sufficient
- Verify responsive design in Streamlit app
- Check for CSS conflicts between Wagtail and Streamlit

### Performance issues
- Use the stress tester to identify bottlenecks
- Consider lazy loading the iframe
- Monitor Streamlit Community Cloud usage limits

## Example: Full Page Template

```html
{% extends "base.html" %}

{% block content %}
<div class="dashboard-page">
    <header class="dashboard-header">
        <h1>{{ page.title }}</h1>
        <p class="dashboard-description">{{ page.description }}</p>
    </header>
    
    <div class="dashboard-content">
        <iframe 
            src="{{ page.streamlit_app_url }}?embed=true" 
            style="width: 100%; height: 90vh; border: none;"
            frameborder="0"
            allow="clipboard-read; clipboard-write"
            title="{{ page.title }}">
        </iframe>
    </div>
</div>

<style>
    .dashboard-page {
        padding: 20px;
    }
    
    .dashboard-header {
        margin-bottom: 20px;
    }
    
    .dashboard-content {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
</style>
{% endblock %}
```

## Next Steps

Once your app is embedded, use the stress tester to:
1. Test the Wagtail page URL (not the Streamlit app directly)
2. Monitor response times under load
3. Identify performance bottlenecks
4. Validate the integration handles concurrent users

