// Main JavaScript for Resume Tailor application

document.addEventListener('DOMContentLoaded', function() {
    // Get form and button elements
    const resumeUploadForm = document.getElementById('resumeUploadForm');
    const jobUrlForm = document.getElementById('jobUrlForm');
    const tailorResumeBtn = document.getElementById('tailorResumeBtn');
    const downloadResumeBtn = document.getElementById('downloadResumeBtn');
    
    // Get status elements
    const uploadStatus = document.getElementById('uploadStatus');
    const jobParseStatus = document.getElementById('jobParseStatus');
    const tailorStatus = document.getElementById('tailorStatus');
    
    // Get content display elements
    const userResumeParsed = document.getElementById('userResumeParsed');
    const jobRequirements = document.getElementById('jobRequirements');
    const resumePreview = document.getElementById('resumePreview');
    
    // State variables
    let uploadedResumeFilename = null;
    let parsedJobData = null;
    let tailoredResumeFilename = null;
    
    // Handle resume upload
    resumeUploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const fileInput = document.getElementById('resumeFile');
        const file = fileInput.files[0];
        
        if (!file) {
            showStatus(uploadStatus, 'Please select a file to upload.', 'error');
            return;
        }
        
        if (!file.name.endsWith('.docx')) {
            showStatus(uploadStatus, 'Only DOCX files are supported.', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('resume', file);
        
        showStatus(uploadStatus, 'Uploading resume...', 'loading');
        
        fetch('/upload-resume', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Resume upload failed');
            }
            return response.json();
        })
        .then(data => {
            showStatus(uploadStatus, 'Resume uploaded and parsed successfully!', 'success');
            console.log('Resume parsed data:', data);
            
            uploadedResumeFilename = data.filename;
            
            // Display the user's parsed resume in the userResumeParsed section
            displayUserResumePreview(data);
            
            // Enable the job URL input and parse button
            jobUrlForm.querySelector('input[name="jobUrl"]').disabled = false;
            jobUrlForm.querySelector('button[type="submit"]').disabled = false;
            
            // If we already have job requirements, enable the tailor button
            if (jobRequirements.innerHTML.trim() !== '') {
                tailorResumeBtn.disabled = false;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showStatus(uploadStatus, 'Error: ' + error.message, 'error');
        });
    });
    
    // Handle job URL parsing with AI analysis
    jobUrlForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const jobUrl = document.getElementById('jobUrl').value;
        
        if (!jobUrl) {
            showStatus(jobParseStatus, 'Please enter a job URL.', 'error');
            return;
        }
        
        showStatus(jobParseStatus, 'Analyzing job listing with AI...', 'loading');
        
        // Use the AI job analysis endpoint
        fetch('/api/analyze-job', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: jobUrl })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                parsedJobData = data;
                showStatus(jobParseStatus, 'Job listing analyzed successfully!', 'success');
                
                // Display job requirements and AI analysis
                displayJobRequirements(data);
                
                checkEnableTailorButton();
            } else {
                showStatus(jobParseStatus, data.error || 'Analysis failed.', 'error');
            }
        })
        .catch(error => {
            console.error('Error during job analysis:', error);
            showStatus(jobParseStatus, 'Error: ' + error.message, 'error');
            
            // Fallback to basic parsing if analysis fails
            console.log('Falling back to basic job parsing...');
            showStatus(jobParseStatus, 'Falling back to basic job parsing...', 'loading');
            
            fetch('/parse-job', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: jobUrl })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    parsedJobData = data;
                    showStatus(jobParseStatus, 'Job listing parsed successfully (without AI analysis).', 'success');
                    displayJobRequirements(data);
                    checkEnableTailorButton();
                } else {
                    showStatus(jobParseStatus, data.error || 'Parsing failed.', 'error');
                }
            })
            .catch(error => {
                showStatus(jobParseStatus, 'Error: ' + error.message, 'error');
            });
        });
    });
    
    // Handle resume tailoring
    tailorResumeBtn.addEventListener('click', function() {
        if (!uploadedResumeFilename || !parsedJobData) {
            showStatus(tailorStatus, 'Please upload a resume and parse a job listing first.', 'error');
            return;
        }
        
        showStatus(tailorStatus, 'Tailoring your resume... (this may take a minute)', 'loading');
        
        // Send the complete job data with AI analysis - using OpenAI specifically
        fetch('/tailor-resume', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                resumeFilename: uploadedResumeFilename,
                jobRequirements: parsedJobData,
                llmProvider: 'openai' // Explicitly use OpenAI instead of auto
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Resume tailoring failed');
            }
            return response.json();
        })
        .then(data => {
            showStatus(tailorStatus, 'Resume tailored successfully!', 'success');
            console.log('Tailored resume data:', data);
            
            // Display the tailored resume preview
            if (data.preview) {
                displayResumePreview(data.preview);
                
                // Scroll to resume preview
                document.getElementById('resumePreview').scrollIntoView({ behavior: 'smooth' });
            } else {
                throw new Error('No preview generated');
            }
            
            // Store the tailored filename for download
            tailoredResumeFilename = data.filename;
            
            // Enable the download button
            downloadResumeBtn.disabled = false;
        })
        .catch(error => {
            console.error('Error:', error);
            showStatus(tailorStatus, 'Error: ' + error.message, 'error');
        });
    });
    
    // Handle resume download
    downloadResumeBtn.addEventListener('click', function() {
        if (!tailoredResumeFilename) {
            showStatus(tailorStatus, 'No tailored resume available for download.', 'error');
            return;
        }
        
        window.location.href = '/download/' + tailoredResumeFilename;
    });
    
    // Helper function to display status messages
    function showStatus(element, message, type) {
        element.innerHTML = message;
        element.className = '';
        element.classList.add('status-' + type);
        
        if (type === 'loading') {
            const spinner = document.createElement('span');
            spinner.classList.add('spinner');
            spinner.style.marginLeft = '10px';
            element.appendChild(spinner);
        }
    }
    
    // Helper function to display job requirements and AI analysis
    function displayJobRequirements(data) {
        console.log('Displaying job requirements with data:', data);
        
        if (!data || (!data.requirements && !data.sections && !data.complete_job_text)) {
            jobRequirements.innerHTML = '<p class="text-muted">No job information found.</p>';
            return;
        }
        
        // Clear previous content
        jobRequirements.innerHTML = '';
        
        // Add job title and company if available
        if (data.job_title && data.company) {
            const titleElement = document.createElement('h3');
            titleElement.className = 'job-title mb-3';
            titleElement.innerHTML = `${data.job_title} <span class="text-muted">at ${data.company}</span>`;
            jobRequirements.appendChild(titleElement);
        }
        
        // Display AI analysis first if available
        if (data.analysis && (data.analysis.candidate_profile || data.analysis.hard_skills?.length || data.analysis.soft_skills?.length)) {
            const analysisSection = document.createElement('div');
            analysisSection.className = 'job-section mb-4 ai-analysis-section';
            
            const analysisHeading = document.createElement('h4');
            analysisHeading.className = 'job-section-title mb-2';
            analysisHeading.innerHTML = 'AI Analysis <span class="badge bg-info">AI Insights</span>';
            analysisSection.appendChild(analysisHeading);
            
            const analysisContent = document.createElement('div');
            analysisContent.className = 'job-section-content';
            
            // Add candidate profile
            if (data.analysis.candidate_profile) {
                const profileHeading = document.createElement('h5');
                profileHeading.className = 'mb-2 mt-3';
                profileHeading.textContent = 'Candidate Profile';
                analysisContent.appendChild(profileHeading);
                
                const profilePara = document.createElement('p');
                profilePara.textContent = data.analysis.candidate_profile;
                analysisContent.appendChild(profilePara);
            }
            
            // Add skills sections
            if (data.analysis.hard_skills && data.analysis.hard_skills.length > 0) {
                const hardSkillsHeading = document.createElement('h5');
                hardSkillsHeading.className = 'mb-2 mt-3';
                hardSkillsHeading.textContent = 'Required Hard Skills';
                analysisContent.appendChild(hardSkillsHeading);
                
                const skillsList = document.createElement('ul');
                skillsList.className = 'requirement-list';
                
                data.analysis.hard_skills.forEach(skill => {
                    const skillItem = document.createElement('li');
                    skillItem.className = 'requirement-item';
                    skillItem.textContent = skill;
                    skillsList.appendChild(skillItem);
                });
                
                analysisContent.appendChild(skillsList);
            }
            
            if (data.analysis.soft_skills && data.analysis.soft_skills.length > 0) {
                const softSkillsHeading = document.createElement('h5');
                softSkillsHeading.className = 'mb-2 mt-3';
                softSkillsHeading.textContent = 'Required Soft Skills';
                analysisContent.appendChild(softSkillsHeading);
                
                const skillsList = document.createElement('ul');
                skillsList.className = 'requirement-list';
                
                data.analysis.soft_skills.forEach(skill => {
                    const skillItem = document.createElement('li');
                    skillItem.className = 'requirement-item';
                    skillItem.textContent = skill;
                    skillsList.appendChild(skillItem);
                });
                
                analysisContent.appendChild(skillsList);
            }
            
            // Add ideal candidate if available
            if (data.analysis.ideal_candidate) {
                const idealHeading = document.createElement('h5');
                idealHeading.className = 'mb-2 mt-3';
                idealHeading.textContent = 'Ideal Candidate';
                analysisContent.appendChild(idealHeading);
                
                const idealPara = document.createElement('p');
                idealPara.textContent = data.analysis.ideal_candidate;
                analysisContent.appendChild(idealPara);
            }
            
            analysisSection.appendChild(analysisContent);
            jobRequirements.appendChild(analysisSection);
        }
        
        // Check if we have complete job text first (prioritize this)
        if (data.complete_job_text && data.complete_job_text.trim()) {
            const completeJobSection = document.createElement('div');
            completeJobSection.className = 'job-section mb-4';
            
            const completeJobHeading = document.createElement('h4');
            completeJobHeading.className = 'job-section-title mb-2';
            completeJobHeading.textContent = 'Complete Job Description';
            completeJobSection.appendChild(completeJobHeading);
            
            const completeJobContent = document.createElement('div');
            completeJobContent.className = 'job-section-content';
            
            // Parse the text to preserve formatting
            const paragraphs = data.complete_job_text.split('\n\n').filter(p => p.trim());
            paragraphs.forEach(paragraph => {
                // Check if this is a bullet point list
                if (paragraph.includes('\n•') || paragraph.includes('\n-') || paragraph.includes('\n*')) {
                    const listItems = paragraph.split(/\n[•\-*]/);
                    if (listItems.length > 1) {
                        // First item might be a heading
                        const heading = listItems[0].trim();
                        if (heading) {
                            const headingEl = document.createElement('p');
                            headingEl.className = 'fw-bold';
                            headingEl.textContent = heading;
                            completeJobContent.appendChild(headingEl);
                        }
                        
                        // Create list for remaining items
                        const list = document.createElement('ul');
                        list.className = 'requirement-list';
                        
                        // Skip first item if it was a heading
                        for (let i = heading ? 1 : 0; i < listItems.length; i++) {
                            const item = listItems[i].trim();
                            if (item) {
                                const listItem = document.createElement('li');
                                listItem.className = 'requirement-item';
                                listItem.textContent = item;
                                list.appendChild(listItem);
                            }
                        }
                        
                        completeJobContent.appendChild(list);
                    } else {
                        // Just a paragraph with a bullet
                        const para = document.createElement('p');
                        para.textContent = paragraph.trim();
                        completeJobContent.appendChild(para);
                    }
                } else {
                    // Regular paragraph
                    const para = document.createElement('p');
                    para.textContent = paragraph.trim();
                    completeJobContent.appendChild(para);
                }
            });
            
            completeJobSection.appendChild(completeJobContent);
            jobRequirements.appendChild(completeJobSection);
        } else {
            // If no complete job text, use the existing section-based display
            
            // Create a comprehensive view showing all relevant sections
            const sectionOrder = [
                { key: 'about_the_job', title: 'About the Job' },
                { key: 'job_description', title: 'Job Description' },
                { key: 'job_responsibilities', title: 'Job Responsibilities' },
                { key: 'required_qualifications', title: 'Required Qualifications' },
                { key: 'preferred_qualifications', title: 'Preferred Qualifications' },
                { key: 'requirements', title: 'Requirements' }, // For backward compatibility
                { key: 'skills', title: 'Skills' },
                { key: 'about_us', title: 'About the Company' },
                { key: 'about_team', title: 'About the Team' },
                { key: 'benefits', title: 'Benefits' }
            ];
            
            // Track if we've added any sections
            let addedSections = false;
            
            // Display each section if available
            sectionOrder.forEach(section => {
                let content = data[section.key];
                
                // Skip empty sections
                if (!content || (Array.isArray(content) && content.length === 0)) {
                    return;
                }
                
                // Create section heading
                const sectionHeading = document.createElement('h4');
                sectionHeading.className = 'job-section-title mt-3 mb-2';
                sectionHeading.textContent = section.title;
                jobRequirements.appendChild(sectionHeading);
                
                // Create content container
                const contentDiv = document.createElement('div');
                contentDiv.className = 'job-section-content mb-3';
                
                // Format based on content type
                if (Array.isArray(content)) {
                    // List items (like requirements or skills)
                    const list = document.createElement('ul');
                    list.className = 'requirement-list';
                    
                    content.forEach(item => {
                        const listItem = document.createElement('li');
                        listItem.className = 'requirement-item';
                        listItem.textContent = item;
                        list.appendChild(listItem);
                    });
                    
                    contentDiv.appendChild(list);
                } else {
                    // Text content with paragraphs
                    const paragraphs = content.split('\n\n').filter(p => p.trim());
                    
                    paragraphs.forEach(paragraph => {
                        const para = document.createElement('p');
                        para.textContent = paragraph.trim();
                        contentDiv.appendChild(para);
                    });
                }
                
                jobRequirements.appendChild(contentDiv);
                addedSections = true;
            });
            
            // If no sections were added but we have a sections object, display those
            if (!addedSections && data.sections && Object.keys(data.sections).length > 0) {
                // Display sections here (existing code)
                // ... (keep the existing code for displaying sections)
            }
        }
        
        // If after all attempts no content was added, show a message
        if (jobRequirements.children.length === 0) {
            jobRequirements.innerHTML = '<p class="text-muted">No detailed job information could be extracted.</p>';
        }
    }
    
    // Helper function to display the user's original resume preview
    function displayUserResumePreview(data) {
        console.log('Displaying user resume preview with data:', data);
        
        // This function should update ONLY the userResumeParsed element, not the main resumePreview
        const userResumeParsed = document.getElementById('userResumeParsed');
        userResumeParsed.innerHTML = '';
        
        // Check if we have sections data directly or if it's nested in the response
        let sections = data.sections;
        
        // If no sections found or empty, display a message
        if (!sections || Object.keys(sections).length === 0) {
            userResumeParsed.innerHTML = '<p class="text-muted">No resume content could be parsed.</p>';
            console.warn('No sections found in resume data');
            return;
        }
        
        // Add each section to the preview
        for (const section in sections) {
            if (sections[section] && sections[section].trim && sections[section].trim()) {
                const sectionTitle = document.createElement('h4');
                sectionTitle.className = 'resume-section-title';
                sectionTitle.textContent = section.replace(/_/g, ' ').toUpperCase();
                userResumeParsed.appendChild(sectionTitle);
                
                const sectionContent = document.createElement('div');
                sectionContent.className = 'resume-section-content';
                sectionContent.innerHTML = sections[section].replace(/\n/g, '<br>');
                userResumeParsed.appendChild(sectionContent);
            }
        }
        
        console.log('User resume preview displayed with sections:', Object.keys(sections));
    }
    
    // Helper function to display the tailored resume preview
    function displayResumePreview(preview) {
        console.log('Displaying tailored resume preview with HTML content length:', preview.length);
        
        const resumePreview = document.getElementById('resumePreview');
        
        // Clear current preview content
        resumePreview.innerHTML = '';
        
        // Create heading for tailored preview
        const heading = document.createElement('h3');
        heading.textContent = 'Tailored Resume Preview';
        heading.style.color = '#4a6fdc';
        heading.style.borderBottom = '2px solid #4a6fdc';
        heading.style.paddingBottom = '8px';
        heading.style.marginBottom = '15px';
        
        // Add heading and preview content
        resumePreview.appendChild(heading);
        
        // Show a debug message when preview is empty
        if (!preview || preview.trim() === '') {
            const errorMsg = document.createElement('p');
            errorMsg.className = 'text-danger';
            errorMsg.innerHTML = 'Error: Empty preview content received from server';
            resumePreview.appendChild(errorMsg);
            console.error('Empty preview content received');
            return;
        }
        
        // Create a container for the preview HTML to ensure proper styling
        const previewContainer = document.createElement('div');
        previewContainer.className = 'tailored-resume-content';
        previewContainer.innerHTML = preview;
        resumePreview.appendChild(previewContainer);
        
        // Enable download button after preview is shown
        downloadResumeBtn.disabled = false;
        
        // Scroll to the resume preview section
        resumePreview.scrollIntoView({ behavior: 'smooth' });
        
        console.log("Tailored resume preview displayed successfully");
    }
    
    // Helper function to check if tailoring should be enabled
    function checkEnableTailorButton() {
        tailorResumeBtn.disabled = !(uploadedResumeFilename && parsedJobData);
    }
});

