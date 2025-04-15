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
    
    // Handle job URL parsing
    jobUrlForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const jobUrl = document.getElementById('jobUrl').value;
        
        if (!jobUrl) {
            showStatus(jobParseStatus, 'Please enter a job URL.', 'error');
            return;
        }
        
        showStatus(jobParseStatus, 'Parsing job listing...', 'loading');
        
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
                showStatus(jobParseStatus, 'Job listing parsed successfully!', 'success');
                
                // Display job requirements if available
                if (data.requirements) {
                    displayJobRequirements(data.requirements);
                }
                
                checkEnableTailorButton();
            } else {
                showStatus(jobParseStatus, data.error || 'Parsing failed.', 'error');
            }
        })
        .catch(error => {
            showStatus(jobParseStatus, 'Error: ' + error.message, 'error');
        });
    });
    
    // Handle resume tailoring
    tailorResumeBtn.addEventListener('click', function() {
        if (!uploadedResumeFilename || !parsedJobData) {
            showStatus(tailorStatus, 'Please upload a resume and parse a job listing first.', 'error');
            return;
        }
        
        showStatus(tailorStatus, 'Tailoring your resume... (this may take a minute)', 'loading');
        
        // Get job requirements from the displayed content
        const requirementsText = Array.from(jobRequirements.querySelectorAll('.requirement-item'))
            .map(item => item.textContent)
            .join('\n');
        
        // Send the tailoring request
        fetch('/tailor-resume', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                resumeFilename: uploadedResumeFilename,
                jobRequirements: requirementsText
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
    
    // Helper function to display job requirements
    function displayJobRequirements(requirements) {
        if (!requirements || requirements.length === 0) {
            jobRequirements.innerHTML = '<p class="text-muted">No requirements found.</p>';
            return;
        }
        
        let html = '<ul class="list-unstyled">';
        requirements.forEach(req => {
            html += `<li class="requirement-item">${req}</li>`;
        });
        html += '</ul>';
        
        jobRequirements.innerHTML = html;
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

