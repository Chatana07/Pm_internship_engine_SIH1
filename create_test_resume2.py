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
    "Name: Priya Sharma",
    "Email: priya.sharma@example.com",
    "Phone: (555) 987-6543",
    "",
    "Education:",
    "B.Sc Computer Science",
    "Delhi University",
    "2018-2021",
    "",
    "Skills:",
    "Python",
    "Java",
    "SQL",
    "HTML",
    "CSS",
    "",
    "Experience:",
    "Software Intern",
    "Tech Corp",
    "2021-2022"
]

# Add text to PDF
for line in content:
    pdf.cell(w=0, h=10, text=line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

# Save the PDF with name .pdf
pdf.output("test_resume2.pdf")

print("Test resume 2 PDF created successfully!")