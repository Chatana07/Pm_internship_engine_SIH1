from fpdf import FPDF
from fpdf.enums import XPos, YPos

# Create instance of FPDF class
pdf = FPDF()

# Add a page
pdf.add_page()

# Set font
pdf.set_font("Helvetica", size=12)

# Add content to PDF
content = [
    "John Doe",
    "Software Developer",
    "",
    "Contact Information:",
    "Email: john.doe@example.com",
    "Phone: (555) 123-4567",
    "",
    "Summary:",
    "Experienced software developer with expertise in JavaScript, Python, and React.",
    "",
    "Skills:",
    "JavaScript",
    "Python",
    "React",
    "Node.js",
    "HTML/CSS",
    "SQL",
    "",
    "Education:",
    "Bachelor of Science in Computer Science",
    "University of Technology",
    "2016-2020",
    "",
    "Experience:",
    "Senior Developer",
    "Tech Solutions Inc.",
    "2020-Present"
]

# Add text to PDF
for line in content:
    pdf.cell(w=0, h=10, text=line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

# Save the PDF with name .pdf
pdf.output("test_resume.pdf")

print("Test resume PDF created successfully!")