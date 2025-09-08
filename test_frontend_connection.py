import webbrowser
import os

# Get the absolute path of the test HTML file
test_file_path = os.path.abspath("test_frontend.html")
print(f"Opening test file: {test_file_path}")

# Open the test file in the default browser
webbrowser.open(f"file://{test_file_path}")