# Updating Your App on PythonAnywhere

Follow these steps to update your PythonAnywhere deployment with the latest code changes:

## 1. SSH into PythonAnywhere

Log into your PythonAnywhere account and open a Bash console from the dashboard.

## 2. Navigate to your project directory

```bash
cd manus_resume_site
```

## 3. Pull the latest changes from GitHub

```bash
git pull origin main
```

This will fetch and apply the latest changes we just pushed, including the fix to remove the template_resume.docx dependency.

## 4. Reload the web app

After pulling the changes, you need to reload your web application for the changes to take effect:

1. Go to the "Web" tab in your PythonAnywhere dashboard
2. Click the "Reload" button for your web app

## 5. Verify the fix

After reloading, try using the application's resume tailoring feature again. The error should no longer occur because:

1. We've removed the dependency on template_resume.docx
2. The code now uses the YC-Eddie style directly to create modern, well-formatted resumes

## Troubleshooting

If you still encounter issues:

1. Check the error logs on PythonAnywhere (Web tab > Error log)
2. Verify that the git pull was successful and the changes to tailoring_handler.py were applied
3. Make sure your web app reloaded successfully

## For Future Updates

Whenever you need to update your deployed application:

1. Make and test changes locally
2. Commit and push to GitHub
3. Pull the changes on PythonAnywhere
4. Reload the web app 