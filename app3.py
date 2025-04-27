import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

# Replace with your actual Gemini API Key

# Initialize Gemini Flash model
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

# Function to check if the URL is a valid job listing URL using Gemini API
def is_valid_job_listing(url: str) -> bool:
    # Update the prompt to check for job listings based on URL content
    prompt = f"Check if this URL points to a valid job listing or career opportunity page: {url}. The URL may contain words like 'careers', 'jobs', 'hiring', 'employment', or similar job-related terms, and it may include job positions like 'developer', 'software engineer', etc. Respond with 'yes' if it's a valid job listing page and 'no' if it is not."
    
    try:
        # Use the generate method to get a response from Gemini API
        response = model.generate_content(
            prompt
        )
        result = response.result.strip().lower()
        return result == 'yes'
    except Exception as e:
        print(f"Error checking job listing validity for {url}: {e}")
        return False

# Function to get and parse the webpage for links
def fetch_links(url: str):
    try:
        # Send GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for invalid responses

        # Parse the content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all links on the page
        links = soup.find_all('a', href=True)
        return links
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching URL {url}: {e}")
        return []

# Function to check if the URL contains job-related keywords
def contains_job_keywords(url: str) -> bool:
    job_keywords = ['careers', 'jobs', 'hiring', 'employment', 'developer', 'engineer', 'software', 'position']
    return any(keyword in url.lower() for keyword in job_keywords)

# Streamlit UI elements
st.title("Job Listing URL Validator")

# Input URL from the user
url = st.text_input("Enter the URL to parse:")

if url:
    # Fetch links from the provided URL
    links = fetch_links(url)
    
    if links:
        # Display all links for troubleshooting
        st.subheader("All Links Found on the Page:")
        for link in links:
            st.write(link['href'])  # Display each link on the page

        # Use a thread pool to validate links concurrently
        valid_links = []
        with ThreadPoolExecutor() as executor:
            future_to_url = {executor.submit(is_valid_job_listing, urljoin(url, link['href'])): link for link in links}
            
            for future in as_completed(future_to_url):
                link = future_to_url[future]
                try:
                    if future.result() or contains_job_keywords(link['href']):
                        valid_links.append(link['href'])
                except Exception as e:
                    print(f"Error checking {link['href']}: {e}")

        # Display the valid job listing URLs
        if valid_links:
            st.subheader("Valid Job Listing URLs found:")
            for valid_link in valid_links:
                st.write(valid_link)
        else:
            st.write("No valid job listing URLs found.")
    else:
        st.write("No links found on this page.")
