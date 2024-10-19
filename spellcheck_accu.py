import openai
import os
import csv
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv("OPENAPI_KEY")
openai.api_key = api_key

# Define a function to check if the correction is valid
def check_spelling(misspelled: str, corrected: str) -> int:
    # Construct the prompt
    prompt = f"Is '{corrected}' a valid correction for the misspelled word '{misspelled}'? Respond with 'yes' or 'no'."
    
    # print(f"\n\nConstructed prompt: {prompt}")
    
    try:
        # Call the OpenAI API
        response = openai.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=28,
            temperature=0
        )

        # Print the entire response for debugging
        # print(f"Full response: {response}")
        
        # Check if response contains choices and if the text is present
        if not response.choices:
            print("No choices returned in the response.")
            return 0  # Default to invalid if no choices are returned

        # Extract and print the actual text content from GPT response
        answer = response.choices[0].text.strip().lower()
        # print(f"GPT response text: '{response['choices'][0]['text'].strip()}'")
              
        # Return 1 if valid correction, 0 if invalid
        if answer.lower().startswith('yes'):
            # print("Correction is valid.")
            return 1
        else:
            # print("Correction is invalid.")
            return 0
    except Exception as e:
        print(f"Error occurred: {e}")
        return 0  # Default to invalid if error occurs


# Process the CSV file to validate spelling corrections
def process_spellchecker_results(csv_file: str):
    # Read the CSV into a DataFrame (assuming two columns: 'misspelled', 'corrected')
    df = pd.read_csv(csv_file)

    # Create an empty list to store the validation results
    validation_results = []

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        misspelled_word = row['original']
        corrected_word = row['returned']

        # Check if the correction is valid
        is_valid = check_spelling(misspelled_word, corrected_word)

        # Append the result to the list
        validation_results.append(is_valid)

    # Add the results to the DataFrame as a new column 'is_valid'
    df['is_valid'] = validation_results

    # Count the number of valid entries (is_valid == 1)
    valid_entries = df['is_valid'].sum()
    total_entries = len(df)
    match_rate = valid_entries*100/total_entries
    print(f"\n\nMatch rate = {match_rate}")

    # Save the updated DataFrame to a new CSV file
    df.to_csv(csv_file.split('.')[0] + '_response.csv', index=False)

# Call the function with your CSV file
process_spellchecker_results('spellcheck_testdata.csv')
process_spellchecker_results('spellcheck_testdata_v3.csv')
