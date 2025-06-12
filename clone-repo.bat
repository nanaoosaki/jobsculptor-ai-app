@echo off
git clone -b main https://github.com/nanaoosaki/jobsculptor-ai-app.git temp_repo
xcopy /E /H /Y temp_repo\* .
rd /S /Q temp_repo
echo Repository files have been cloned directly into the current directory. 