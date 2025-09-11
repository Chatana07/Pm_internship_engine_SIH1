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
    showExtractionStatus('No file selected. You can still get recommendations without uploading a resume.', 'info');
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
    
    console.log('Extracted text from PDF:', fullText.substring(0, 500) + '...'); // Log first 500 characters
    
    // Extract information from text
    const extractedInfo = extractInfoFromText(fullText);
    
    console.log('Extracted information:', extractedInfo); // Log extracted info
    
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
  
  console.log('Starting extraction from text...');
  
  // Convert to lowercase for easier matching
  const lowerText = text.toLowerCase();
  
  // Extract name with improved pattern matching
  // Look for common name patterns and capitalized words at the beginning of the document
  const namePatterns = [
    /name[^\w\n\r]*([a-z\s\-'.]{2,50})/i,
    /candidate[^\w\n\r]*([a-z\s\-'.]{2,50})/i,
    /applicant[^\w\n\r]*([a-z\s\-'.]{2,50})/i,
    /resume[^\w\n\r]*of[^\w\n\r]*([a-z\s\-'.]{2,50})/i,
    /cv[^\w\n\r]*of[^\w\n\r]*([a-z\s\-'.]{2,50})/i,
    /(?:^|\n)([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})/,
    /^([a-z\s\-'.]{2,50})\n/i,  // First line with reasonable name length
    /\n([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\s*\n/, // Name as a separate line
    /([A-Z][a-z]+\s+[A-Z][a-z]+)/ // First and last name pattern
  ];
  
  // Try to find name using patterns
  for (const pattern of namePatterns) {
    const match = text.match(pattern);
    if (match && match[1]) {
      let name = match[1].trim();
      console.log('Found potential name match:', name);
      // Validate that it looks like a proper name (not just random text)
      if (isValidName(name)) {
        info.name = formatName(name);
        console.log('Valid name found:', info.name);
        break;
      } else {
        console.log('Name validation failed for:', name);
      }
    }
  }
  
  // If no name found with patterns, try to find it at the very beginning of the document
  if (!info.name) {
    console.log('No name found with patterns, trying alternative approach...');
    // Get first few lines of the document
    const lines = text.split('\n').slice(0, 10);
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      console.log('Checking line for name:', line);
      // Check if line contains only capitalized words with spaces (typical for names)
      if (line && line.length > 2 && line.length < 40 && isValidName(line)) {
        info.name = formatName(line);
        console.log('Name found from lines check:', info.name);
        break;
      }
      // Additional check for names that start with capital letters
      const nameMatch = line.match(/^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})/);
      if (nameMatch && nameMatch[1] && isValidName(nameMatch[1])) {
        info.name = formatName(nameMatch[1]);
        console.log('Name found from regex check:', info.name);
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
      console.log('Age found:', info.age);
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
  console.log('Skills found:', info.skills);
  
  // Extract education using a more comprehensive mapping
  // Create a hash map for education qualifications
  const educationMap = {
    // Bachelor's degrees
    'bca': 'BCA',
    'bba': 'BBA',
    'bcom': 'B.Com',
    'b.sc': 'B.Sc',
    'bachelor of science': 'B.Sc',
    'bachelor of commerce': 'B.Com',
    'bachelor of arts': 'BA',
    'ba': 'BA',
    'btech': 'B.Tech',
    'b.tech': 'B.Tech',
    'be': 'B.E',
    'b.e': 'B.E',
    'bachelor of engineering': 'B.E',
    'bachelor of technology': 'B.Tech',
    'bachelor': 'Bachelor',
    'b.pharma': 'B.Pharma',
    'bachelor of pharmacy': 'B.Pharma',
    
    // Master's degrees
    'mca': 'MCA',
    'mba': 'MBA',
    'mcom': 'M.Com',
    'm.sc': 'M.Sc',
    'master of science': 'M.Sc',
    'master of commerce': 'M.Com',
    'master of arts': 'MA',
    'ma': 'MA',
    'mtech': 'M.Tech',
    'm.tech': 'M.Tech',
    'me': 'M.E',
    'm.e': 'M.E',
    'master of engineering': 'M.E',
    'master of technology': 'M.Tech',
    'master': 'Master',
    
    // Other qualifications
    'diploma': 'Diploma',
    'iti': 'ITI',
    'class 10': 'Class 10',
    'class x': 'Class 10',
    '10th': 'Class 10',
    'class 12': 'Class 12',
    'class xii': 'Class 12',
    '12th': 'Class 12'
  };
  
  // Search for education keywords in the text
  const educationKeywords = Object.keys(educationMap);
  let highestLevelEducation = '';
  
  console.log('Searching for education keywords...');
  // Look for education patterns in the text
  for (const keyword of educationKeywords) {
    // Create a regex pattern to match the education keyword with word boundaries
    const pattern = new RegExp(`\\b${keyword.replace('.', '\\.').replace(' ', '\\s*')}\\b`, 'i');
    if (pattern.test(text)) {
      const educationValue = educationMap[keyword];
      console.log('Found education keyword:', keyword, '->', educationValue);
      // If we haven't found any education yet, use this one
      if (!highestLevelEducation) {
        highestLevelEducation = educationValue;
        console.log('Setting initial education level:', highestLevelEducation);
      } 
      // Otherwise, check if this is a higher level of education
      else {
        // Define education hierarchy
        const educationHierarchy = {
          'Class 10': 1,
          'Class 12': 2,
          'ITI': 3,
          'Diploma': 4,
          'Bachelor': 5,
          'BCA': 5,
          'BBA': 5,
          'B.Com': 5,
          'B.Sc': 5,
          'BA': 5,
          'B.E': 5,
          'B.Tech': 5,
          'B.Pharma': 5,
          'Master': 6,
          'MCA': 6,
          'MBA': 6,
          'M.Com': 6,
          'M.Sc': 6,
          'MA': 6,
          'M.E': 6,
          'M.Tech': 6
        };
        
        // If this education is higher level than what we currently have, replace it
        if ((educationHierarchy[educationValue] || 0) > (educationHierarchy[highestLevelEducation] || 0)) {
          console.log('Upgrading education level from', highestLevelEducation, 'to', educationValue);
          highestLevelEducation = educationValue;
        }
      }
    }
  }
  
  info.education = highestLevelEducation;
  console.log('Final education level:', info.education);
  
  console.log('Extraction complete. Results:', info);
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
  const nonNameWords = ['resume', 'cv', 'curriculum', 'vitae', 'contact', 'information', 'details', 'name', 'address', 'phone', 'email', 'objective', 'summary'];
  const lowerName = name.toLowerCase();
  for (const word of nonNameWords) {
    if (lowerName.includes(word)) return false;
  }
  
  // More permissive check for capitalization - just make sure it's not all lowercase
  // Many PDFs don't preserve proper capitalization
  if (name === name.toLowerCase()) {
    // This is okay, we'll fix the capitalization in formatName
    return true;
  }
  
  return true;
}

// Helper function to format a name properly
function formatName(name) {
  // Trim whitespace
  name = name.trim();
  
  // If the name is all lowercase, capitalize it properly
  if (name === name.toLowerCase()) {
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
  
  // Capitalize first letter of each word (existing logic)
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
  console.log('Populating form fields with info:', info);
  
  // Populate name field
  if (info.name) {
    const nameField = document.getElementById('name');
    if (nameField && !nameField.value) {
      nameField.value = info.name;
      console.log('Name field populated:', info.name);
    } else if (nameField) {
      console.log('Name field already has value or not found:', nameField.value);
    }
  }
  
  // Populate age field
  if (info.age) {
    const ageField = document.getElementById('age');
    if (ageField && !ageField.value) {
      ageField.value = info.age;
      console.log('Age field populated:', info.age);
    } else if (ageField) {
      console.log('Age field already has value or not found:', ageField.value);
    }
  }
  
  // Populate skills field
  if (info.skills && info.skills.length > 0) {
    const skillsField = document.getElementById('skills');
    if (skillsField) {
      const currentSkills = skillsField.value ? skillsField.value.split(',').map(s => s.trim()) : [];
      const newSkills = [...new Set([...currentSkills, ...info.skills])];
      skillsField.value = newSkills.join(', ');
      console.log('Skills field populated:', skillsField.value);
    } else {
      console.log('Skills field not found');
    }
  }
  
  // Populate education field
  if (info.education) {
    const eduField = document.getElementById('eduMin');
    if (eduField) {
      console.log('Attempting to populate education field with:', info.education);
      
      // First try to find an exact match
      const eduOptions = Array.from(eduField.options);
      console.log('Available education options:', eduOptions.map(opt => opt.text));
      
      let matchedOption = eduOptions.find(option => 
        option.text.toLowerCase() === info.education.toLowerCase()
      );
      
      // If no exact match, try partial match
      if (!matchedOption) {
        matchedOption = eduOptions.find(option => 
          option.text.toLowerCase().includes(info.education.toLowerCase())
        );
      }
      
      // If still no match, try to find the highest level of education in the options
      if (!matchedOption) {
        console.log('No direct match found, trying to find highest level match');
        // Define education hierarchy for the available options
        const optionHierarchy = {
          'class 10': 1,
          'iti': 2,
          'diploma': 3,
          'bca': 4,
          'ba': 4,
          'bba': 4,
          'b.sc': 4,
          'b.com': 4,
          'b.pharma': 4
        };
        
        // Find the highest matching education level
        let highestLevel = 0;
        let bestOption = null;
        
        for (const option of eduOptions) {
          const optionText = option.text.toLowerCase();
          const level = optionHierarchy[optionText] || 0;
          if (level > highestLevel) {
            highestLevel = level;
            bestOption = option;
          }
        }
        
        matchedOption = bestOption;
      }
      
      if (matchedOption) {
        console.log('Matched education option:', matchedOption.text);
        eduField.value = matchedOption.value;
        console.log('Education field populated with value:', matchedOption.value);
      } else {
        // If no match found, try to set to a default value if the field is empty
        console.log('No matching education option found');
        if (!eduField.value) {
          eduField.selectedIndex = 0; // Select the first option as default
          console.log('Education field set to default option');
        }
      }
    } else {
      console.log('Education field not found');
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
  
  // Check if all required fields are filled (excluding resume upload)
  const requiredFields = document.querySelectorAll("[required]");
  let allFilled = true;
  
  requiredFields.forEach(field => {
    // Skip resume upload field as it's now optional
    if (field.id === "resumeUpload") {
      return; // Skip this field
    }
    
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

// Function to get the appropriate CSS class based on similarity score
function getScoreClass(score) {
  if (score >= 0.8) {
    return 'similarity-score high';
  } else if (score >= 0.5) {
    return 'similarity-score medium';
  } else {
    return 'similarity-score low';
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
                    <span class="${getScoreClass(rec.similarity_score)}">Score: ${(rec.similarity_score * 100).toFixed(1)}%</span>
                  </div>
                  <div class="card-body">
                    <p><strong>Domain:</strong> ${rec.domain}</p>
                    <p><strong>Location:</strong> ${rec.location}</p>
                    <p><strong>Type:</strong> ${rec.type}</p>
                    <p><strong>Duration:</strong> ${rec.duration}</p>
                    <p><strong>Stipend:</strong> ${rec.stipend}</p>
                    <p><strong>Why Recommended:</strong> ${rec.reason}</p>
                  </div>
                  <!-- Translation buttons for each recommendation -->
                  <div class="translation-controls">
                    <button class="translate-btn" data-index="${index}" data-lang="en">English</button>
                    <button class="translate-btn" data-index="${index}" data-lang="hi">हिंदी</button>
                    <button class="translate-btn" data-index="${index}" data-lang="bn">বাংলা</button>
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
    
    // Add event listeners for translation buttons
    document.querySelectorAll('.translate-btn').forEach(button => {
      button.addEventListener('click', function() {
        const index = this.getAttribute('data-index');
        const lang = this.getAttribute('data-lang');
        translateRecommendation(index, lang, result.recommendations);
      });
    });
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

// Function to translate a specific recommendation
async function translateRecommendation(index, targetLang, recommendations) {
  const rec = recommendations[index];
  const card = document.querySelectorAll('.recommendation-card')[index];
  
  // Show loading state
  const translateButtons = card.querySelectorAll('.translate-btn');
  const originalButtonText = {};
  translateButtons.forEach(btn => {
    originalButtonText[btn.getAttribute('data-lang')] = btn.textContent;
    if (btn.getAttribute('data-lang') === targetLang) {
      btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    }
    btn.disabled = true;
  });
  
  try {
    // Create complete field strings to translate
    const fieldStrings = [
      `${index + 1}. ${rec.company} - ${rec.role}`, // Card header
      `Domain: ${rec.domain}`,
      `Location: ${rec.location}`,
      `Type: ${rec.type}`,
      `Duration: ${rec.duration}`,
      `Stipend: ${rec.stipend}`,
      `Why Recommended: ${rec.reason}`
    ];
    
    // Send request to translation service through the main API server (to avoid CORS issues)
    const response = await fetch('http://localhost:5000/translate_batch', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
        // Note: We don't need to set CORS headers here as the API server handles them
      },
      body: JSON.stringify({
        texts: fieldStrings,
        target_lang: targetLang
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      const translations = data.translations;
      
      // Update the card content with translations
      const cardHeader = card.querySelector('.card-header h4');
      const cardBody = card.querySelector('.card-body');
      
      // Update header (first translation)
      cardHeader.innerHTML = translations[0].translated;
      
      // Update body content
      const bodyParagraphs = cardBody.querySelectorAll('p');
      for (let i = 0; i < bodyParagraphs.length && i+1 < translations.length; i++) {
        // Replace entire paragraph content with translated string
        bodyParagraphs[i].innerHTML = translations[i+1].translated.replace(/\n/g, '<br>');
      }
      
      // Update button states to show which language is active
      translateButtons.forEach(btn => {
        btn.textContent = originalButtonText[btn.getAttribute('data-lang')];
        btn.disabled = false;
        
        if (btn.getAttribute('data-lang') === targetLang) {
          btn.style.backgroundColor = '#1976d2';
          btn.style.color = 'white';
        } else {
          btn.style.backgroundColor = '';
          btn.style.color = '';
        }
      });
    } else {
      // Handle HTTP errors
      const errorText = await response.text();
      throw new Error(`Translation service error: ${response.status} - ${errorText}`);
    }
  } catch (error) {
    console.error('Translation error:', error);
    
    // Restore button states
    translateButtons.forEach(btn => {
      btn.textContent = originalButtonText[btn.getAttribute('data-lang')];
      btn.disabled = false;
    });
    
    // Show detailed error message
    let errorMessage = 'Translation failed. Please try again.';
    if (error instanceof TypeError && error.message.includes('fetch')) {
      errorMessage = 'Could not connect to translation service. Please ensure the service is running.';
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    // Show error in a more user-friendly way
    const errorDiv = document.createElement('div');
    errorDiv.className = 'translation-error-message';
    errorDiv.innerHTML = `
      <div style="background-color: #f8d7da; color: #721c24; padding: 10px; border: 1px solid #f5c6cb; border-radius: 4px; margin: 10px 15px; font-size: 0.9rem;">
        <strong>Translation Error:</strong> ${errorMessage}
      </div>
    `;
    
    // Add error message to the card
    const cardBody = card.querySelector('.card-body');
    if (cardBody && !cardBody.querySelector('.translation-error-message')) {
      cardBody.parentNode.insertBefore(errorDiv, cardBody.nextSibling);
      
      // Remove error message after 5 seconds
      setTimeout(() => {
        if (errorDiv.parentNode) {
          errorDiv.parentNode.removeChild(errorDiv);
        }
      }, 5000);
    }
  }
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
      background-color: #ffffff;
      color: #1976d2;
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 0.9rem;
      font-weight: 600;
      border: 2px solid #1976d2;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Add a vibrant color coding based on score */
    .similarity-score.high {
      background-color: #e8f5e9;
      color: #2e7d32;
      border-color: #2e7d32;
    }
    
    .similarity-score.medium {
      background-color: #fff8e1;
      color: #f57f17;
      border-color: #f57f17;
    }
    
    .similarity-score.low {
      background-color: #ffebee;
      color: #c62828;
      border-color: #c62828;
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
    
    /* Translation controls */
    .translation-controls {
      padding: 10px 15px;
      background-color: #f9f9f9;
      border-top: 1px solid #eee;
      display: flex;
      gap: 10px;
      justify-content: flex-end;
    }
    
    .translate-btn {
      padding: 5px 10px;
      border: 1px solid #1976d2;
      background-color: white;
      color: #1976d2;
      border-radius: 3px;
      cursor: pointer;
      font-size: 0.8rem;
    }
    
    .translate-btn:hover {
      background-color: #e3f2fd;
    }
    
    .translate-btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
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
    resumeUploadDesc: "Upload your resume to automatically extract your information. (Optional)",
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
    uploadHint: "Supported format: PDF only (Optional)",
    translationNote: "After getting recommendations, you can translate internship details to Hindi or Bengali using the language buttons on each card."
  },
  hi: {
    mainTitle: "एआई-आधारित अनुशंसा इंजन",
    subtitle: "पीएम इंटर्नशिप कार्यक्रम के लिए",
    description: "अपनी प्रोफ़ाइल के अनुरूप व्यक्तिगत इंटर्नशिप मैच प्राप्त करने के लिए नीचे मानदंड भरें और आगे बढ़ें।",
    resumeUploadTitle: "रिज्यूमे अपलोड करें",
    resumeUploadDesc: "अपनी जानकारी स्वचालित रूप से निकालने के लिए अपना रिज्यूमे अपलोड करें। (वैकल्पिक)",
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
    uploadHint: "समर्थित प्रारूप: केवल पीडीएफ (वैकल्पिक)",
    translationNote: "अनुशंसाएं प्राप्त करने के बाद, आप प्रत्येक कार्ड पर भाषा बटन का उपयोग करकে इंटर्नशिप विवरण का हिंदी या बंगाली में अनुवाद कर सकते हैं।"
  },
  bn: {
    mainTitle: "এআই-ভিত্তিক সুপারিশ ইঞ্জিন",
    subtitle: "পিএম ইন্টার্নশিপ প্রোগ্রামের জন্য",
    description: "আপনার প্রোফাইলের জন্য ব্যক্তিগতভাবে মানানসই ইন্টার্নশিপ ম্যাচ পেতে নীচের মানদণ্ডগুলি পূরণ করুন এবং এগিয়ে যান।",
    resumeUploadTitle: "রেজুমে আপলোড করুন",
    resumeUploadDesc: "স্বয়ংক্রিয়ভাবে আপনার তথ্য নিষ্কাশন করতে আপনার রেজুমে আপলোড করুন। (ঐচ্ছিক)",
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
    uploadHint: "সমর্থিত বিন্যাস: শুধুমাত্র পিডিএফ (ঐচ্ছিক)",
    translationNote: "সুপারিশ পেতে পরে, আপনি প্রতিটি কার্ডের ভাষা বোতামগুলি ব্যবহার করে ইন্টার্নশিপের বিবরণগুলি হিন্দি বা বাংলায় অনুবাদ করতে পারেন।"
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
    'incomeHint', 'uploadHint', 'translationNote'
  ];
  
  // Update translation note specifically
  const translationNoteElement = document.querySelector('.translation-note p');
  if (translationNoteElement && translations[lang].translationNote) {
    translationNoteElement.innerHTML = `<i class="fas fa-language"></i> ${translations[lang].translationNote}`;
  }
  
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
    const response = await fetch('http://localhost:5000/translate_batch', {
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
