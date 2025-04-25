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
        
        const fileExt = file.name.split('.').pop().toLowerCase();
        if (fileExt !== 'docx' && fileExt !== 'pdf') {
            showStatus(uploadStatus, 'Only DOCX and PDF files are supported.', 'error');
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
        console.log("Displaying user resume preview...");
        
        const userResumeContainer = document.getElementById('userResumeParsed');
        if (!userResumeContainer) {
            console.error("User resume container not found");
            return;
        }
        
        // Clear any previous content
        userResumeContainer.innerHTML = '';
        
        // Add section header
        const sectionHeader = document.createElement('h6');
        sectionHeader.className = 'text-primary mb-3';
        sectionHeader.textContent = 'User Resume Parsed (LLM)';
        userResumeContainer.appendChild(sectionHeader);
        
        // Create content container with proper class
        const contentContainer = document.createElement('div');
        contentContainer.className = 'user-resume-content';
        contentContainer.style.overflow = 'visible';
        contentContainer.style.maxHeight = 'none';
        contentContainer.style.border = 'none';
        
        // Add the HTML content from the server
        if (data && data.preview) {
            contentContainer.innerHTML = data.preview;
            
            // Remove any potential nested scrollable elements
            const allElements = contentContainer.querySelectorAll('*');
            allElements.forEach(element => {
                element.style.overflow = 'visible';
                element.style.maxHeight = 'none';
                if (element.tagName === 'DIV' || element.tagName === 'SECTION') {
                    element.style.height = 'auto';
                }
                element.style.border = 'none';
                element.style.boxShadow = 'none';
            });
            
            userResumeContainer.appendChild(contentContainer);
            
            // Enable the tailor button if both resume and job data are available
            checkEnableTailorButton();
        } else {
            // Handle case where no content was extracted
            const noContentMessage = document.createElement('p');
            noContentMessage.textContent = 'No content could be extracted from the resume. Please try a different file.';
            noContentMessage.className = 'text-danger';
            userResumeContainer.appendChild(noContentMessage);
        }
    }
    
    /**
     * Recursively removes scrollbar-causing properties from all elements
     * @param {HTMLElement} element - The parent element to start with
     */
    function removeNestedScrollbars(element) {
        if (!element) return;
        
        // Apply to the element itself
        element.style.overflow = 'visible';
        element.style.maxHeight = 'none';
        element.style.border = 'none';
        
        // Apply to all child elements
        Array.from(element.children).forEach(child => {
            // Apply same styles to direct children
            child.style.overflow = 'visible';
            child.style.maxHeight = 'none';
            child.style.border = 'none';
            
            // Recursively apply to grandchildren
            if (child.children.length > 0) {
                removeNestedScrollbars(child);
            }
        });
    }
    
    // Helper function to display the tailored resume preview
    function displayResumePreview(preview) {
        // Get the resume preview container
        const resumePreview = document.getElementById('resumePreview');
        
        // Clear existing content
        resumePreview.innerHTML = '';
        
        // Create heading for tailored content
        const heading = document.createElement('h3');
        heading.textContent = 'Tailored Resume Preview';
        heading.style.marginBottom = '15px';
        heading.style.color = '#4e2a8e'; // Purple color to indicate AI tailoring
        heading.style.textAlign = 'center';
        
        // Add heading to the preview
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
        
        // Create a container for the preview HTML with A4 paper styling
        const previewContainer = document.createElement('div');
        previewContainer.className = 'tailored-resume-content';
        
        // Add a "paper" effect
        previewContainer.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
        previewContainer.style.backgroundColor = 'white';
        previewContainer.style.position = 'relative';
        previewContainer.style.maxWidth = '100%'; // Ensure proper width
        
        // Add the HTML content
        previewContainer.innerHTML = preview;
        
        // Apply paper-specific styles
        const paperContainer = document.createElement('div');
        paperContainer.className = 'paper-container';
        paperContainer.style.margin = '0 auto';
        paperContainer.style.width = '95%'; // Widen the container
        paperContainer.style.maxWidth = '95%'; // Widen the container
        paperContainer.style.display = 'flex';
        paperContainer.style.justifyContent = 'center';
        
        // Add preview container to paper container
        paperContainer.appendChild(previewContainer);
        
        // Add paper container to the resume preview
        resumePreview.appendChild(paperContainer);
        
        // Remove any nested scrollable elements
        removeNestedScrollbars(previewContainer);
        
        // Add a log message to the console
        console.log("Tailored resume preview displayed successfully");
        console.log("Preview length:", preview.length);
        
        // Enable download button after preview is shown
        downloadResumeBtn.disabled = false;
        
        // Scroll to the resume preview section
        resumePreview.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Helper function to check if tailoring should be enabled
    function checkEnableTailorButton() {
        tailorResumeBtn.disabled = !(uploadedResumeFilename && parsedJobData);
    }
});

