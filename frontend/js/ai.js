// Get reference to enrollment message element
const eduErrMessage = document.getElementById("eduErrMessage");

// Add PDF upload functionality
document.addEventListener('DOMContentLoaded', function() {
  const resumeUpload = document.getElementById('resumeUpload');
  const extractBtn = document.getElementById('extractBtn');
  const extractionStatus = document.getElementById('extractionStatus');
  
  // Show extract button when a file is selected
  resumeUpload.addEventListener('change', function(e) {
    if (e.target.files.length > 0) {
      extractBtn.style.display = 'inline-block';
      extractionStatus.style.display = 'none';
    } else {
      extractBtn.style.display = 'none';
      extractionStatus.style.display = 'none';
    }
  });
  
  // Handle extraction button click
  extractBtn.addEventListener('click', extractResumeInfo);
});

// Extract information from PDF resume using client-side processing only
async function extractResumeInfo() {
  const resumeUpload = document.getElementById('resumeUpload');
  const extractionStatus = document.getElementById('extractionStatus');
  
  if (!resumeUpload.files || resumeUpload.files.length === 0) {
    showExtractionStatus('Please select a PDF file first.', 'error');
    return;
  }
  
  const file = resumeUpload.files[0];
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    showExtractionStatus('Please select a PDF file.', 'error');
    return;
  }
  
  showExtractionStatus('Extracting information from your resume...', 'info');
  
  try {
    // Read PDF file
    const arrayBuffer = await file.arrayBuffer();
    
    // Load PDF document
    const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    
    // Extract text from all pages
    let fullText = '';
    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i);
      const textContent = await page.getTextContent();
      const pageText = textContent.items.map(item => item.str).join(' ');
      fullText += pageText + ' ';
    }
    
    // Extract information from text
    const extractedInfo = extractInfoFromText(fullText);
    
    // Populate form fields
    populateFormFields(extractedInfo);
    
    showExtractionStatus('Information extracted successfully! Fields have been populated.', 'success');
  } catch (error) {
    console.error('Error extracting PDF:', error);
    showExtractionStatus(`Error extracting information from PDF: ${error.message}`, 'error');
  }
}

// Show extraction status message
function showExtractionStatus(message, type) {
  const extractionStatus = document.getElementById('extractionStatus');
  extractionStatus.textContent = message;
  extractionStatus.className = 'message ' + type;
  extractionStatus.style.display = 'block';
}

// Extract information from text
function extractInfoFromText(text) {
  const info = {
    name: '',
    age: '',
    skills: [],
    education: ''
  };
  
  // Convert to lowercase for easier matching
  const lowerText = text.toLowerCase();
  
  // Extract name with improved pattern matching
  // Look for common name patterns and capitalized words at the beginning of the document
  const namePatterns = [
    /name[^\w\n\r]*([a-z\s\-'.]{2,50})/i,
    /candidate[^\w\n\r]*([a-z\s\-'.]{2,50})/i,
    /applicant[^\w\n\r]*([a-z\s\-'.]{2,50})/i,
    /^([a-z\s\-'.]{2,50})\n/i  // First line with reasonable name length
  ];
  
  // Try to find name using patterns
  for (const pattern of namePatterns) {
    const match = text.match(pattern);
    if (match && match[1]) {
      let name = match[1].trim();
      // Validate that it looks like a proper name (not just random text)
      if (isValidName(name)) {
        info.name = formatName(name);
        break;
      }
    }
  }
  
  // If no name found with patterns, try to find it at the very beginning of the document
  if (!info.name) {
    // Get first few lines of the document
    const lines = text.split('\n').slice(0, 10);
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      // Check if line contains only capitalized words with spaces (typical for names)
      if (line && line.length > 2 && line.length < 40 && isValidName(line)) {
        info.name = formatName(line);
        break;
      }
    }
  }
  
  // Extract age (look for patterns like "Age:" or numbers between 18-30)
  const ageMatch = text.match(/(?:age|years\s*old)[:\s]*(\d{2})/i);
  if (ageMatch && ageMatch[1]) {
    const age = parseInt(ageMatch[1]);
    if (age >= 18 && age <= 35) {
      info.age = age;
    }
  }
  
  // Common skill keywords and patterns
  const skillKeywords = [
    'python', 'java', 'javascript', 'html', 'css', 'sql', 'c++', 'c#', 'php', 'ruby', 'swift', 'kotlin',
    'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring', 'laravel',
    'mysql', 'postgresql', 'mongodb', 'redis', 'firebase',
    'git', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
    'machine learning', 'data science', 'artificial intelligence', 'deep learning', 'neural networks',
    'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib',
    'ui/ux', 'figma', 'adobe xd', 'sketch', 'photoshop', 'illustrator',
    'excel', 'tableau', 'power bi', 'data analysis', 'statistics',
    'communication', 'leadership', 'teamwork', 'problem solving', 'critical thinking'
  ];
  
  // Extract skills
  const foundSkills = [];
  skillKeywords.forEach(skill => {
    if (lowerText.includes(skill)) {
      // Capitalize properly
      const formattedSkill = skill.split(' ').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ');
      foundSkills.push(formattedSkill);
    }
  });
  
  // Remove duplicates
  info.skills = [...new Set(foundSkills)];
  
  // Extract education
  const educationPatterns = [
    { pattern: /\b(bachelor|b\.?\s*a\.?|b\.?\s*tech|b\.?\s*e\.?|b\.?\s*sc\.?|b\.?\s*com\.?|bca|bba)\b/i, value: 'Bachelor' },
    { pattern: /\b(master|m\.?\s*a\.?|m\.?\s*tech|m\.?\s*e\.?|m\.?\s*sc\.?|m\.?\s*com\.?|mca|mba)\b/i, value: 'Master' },
    { pattern: /\b(diploma)\b/i, value: 'Diploma' },
    { pattern: /\b(class\s*10|class\s*x)\b/i, value: 'Class 10' },
    { pattern: /\b(class\s*12|class\s*xii)\b/i, value: 'Class 12' },
    { pattern: /\b(iti)\b/i, value: 'ITI' }
  ];
  
  for (const { pattern, value } of educationPatterns) {
    if (pattern.test(text)) {
      info.education = value;
      break;
    }
  }
  
  return info;
}

// Helper function to validate if text looks like a proper name
function isValidName(name) {
  // Remove extra whitespace
  name = name.trim();
  
  // Check if it's empty or too short
  if (!name || name.length < 2) return false;
  
  // Check if it's too long
  if (name.length > 40) return false;
  
  // Check if it contains only letters, spaces, hyphens, and apostrophes
  if (!/^[a-zA-Z\s\-'.]+$/.test(name)) return false;
  
  // Check if it has at least one space (most names have first and last name)
  // But also allow single names
  const words = name.trim().split(/\s+/);
  if (words.length > 4) return false; // Too many words for a name
  
  // Check that it doesn't contain common non-name words
  const nonNameWords = ['resume', 'cv', 'curriculum', 'vitae', 'contact', 'information', 'details', 'name', 'address'];
  const lowerName = name.toLowerCase();
  for (const word of nonNameWords) {
    if (lowerName.includes(word)) return false;
  }
  
  // Check that it has reasonable capitalization pattern
  // At least the first letter should be capitalized
  if (name.charAt(0) !== name.charAt(0).toUpperCase()) return false;
  
  return true;
}

// Helper function to format a name properly
function formatName(name) {
  // Trim whitespace
  name = name.trim();
  
  // Capitalize first letter of each word
  return name.split(/\s+/).map(word => {
    // Handle hyphenated names
    if (word.includes('-')) {
      return word.split('-').map(part => 
        part.charAt(0).toUpperCase() + part.slice(1).toLowerCase()
      ).join('-');
    }
    // Handle names with apostrophes (like O'Brien)
    if (word.includes("'")) {
      const parts = word.split("'");
      return parts.map((part, index) => 
        index === 0 ? part.charAt(0).toUpperCase() + part.slice(1).toLowerCase() : part.toLowerCase()
      ).join("'");
    }
    // Regular words
    return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
  }).join(' ');
}

// Populate form fields with extracted information
function populateFormFields(info) {
  // Populate name field
  if (info.name) {
    const nameField = document.getElementById('name');
    if (!nameField.value) {
      nameField.value = info.name;
    }
  }
  
  // Populate age field
  if (info.age) {
    const ageField = document.getElementById('age');
    if (!ageField.value) {
      ageField.value = info.age;
    }
  }
  
  // Populate skills field
  if (info.skills && info.skills.length > 0) {
    const skillsField = document.getElementById('skills');
    const currentSkills = skillsField.value ? skillsField.value.split(',').map(s => s.trim()) : [];
    const newSkills = [...new Set([...currentSkills, ...info.skills])];
    skillsField.value = newSkills.join(', ');
  }
  
  // Populate education field
  if (info.education) {
    const eduField = document.getElementById('eduMin');
    const eduOptions = Array.from(eduField.options);
    const matchedOption = eduOptions.find(option => 
      option.text.toLowerCase().includes(info.education.toLowerCase())
    );
    
    if (matchedOption) {
      eduField.value = matchedOption.value;
    }
  }
}

// Handle enrollment status changes
document.querySelectorAll('input[name="edu"]').forEach(radio => {
  radio.addEventListener("change", function() {
    // Process enrollment eligibility immediately when option is selected
    processEnrollmentEligibility();
    
    // Add visual feedback for selection
    this.closest('.radio').classList.add('selected');
    document.querySelectorAll('input[name="edu"]').forEach(otherRadio => {
      if (otherRadio !== this) {
        otherRadio.closest('.radio').classList.remove('selected');
      }
    });
  });
});

// Process enrollment eligibility
function processEnrollmentEligibility() {
  const selected = document.querySelector('input[name="edu"]:checked');
  
  if (!selected) return; // No option selected yet
  
  if (selected.value === "Enrolled full-time") {
    // Show rejection message
    eduErrMessage.innerHTML = "<i class='fas fa-times-circle'></i> Sorry, you are not eligible for this internship as you are enrolled in full-time study/job.";
    eduErrMessage.classList.remove("success");
    eduErrMessage.classList.add("error");
    eduErrMessage.style.display = "block";

    // Disable further actions if not eligible
    const submitBtn = document.querySelector(".submit-btn");
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.style.backgroundColor = "#9ca3af";
      submitBtn.style.cursor = "not-allowed";
      
      // Add visual indication
      submitBtn.innerHTML = "<i class='fas fa-ban'></i> Not Eligible";
    }
    
    // Highlight the section to draw attention
    document.querySelector('.edu').classList.add('error-section');
  } else {
    // If not "Enrolled full-time" → Eligible
    eduErrMessage.innerHTML = "<i class='fas fa-check-circle'></i> You are eligible to apply for this internship.";
    eduErrMessage.classList.remove("error");
    eduErrMessage.classList.add("success");
    eduErrMessage.style.display = "block";
    
    // Re-enable submit button if it was disabled and govt job is not "yes"
    const submitBtn = document.querySelector(".submit-btn");
    const govtJobSelected = document.querySelector('input[name="govtJob"]:checked');
    
    if (submitBtn && (!govtJobSelected || govtJobSelected.value !== "yes")) {
      submitBtn.disabled = false;
      submitBtn.style.backgroundColor = "";
      submitBtn.style.cursor = "";
      
      // Restore original text
      submitBtn.innerHTML = "<i class='fas fa-robot'></i> Get AI Recommendations";
    }
    
    // Remove error highlighting
    document.querySelector('.edu').classList.remove('error-section');
  }
}



// Get references to DOM elements
const govtJobForm = document.getElementById("govtJobForm");
const govtJobMessage = document.getElementById("govtJobMessage");
const govtDetailsBox = document.getElementById("govtDetailsBox"); // This might be null if commented out in HTML
const aadhaarMessage = document.getElementById("aadhaarMessage");

// Add visual feedback for form interactions
document.querySelectorAll('input, select').forEach(element => {
  // Add focus effect
  element.addEventListener('focus', function() {
    this.closest('.field')?.classList.add('focused');
  });
  
  // Remove focus effect
  element.addEventListener('blur', function() {
    this.closest('.field')?.classList.remove('focused');
  });
});

// Show/hide government details box based on selection
document.querySelectorAll('input[name="govtJob"]').forEach(radio => {
  radio.addEventListener("change", function() {
    // Only manipulate govtDetailsBox if it exists in the DOM
    if (govtDetailsBox) {
      if (this.value === "yes") {
        govtDetailsBox.style.display = "block";
      } else {
        govtDetailsBox.style.display = "none";
      }
    }
    
    // Process eligibility immediately when option is selected
    processGovtJobEligibility();
    
    // Add visual feedback for selection
    this.closest('.radio').classList.add('selected');
    document.querySelectorAll('input[name="govtJob"]').forEach(otherRadio => {
      if (otherRadio !== this) {
        otherRadio.closest('.radio').classList.remove('selected');
      }
    });
  });
});

// Process government job eligibility
function processGovtJobEligibility() {
  const selected = document.querySelector('input[name="govtJob"]:checked');
  
  if (!selected) return; // No option selected yet
  
  if (selected.value === "yes") {
    // Show rejection message
    govtJobMessage.innerHTML = "<i class='fas fa-times-circle'></i> Sorry, you are not eligible for this internship as you or your family members or your spouse has a government job.";
    govtJobMessage.classList.remove("success");
    govtJobMessage.classList.add("error");
    govtJobMessage.style.display = "block";

    // Disable further actions if not eligible
    const submitBtn = document.querySelector(".submit-btn");
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.style.backgroundColor = "#9ca3af";
      submitBtn.style.cursor = "not-allowed";
      
      // Add visual indication
      submitBtn.innerHTML = "<i class='fas fa-ban'></i> Not Eligible";
    }
    
    // Highlight the section to draw attention
    document.querySelector('.govt-job-section').classList.add('error-section');
  } else {
    // If "No" → Eligible
    govtJobMessage.innerHTML = "<i class='fas fa-check-circle'></i> You are eligible to apply for this internship.";
    govtJobMessage.classList.remove("error");
    govtJobMessage.classList.add("success");
    govtJobMessage.style.display = "block";
    
    // Re-enable submit button if it was disabled
    const submitBtn = document.querySelector(".submit-btn");
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.style.backgroundColor = "";
      submitBtn.style.cursor = "";
      
      // Restore original text
      submitBtn.innerHTML = "<i class='fas fa-robot'></i> Get AI Recommendations";
    }
    
    // Remove error highlighting
    document.querySelector('.govt-job-section').classList.remove('error-section');
  }
}

// Handle Aadhaar linking section
document.querySelectorAll('input[name="aadhaarLink"]').forEach(radio => {
  radio.addEventListener("change", function() {
    if (this.value === "yes") {
      // Show success message for Aadhaar linking
      aadhaarMessage.innerHTML = "<i class='fas fa-check-circle'></i> Great! Your bank account is linked with Aadhaar.";
      aadhaarMessage.classList.remove("error", "warning");
      aadhaarMessage.classList.add("success");
      aadhaarMessage.style.display = "block";
    } else {
      // Show warning message for Aadhaar linking
      aadhaarMessage.innerHTML = "<i class='fas fa-exclamation-triangle'></i> Please link your bank account with Aadhaar before the internship starts for stipend disbursement.";
      aadhaarMessage.classList.remove("success", "error");
      aadhaarMessage.classList.add("warning");
      aadhaarMessage.style.display = "block";
    }
    
    // Add visual feedback for selection
    this.closest('.radio').classList.add('selected');
    document.querySelectorAll('input[name="aadhaarLink"]').forEach(otherRadio => {
      if (otherRadio !== this) {
        otherRadio.closest('.radio').classList.remove('selected');
      }
    });
  });
});

// Handle main form submission
document.querySelector("form").addEventListener("submit", function(e) {
  e.preventDefault();
  
  // Check if user is eligible (not in govt job)
  const govtJobSelected = document.querySelector('input[name="govtJob"]:checked');
  if (!govtJobSelected || (govtJobSelected.value === "yes")) {
    alert("Please complete the Government Job Status section. You must not be in a government job to be eligible.");
    return;
  }
  
  // Check if user is eligible (not enrolled full-time)
  const eduSelected = document.querySelector('input[name="edu"]:checked');
  if (!eduSelected || (eduSelected.value === "Enrolled full-time")) {
    alert("Please complete the Enrollment Status section. You must not be enrolled in full-time study/job to be eligible.");
    return;
  }
  
  // Check if all required fields are filled
  const requiredFields = document.querySelectorAll("[required]");
  let allFilled = true;
  
  requiredFields.forEach(field => {
    if (!field.value && !field.checked) {
      // Special handling for radio buttons
      if (field.type === 'radio') {
        const radioGroup = document.querySelectorAll(`input[name="${field.name}"]`);
        const isChecked = Array.from(radioGroup).some(radio => radio.checked);
        if (!isChecked) {
          allFilled = false;
        }
      } else {
        allFilled = false;
      }
    }
  });
  
  if (!allFilled) {
    alert("Please fill in all required fields.");
    return;
  }
  
  // Collect form data
  const formData = {
    name: document.getElementById("name")?.value || "",
    citizenship: document.getElementById("citizenship")?.value || "Indian",
    age: document.getElementById("age")?.value ? parseInt(document.getElementById("age").value) : 0,
    eduMin: document.getElementById("eduMin")?.value || "",
    skills: document.getElementById("skills")?.value || "",
    domain: document.getElementById("domain")?.value || "",
    location: document.getElementById("location")?.value || "",
    duration: document.getElementById("duration")?.value || "12 Months",
    edu: document.querySelector('input[name="edu"]:checked')?.value || "Not in full-time",
    income: document.getElementById("income")?.value || "Up to ₹8,00,000",
    aadhaarLink: document.querySelector('input[name="aadhaarLink"]:checked')?.value || "no",
    govtJob: document.querySelector('input[name="govtJob"]:checked')?.value || "no"
  };
  
  console.log("Form data being sent:", formData);
  
  // Send data to backend
  getAIRecommendations(formData);
});

// Function to send data to backend and get AI recommendations
async function getAIRecommendations(formData) {
  try {
    console.log("Sending request to backend with data:", formData);
    
    // Show loading state
    const submitBtn = document.querySelector(".submit-btn");
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = "<i class='fas fa-spinner fa-spin'></i> Processing...";
    submitBtn.disabled = true;
    
    // Send request to backend
    const response = await fetch('http://localhost:5000/ai_recommend', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    });
    
    console.log("Response received:", response);
    console.log("Response status:", response.status);
    console.log("Response headers:", [...response.headers.entries()]);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error("Error response body:", errorText);
      throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
    }
    
    const result = await response.json();
    console.log("Result received:", result);
    
    // Restore button state
    submitBtn.innerHTML = originalText;
    submitBtn.disabled = false;
    
    // Display results
    displayRecommendations(result);
    
  } catch (error) {
    console.error('Error getting AI recommendations:', error);
    
    // More detailed error message
    let errorMessage = "Error getting AI recommendations. Please try again.";
    if (error instanceof TypeError && error.message.includes('fetch')) {
      errorMessage = "Network error: Could not connect to the server. Please make sure the backend is running on http://localhost:5000";
    } else if (error.message) {
      errorMessage = `Error: ${error.message}`;
    }
    
    // Show error in a more user-friendly way
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `
      <div style="background-color: #f8d7da; color: #721c24; padding: 15px; border: 1px solid #f5c6cb; border-radius: 4px; margin: 10px 0;">
        <strong>Error:</strong> ${errorMessage}
      </div>
    `;
    
    // Add error message to the form
    const form = document.querySelector('form');
    form.insertBefore(errorDiv, form.firstChild);
    
    // Remove error message after 5 seconds
    setTimeout(() => {
      if (errorDiv.parentNode) {
        errorDiv.parentNode.removeChild(errorDiv);
      }
    }, 5000);
    
    // Restore button state
    const submitBtn = document.querySelector(".submit-btn");
    if (submitBtn) {
      submitBtn.innerHTML = "<i class='fas fa-robot'></i> Get AI Recommendations";
      submitBtn.disabled = false;
    }
  }
}

// Function to display recommendations
function displayRecommendations(result) {
  // Check if there are any recommendations
  if (result.total_recommendations === 0) {
    // Show message when no recommendations are found
    const noResultsHTML = `
      <div class="recommendations-modal">
        <div class="modal-content">
          <div class="modal-header">
            <h2><i class="fas fa-robot"></i> AI Recommendations</h2>
            <button class="close-btn">&times;</button>
          </div>
          <div class="modal-body">
            <div class="no-results-message">
              <h3><i class="fas fa-exclamation-circle"></i> No Internships Found</h3>
              <p>${result.message || 'No internships found matching your criteria. Please try adjusting your preferences.'}</p>
              <div class="user-profile-summary">
                <h4>Your Profile Summary</h4>
                <p><strong>Name:</strong> ${result.user_profile.name}</p>
                <p><strong>Education:</strong> ${result.user_profile.education}</p>
                <p><strong>Skills:</strong> ${result.user_profile.skills}</p>
                <p><strong>Preferred Domain:</strong> ${result.user_profile.preferred_domain}</p>
                <p><strong>Preferred Location:</strong> ${result.user_profile.preferred_location}</p>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn primary close-modal-btn">Close</button>
          </div>
        </div>
      </div>
    `;
    
    // Add modal to page
    document.body.insertAdjacentHTML('beforeend', noResultsHTML);
  } else {
    // Create a modal to display results
    const recommendationsHTML = `
      <div class="recommendations-modal">
        <div class="modal-content">
          <div class="modal-header">
            <h2><i class="fas fa-robot"></i> AI Recommendations</h2>
            <button class="close-btn">&times;</button>
          </div>
          <div class="modal-body">
            <div class="user-profile-summary">
              <h3>Your Profile Summary</h3>
              <p><strong>Name:</strong> ${result.user_profile.name}</p>
              <p><strong>Education:</strong> ${result.user_profile.education}</p>
              <p><strong>Skills:</strong> ${result.user_profile.skills}</p>
              <p><strong>Preferred Domain:</strong> ${result.user_profile.preferred_domain}</p>
              <p><strong>Preferred Location:</strong> ${result.user_profile.preferred_location}</p>
            </div>
            
            <div class="recommendations-list">
              <h3>${result.message || `Top ${result.total_recommendations} Internship Recommendation${result.total_recommendations !== 1 ? 's' : ''}`}</h3>
              ${result.recommendations.map((rec, index) => `
                <div class="recommendation-card">
                  <div class="card-header">
                    <h4>${index + 1}. ${rec.company} - ${rec.role}</h4>
                    <span class="similarity-score">Score: ${(rec.similarity_score * 100).toFixed(1)}%</span>
                  </div>
                  <div class="card-body">
                    <p><strong>Domain:</strong> ${rec.domain}</p>
                    <p><strong>Location:</strong> ${rec.location}</p>
                    <p><strong>Type:</strong> ${rec.type}</p>
                    <p><strong>Duration:</strong> ${rec.duration}</p>
                    <p><strong>Stipend:</strong> ${rec.stipend}</p>
                    <p><strong>Why Recommended:</strong> ${rec.reason}</p>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn primary close-modal-btn">Close</button>
          </div>
        </div>
      </div>
    `;
    
    // Add modal to page
    document.body.insertAdjacentHTML('beforeend', recommendationsHTML);
  }
  
  // Add event listeners for closing modal
  document.querySelector('.close-btn').addEventListener('click', closeModal);
  document.querySelector('.close-modal-btn').addEventListener('click', closeModal);
  
  // Close modal when clicking outside
  document.querySelector('.recommendations-modal').addEventListener('click', function(e) {
    if (e.target === this) {
      closeModal();
    }
  });
  
  // Show modal
  document.querySelector('.recommendations-modal').style.display = 'block';
}

// Function to close modal
function closeModal() {
  const modal = document.querySelector('.recommendations-modal');
  if (modal) {
    modal.remove();
  }
}

// Add CSS for recommendations modal
document.head.insertAdjacentHTML('beforeend', `
  <style>
    .focused {
      background-color: rgba(25, 118, 210, 0.05);
      padding: 5px;
      border-radius: 5px;
      transition: all 0.3s ease;
    }
    
    .radio.selected {
      background-color: #e3f2fd;
      border-left: 3px solid #1976d2;
      font-weight: 500;
    }
    
    .error-section {
      border: 1px solid #ffcdd2 !important;
      background-color: #ffebee !important;
    }
    
    /* Smooth transitions */
    .section, .field, .radio, .btn, .message {
      transition: all 0.3s ease;
    }
    
    /* Hover effects for better desktop experience */
    .section:hover {
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
    }
    
    /* Error message */
    .error-message {
      animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-10px); }
      to { opacity: 1; transform: translateY(0); }
    }
    
    /* Recommendations Modal */
    .recommendations-modal {
      display: none;
      position: fixed;
      z-index: 1000;
      left: 0;
      top: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, 0.7);
      overflow: auto;
    }
    
    .modal-content {
      background-color: #fff;
      margin: 2% auto;
      padding: 0;
      border-radius: 8px;
      width: 90%;
      max-width: 800px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
      max-height: 90vh;
      overflow-y: auto;
    }
    
    .modal-header {
      padding: 20px;
      background-color: #1976d2;
      color: white;
      border-top-left-radius: 8px;
      border-top-right-radius: 8px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .modal-header h2 {
      margin: 0;
      font-size: 1.5rem;
    }
    
    .close-btn {
      background: none;
      border: none;
      color: white;
      font-size: 2rem;
      cursor: pointer;
      padding: 0;
      width: 30px;
      height: 30px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .modal-body {
      padding: 20px;
      background-color: #ffffff;
      color: #333333;
    }
    
    .user-profile-summary {
      background-color: #f5f5f5;
      padding: 15px;
      border-radius: 5px;
      margin-bottom: 20px;
      color: #333333;
    }
    
    .user-profile-summary h3, .user-profile-summary h4 {
      margin-top: 0;
      color: #1976d2;
    }
    
    .recommendations-list h3 {
      color: #1976d2;
      border-bottom: 2px solid #1976d2;
      padding-bottom: 5px;
    }
    
    .recommendation-card {
      border: 1px solid #ddd;
      border-radius: 5px;
      margin-bottom: 15px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      background-color: #ffffff;
      color: #333333;
    }
    
    .card-header {
      background-color: #e3f2fd;
      padding: 15px;
      border-top-left-radius: 5px;
      border-top-right-radius: 5px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .card-header h4 {
      margin: 0;
      color: #1976d2;
    }
    
    .similarity-score {
      background-color: #1976d2;
      color: white;
      padding: 5px 10px;
      border-radius: 15px;
      font-size: 0.9rem;
    }
    
    .card-body {
      padding: 15px;
      background-color: #ffffff;
      color: #333333;
    }
    
    .card-body p {
      margin: 5px 0;
      color: #333333;
    }
    
    .modal-footer {
      padding: 20px;
      text-align: right;
      border-top: 1px solid #eee;
      background-color: #ffffff;
    }
    
    .close-modal-btn {
      background-color: #1976d2;
      color: white;
      border: none;
      padding: 10px 20px;
      border-radius: 5px;
      cursor: pointer;
      font-size: 1rem;
    }
    
    .close-modal-btn:hover {
      background-color: #1565c0;
    }
    
    /* Ensure all text in modal is visible */
    .recommendations-modal * {
      color: #333333;
    }
    
    .recommendations-modal h1, 
    .recommendations-modal h2, 
    .recommendations-modal h3, 
    .recommendations-modal h4 {
      color: #1976d2;
    }
    
    /* No results message */
    .no-results-message {
      text-align: center;
      padding: 20px;
    }
    
    .no-results-message h3 {
      color: #1976d2;
      margin-bottom: 15px;
    }
    
    .no-results-message p {
      font-size: 1.1rem;
      margin-bottom: 20px;
    }
    
    .no-results-message .user-profile-summary {
      text-align: left;
      margin-top: 20px;
    }
  </style>
`);

// Add smooth scrolling to sections
document.querySelectorAll('.subhead').forEach(subhead => {
  subhead.addEventListener('click', function() {
    const section = this.closest('.section');
    section.scrollIntoView({ behavior: 'smooth' });
  });
});

// Language translation functionality
let currentLanguage = 'en';

// Translation dictionaries for all UI elements
const translations = {
  en: {
    mainTitle: "AI-Based Recommendations Engine",
    subtitle: "For PM Internship Program",
    description: "Fill the criteria below and proceed to get personalized internship matches tailored to your profile.",
    resumeUploadTitle: "Resume Upload",
    resumeUploadDesc: "Upload your resume to automatically extract your information.",
    uploadLabel: "Upload Resume (PDF)",
    extractInfo: "Extract Information",
    personalInfoTitle: "Personal Information",
    nameLabel: "Name",
    citizenshipLabel: "Citizenship",
    ageLabel: "Age",
    educationLabel: "Education",
    preferencesTitle: "Preferences",
    skillsLabel: "Skills",
    domainLabel: "Preferred Domain",
    locationLabel: "Preferred Location",
    durationLabel: "Internship Duration",
    enrollmentTitle: "Enrollment Status",
    currentStatusLabel: "Current Status",
    notEnrolled: "Not in full-time job/study",
    enrolledFullTime: "Enrolled in full-time study/job (ineligible)",
    distanceLearning: "Distance / Online program",
    financialInfoTitle: "Financial Information",
    familyIncomeLabel: "Family Income (Max)",
    aadhaarTitle: "Bank Account & Aadhaar Linking",
    aadhaarDesc: "Please confirm if your bank account is linked with your Aadhaar for seamless stipend disbursement.",
    aadhaarYes: "Yes, my bank account is linked with Aadhaar",
    aadhaarNo: "No, my bank account is not linked with Aadhaar",
    govtJobTitle: "Government Job Status",
    govtJobDesc: "Please let us know if you, any of your family members, or your spouse have a government job.",
    govtJobYes: "Yes",
    govtJobNo: "No",
    resetBtn: "Reset Form",
    getRecommendationsBtn: "Get AI Recommendations",
    citizenshipHint: "Must be an Indian citizen.",
    ageHint: "Between 21–24 years.",
    enrollmentHint: "Distance/online programs are allowed.",
    incomeHint: "Must not exceed ₹8 lakh per annum.",
    uploadHint: "Supported format: PDF only"
  },
  hi: {
    mainTitle: "एआई-आधारित अनुशंसा इंजन",
    subtitle: "पीएम इंटर्नशिप कार्यक्रम के लिए",
    description: "अपनी प्रोफ़ाइल के अनुरूप व्यक्तिगत इंटर्नशिप मैच प्राप्त करने के लिए नीचे मानदंड भरें और आगे बढ़ें।",
    resumeUploadTitle: "रिज्यूमे अपलोड करें",
    resumeUploadDesc: "अपनी जानकारी स्वचालित रूप से निकालने के लिए अपना रिज्यूमे अपलोड करें।",
    uploadLabel: "रिज्यूमे अपलोड करें (पीडीएफ)",
    extractInfo: "जानकारी निकालें",
    personalInfoTitle: "व्यक्तिगत जानकारी",
    nameLabel: "नाम",
    citizenshipLabel: "नागरिकता",
    ageLabel: "उम्र",
    educationLabel: "शिक्षा",
    preferencesTitle: "प्राथमिकताएं",
    skillsLabel: "कौशल",
    domainLabel: "पसंदीदा डोमेन",
    locationLabel: "पसंदीदा स्थान",
    durationLabel: "इंटर्नशिप अवधि",
    enrollmentTitle: "नामांकन की स्थिति",
    currentStatusLabel: "वर्तमान स्थिति",
    notEnrolled: "पूर्णकालिक नौकरी/अध्ययन में नहीं",
    enrolledFullTime: "पूर्णकालिक अध्ययन/नौकरी में नामांकित (अयोग्य)",
    distanceLearning: "दूरस्थ / ऑनलाइन कार्यक्रम",
    financialInfoTitle: "वित्तीय जानकारी",
    familyIncomeLabel: "पारिवारिक आय (अधिकतम)",
    aadhaarTitle: "बैंक खाता और आधार लिंकिंग",
    aadhaarDesc: "कृपया पुष्टि करें कि आपका बैंक खाता आधार से जुड़ा हुआ है ताकि छात्रवृत्ति का निर्बाध वितरण हो सके।",
    aadhaarYes: "हाँ, मेरा बैंक खाता आधार से जुड़ा हुआ है",
    aadhaarNo: "नहीं, मेरा बैंक खाता आधार से जुड़ा नहीं है",
    govtJobTitle: "सरकारी नौकरी की स्थिति",
    govtJobDesc: "कृपया हमें बताएं कि क्या आपके, आपके परिवार के किसी भी सदस्य या आपके जीवनसाथी के पास सरकारी नौकरी है।",
    govtJobYes: "हाँ",
    govtJobNo: "नहीं",
    resetBtn: "फॉर्म रीसेट करें",
    getRecommendationsBtn: "एआई अनुशंसाएं प्राप्त करें",
    citizenshipHint: "भारतीय नागरिक होना आवश्यक है।",
    ageHint: "21-24 वर्ष के बीच।",
    enrollmentHint: "दूरस्थ/ऑनलाइन कार्यक्रमों की अनुमति है।",
    incomeHint: "प्रति वर्ष ₹8 लाख से अधिक नहीं होना चाहिए।",
    uploadHint: "समर्थित प्रारूप: केवल पीडीएफ"
  },
  bn: {
    mainTitle: "এআই-ভিত্তিক সুপারিশ ইঞ্জিন",
    subtitle: "পিএম ইন্টার্নশিপ প্রোগ্রামের জন্য",
    description: "আপনার প্রোফাইলের জন্য ব্যক্তিগতভাবে মানানসই ইন্টার্নশিপ ম্যাচ পেতে নীচের মানদণ্ডগুলি পূরণ করুন এবং এগিয়ে যান।",
    resumeUploadTitle: "রেজুমে আপলোড করুন",
    resumeUploadDesc: "স্বয়ংক্রিয়ভাবে আপনার তথ্য নিষ্কাশন করতে আপনার রেজুমে আপলোড করুন।",
    uploadLabel: "রেজুমে আপলোড করুন (পিডিএফ)",
    extractInfo: "তথ্য নিষ্কাশন করুন",
    personalInfoTitle: "ব্যক্তিগত তথ্য",
    nameLabel: "নাম",
    citizenshipLabel: "নাগরিকত্ব",
    ageLabel: "বয়স",
    educationLabel: "শিক্ষা",
    preferencesTitle: "পছন্দসই",
    skillsLabel: "দক্ষতা",
    domainLabel: "পছন্দসই ডোমেন",
    locationLabel: "পছন্দসই অবস্থান",
    durationLabel: "ইন্টার্নশিপ সময়কাল",
    enrollmentTitle: "ভর্তির অবস্থা",
    currentStatusLabel: "বর্তমান অবস্থা",
    notEnrolled: "পূর্ণ-সময়ের চাকরি/অধ্যয়নে নয়",
    enrolledFullTime: "পূর্ণ-সময়ের অধ্যয়ন/চাকরিতে ভর্তি (অযোগ্য)",
    distanceLearning: "দূরবর্তী / অনলাইন প্রোগ্রাম",
    financialInfoTitle: "আর্থিক তথ্য",
    familyIncomeLabel: "পারিবারিক আয় (সর্বোচ্চ)",
    aadhaarTitle: "ব্যাঙ্ক অ্যাকাউন্ট এবং আধার লিঙ্কিং",
    aadhaarDesc: "নির্বিঘ্নভাবে স্টিপেন্ড বিতরণের জন্য দয়া করে নিশ্চিত করুন যে আপনার ব্যাঙ্ক অ্যাকাউন্ট আধারের সাথে সংযুক্ত।",
    aadhaarYes: "হ্যাঁ, আমার ব্যাঙ্ক অ্যাকাউন্ট আধারের সাথে সংযুক্ত",
    aadhaarNo: "না, আমার ব্যাঙ্ক অ্যাকাউন্ট আধারের সাথে সংযুক্ত নয়",
    govtJobTitle: "সরকারি চাকরির অবস্থা",
    govtJobDesc: "দয়া করে আমাদের জানান যে আপনার, আপনার পরিবারের কোনও সদস্য বা আপনার স্পাউসের কাছে কোনও সরকারি চাকরি রয়েছে কিনা।",
    govtJobYes: "হ্যাঁ",
    govtJobNo: "না",
    resetBtn: "ফর্ম রিসেট করুন",
    getRecommendationsBtn: "এআই সুপারিশ পান",
    citizenshipHint: "ভারতীয় নাগরিক হতে হবে।",
    ageHint: "21-24 বছরের মধ্যে।",
    enrollmentHint: "দূরবর্তী/অনলাইন প্রোগ্রামগুলি অনুমোদিত।",
    incomeHint: "প্রতি বছর ₹8 লক্ষের বেশি হওয়া উচিত নয়।",
    uploadHint: "সমর্থিত বিন্যাস: শুধুমাত্র পিডিএফ"
  }
};

// Function to switch language
async function switchLanguage(lang) {
  if (lang === currentLanguage) return;
  
  currentLanguage = lang;
  
  // Update button states
  document.querySelectorAll('[id^="lang-"]').forEach(btn => {
    btn.style.backgroundColor = '';
    btn.style.color = '';
  });
  
  const activeBtn = document.getElementById(`lang-${lang}`);
  if (activeBtn) {
    activeBtn.style.backgroundColor = '#1976d2';
    activeBtn.style.color = 'white';
  }
  
  // Get all translatable elements
  const translatableElements = [
    'mainTitle', 'subtitle', 'description', 'resumeUploadTitle', 'resumeUploadDesc',
    'uploadLabel', 'extractInfo', 'personalInfoTitle', 'nameLabel', 'citizenshipLabel',
    'ageLabel', 'educationLabel', 'preferencesTitle', 'skillsLabel', 'domainLabel',
    'locationLabel', 'durationLabel', 'enrollmentTitle', 'currentStatusLabel',
    'notEnrolled', 'enrolledFullTime', 'distanceLearning', 'financialInfoTitle',
    'familyIncomeLabel', 'aadhaarTitle', 'aadhaarDesc', 'aadhaarYes', 'aadhaarNo',
    'govtJobTitle', 'govtJobDesc', 'govtJobYes', 'govtJobNo', 'resetBtn',
    'getRecommendationsBtn', 'citizenshipHint', 'ageHint', 'enrollmentHint',
    'incomeHint', 'uploadHint'
  ];
  
  // Collect texts to translate
  const textsToTranslate = [];
  translatableElements.forEach(id => {
    const element = document.getElementById(id);
    if (element) {
      textsToTranslate.push({
        id: id,
        text: element.textContent || element.innerText
      });
    }
  });
  
  // If switching to English, use direct translations
  if (lang === 'en') {
    translatableElements.forEach(id => {
      const element = document.getElementById(id);
      if (element && translations.en[id]) {
        element.textContent = translations.en[id];
      }
    });
    return;
  }
  
  // For other languages, try to use the translation service
  try {
    // Try to translate using the backend service
    const response = await fetch('http://localhost:5001/translate_batch', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        texts: textsToTranslate.map(item => item.text),
        target_lang: lang
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      // Apply translations
      data.translations.forEach((translation, index) => {
        const elementId = textsToTranslate[index].id;
        const element = document.getElementById(elementId);
        if (element) {
          element.textContent = translation.translated;
        }
      });
    } else {
      // Fallback to predefined translations
      translatableElements.forEach(id => {
        const element = document.getElementById(id);
        if (element && translations[lang][id]) {
          element.textContent = translations[lang][id];
        }
      });
    }
  } catch (error) {
    console.error('Translation error:', error);
    // Fallback to predefined translations
    translatableElements.forEach(id => {
      const element = document.getElementById(id);
      if (element && translations[lang][id]) {
        element.textContent = translations[lang][id];
      }
    });
  }
}

// Initialize language buttons
document.addEventListener('DOMContentLoaded', function() {
  // Set English as default active
  const enBtn = document.getElementById('lang-en');
  if (enBtn) {
    enBtn.style.backgroundColor = '#1976d2';
    enBtn.style.color = 'white';
  }
  
  // Add event listeners to language buttons
  document.getElementById('lang-en')?.addEventListener('click', () => switchLanguage('en'));
  document.getElementById('lang-hi')?.addEventListener('click', () => switchLanguage('hi'));
  document.getElementById('lang-bn')?.addEventListener('click', () => switchLanguage('bn'));
});
