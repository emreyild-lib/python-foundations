# Install the required libraries:
# pip install pandas deep-translator

# ------------------------------------
# Step 1: Import necessary libraries
# ------------------------------------
import pandas as pd         # For working with datasets (tables)
import re                   # For cleaning text using regular expressions
from deep_translator import GoogleTranslator  # For translating text to English

# ------------------------------------
# Step 2: Load the dataset
# ------------------------------------
# Read the employee_reviews.csv file
# encoding='ISO-8859-1' handles special characters if UTF-8 fails
df = pd.read_csv('employee_reviews.csv', encoding='ISO-8859-1')

# ------------------------------------
# Step 3: Clean the 'pros&cons' column
# ------------------------------------
def clean_pros_cons(text):
    if pd.isna(text):                 # If the text is empty or NaN
        return 'not mentioned'        # Replace it with 'not mentioned'
    text = str(text).lower()           # Convert text to lowercase
    text = text.encode('ascii', errors='ignore').decode('ascii')  # Remove non-ASCII characters
    text = re.sub(r'[\*\+\-•]', ' ', text)  # Remove unwanted symbols like *, +, -, •
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
    return text                        # Return the cleaned text

# Apply the cleaning function to 'pros&cons' column
df['pros&cons'] = df['pros&cons'].apply(clean_pros_cons)

# ------------------------------------
# Step 4: Take only first 100 rows for testing
# ------------------------------------
sample_df = df.head(100).copy()  # Copy first 100 rows to a new dataframe

# ------------------------------------
# Step 5: Translate text to English
# ------------------------------------
def translate_to_english(text):
    try:
        if pd.isna(text) or text.strip() == '':   # If text is empty or NaN
            return 'not mentioned'
        return GoogleTranslator(source='auto', target='en').translate(text)  # Auto detect source, translate to English
    except Exception:   # If translation fails for any reason
        return text      # Keep the original text

# Apply translation function to 'pros&cons' column
sample_df['pros&cons'] = sample_df['pros&cons'].apply(translate_to_english)

# ------------------------------------
# Step 6: Save the cleaned and translated data
# ------------------------------------
sample_df.to_csv('new_employee_cleaned_data.csv', index=False)  # Save without row numbers

# ------------------------------------
# Step 7: Preview first 10 rows after processing
# ------------------------------------
print(sample_df['pros&cons'].head(10))
