@echo off
git clone -b clean-refactor-data-flow https://github.com/nanaoosaki/manus_resume_site.git temp_repo
xcopy /E /H /Y temp_repo\* .
rd /S /Q temp_repo
echo Repository files have been cloned directly into the current directory. 