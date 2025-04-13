// Main JavaScript for Resume Tailor application

document.addEventListener('DOMContentLoaded', function() {
    // Global variables to store state
    let uploadedResumeFilename = null;
    let parsedJobData = null;
    let tailoredResumeFilename = null;
    
    // Form references
    const resumeUploadForm = document.getElementById('resumeUploadForm');
    const jobUrlForm = document.getElementById('jobUrlForm');
    
    // Button references
    const tailorResumeBtn = document.getElementById('tailorResumeBtn');
    const downloadResumeBtn = document.getElementById('downloadResumeBtn');
    
    // Status display references
    const uploadStatus = document.getElementById('uploadStatus');
    const jobParseStatus = document.getElementById('jobParseStatus');
    const tailorStatus = document.getElementById('tailorStatus');
    
    // Content display references
    const jobRequirements = document.getElementById('jobRequirements');
    const resumePreview = document.getElementById('resumePreview');
    
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
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                uploadedResumeFilename = data.filename;
                showStatus(uploadStatus, 'Resume uploaded successfully!', 'success');
                
                // Display the parsed resume preview if available
                if (data.preview) {
                    displayUserResumePreview(data.preview);
                }
                
                checkEnableTailorButton();
            } else {
                showStatus(uploadStatus, data.error || 'Upload failed.', 'error');
            }
        })
        .catch(error => {
            showStatus(uploadStatus, 'Error: ' + error.message, 'error');
        });
    });
    
    // Handle job URL parsing
    jobUrlForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const jobUrl = document.getElementById('jobUrl').value.trim();
        
        if (!jobUrl) {
            showStatus(jobParseStatus, 'Please enter a job listing URL.', 'error');
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
                // Store the complete job data object instead of just requirements
                parsedJobData = data;
                showStatus(jobParseStatus, 'Job listing parsed successfully!', 'success');
                displayJobRequirements(data.requirements);
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
        
        showStatus(tailorStatus, 'Tailoring your resume...', 'loading');
        
        fetch('/tailor-resume', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                resumeFilename: uploadedResumeFilename,
                jobRequirements: parsedJobData
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                tailoredResumeFilename = data.filename;
                showStatus(tailorStatus, 'Resume tailored successfully!', 'success');
                displayResumePreview(data.preview);
                downloadResumeBtn.disabled = false;
            } else {
                showStatus(tailorStatus, data.error || 'Tailoring failed.', 'error');
            }
        })
        .catch(error => {
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
    
    // Helper function to display resume preview
    function displayResumePreview(preview) {
        if (!preview) {
            resumePreview.innerHTML = '<p class="text-muted">No preview available.</p>';
            return;
        }
        
        resumePreview.innerHTML = preview;
    }
    
    // Helper function to display the user's uploaded resume preview
    function displayUserResumePreview(previewHtml) {
        // Get the user resume preview container
        const userResumeParsed = document.getElementById('userResumeParsed');
        
        if (userResumeParsed) {
            // Set the preview HTML content
            userResumeParsed.innerHTML = previewHtml;
        }
        
        // Also update the resume preview section
        const resumePreview = document.getElementById('resumePreview');
        if (resumePreview) {
            resumePreview.innerHTML = previewHtml;
        }
    }
    
    // Helper function to check if tailoring should be enabled
    function checkEnableTailorButton() {
        tailorResumeBtn.disabled = !(uploadedResumeFilename && parsedJobData);
    }
});
