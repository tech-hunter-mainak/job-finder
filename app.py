import streamlit as st
import pdfplumber
import google.generativeai as genai
import bs4 as bs
import requests
import json
import os

intern_carrier_distionary_india = {
    "Google": "https://careers.google.com/jobs/results/?employment_type=INTERNSHIP&location=India",
    "Microsoft": "https://careers.microsoft.com/students/us/en/search-results?keywords=intern&location=India",
    "Amazon": "https://www.amazon.jobs/en/locations/india",
    "Meta": "https://www.metacareers.com/jobs?location=India&employment_type=INTERNSHIP",
    "Apple": "https://jobs.apple.com/en-in/search?location=India&jobType=Intern",
    "IBM": "https://www.ibm.com/employment/in-en/entrylevel.html",
    "Accenture": "https://www.accenture.com/in-en/careers/jobsearch?jk=intern&location=India",
    "TCS": "https://www.tcs.com/careers/entry-level-jobs",
    "Wipro": "https://careers.wipro.com/careers/home?location=India&jobType=Intern",
    "Infosys": "https://www.infosys.com/careers/entry-level.html",
    "Cognizant": "https://careers.cognizant.com/global/en/search-results?keywords=intern&location=India",
    "HCL": "https://www.hcltech.com/careers/entry-level-jobs",
    "Capgemini": "https://www.capgemini.com/in-en/careers/job-search/?location=India&jobType=Intern",
    "Tech Mahindra": "https://careers.techmahindra.com/careers/home?location=India&jobType=Intern",
    "L&T": "https://careers.larsentoubro.com/careers/home?location=India&jobType=Intern",
    "Zensar": "https://www.zensar.com/careers/entry-level-jobs",
    "Mphasis": "https://www.mphasis.com/careers/entry-level-jobs.html",
    "Mindtree": "https://www.mindtree.com/careers/entry-level-jobs",
    "Hexaware": "https://www.hexaware.com/careers/entry-level-jobs",
    "Zebra Technologies": "https://www.zebra.com/us/en/careers.html",
    "Qualcomm": "https://www.qualcomm.com/company/careers/university-recruiting/internships",
    "NVIDIA": "https://www.nvidia.com/en-us/about-nvidia/careers/university-recruiting/internships/",
    "Intel": "https://www.intel.com/content/www/us/en/jobs/locations/india.html",
    "Cisco": "https://jobs.cisco.com/jobs/SearchJobs/?3=Intern&4=India",
    "Salesforce": "https://www.salesforce.com/company/careers/university-recruiting/internships/",

    "SAP": "https://www.sap.com/about/careers/university-recruiting/internships.html",
    "Oracle": "https://www.oracle.com/corporate/careers/students-and-grads/internships.html",
    "Adobe": "https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced/job/India/Intern--Software-Development--India--2024--2025--Internship--Full-Time--Remote_JR-100100",
    "VMware": "https://careers.vmware.com/main/jobs?location=India&jobType=Intern",
    "ServiceNow": "https://www.servicenow.com/careers/university-recruiting/internships.html",
    "Atlassian": "https://www.atlassian.com/company/careers/university-recruiting/internships",
    "Slack": "https://slack.com/careers/university-recruiting/internships",
    "Zoom": "https://zoom.us/careers/university-recruiting/internships",
    "Dropbox": "https://www.dropbox.com/jobs/university-recruiting/internships",
    "LinkedIn": "https://careers.linkedin.com/students/internships",
    
    "Twitter": "https://careers.twitter.com/en/students/internships.html",
    "Snapchat": "https://www.snap.com/en-US/jobs/university-recruiting/internships",
    "Pinterest": "https://www.pinterestcareers.com/university-recruiting/internships",
    "Reddit": "https://www.redditinc.com/careers/university-recruiting/internships",
    "Spotify": "https://www.spotifyjobs.com/university-recruiting/internships",
    "Netflix": "https://jobs.netflix.com/internships",
    "Uber": "https://www.uber.com/global/en/careers/university-recruiting/internships",
    "Lyft": "https://www.lyft.com/careers/university-recruiting/internships",
    "Airbnb": "https://www.airbnb.com/careers/university-recruiting/internships",
    "DoorDash": "https://www.doordash.com/careers/university-recruiting/internships",
    "Postmates": "https://www.postmates.com/careers/university-recruiting/internships",
    "Instacart": "https://www.instacart.com/careers/university-recruiting/internships",
    "Stripe": "https://stripe.com/jobs/university-recruiting/internships",
    "Square": "https://squareup.com/us/en/careers/university-recruiting/internships",
    "PayPal": "https://www.paypal.com/us/webapps/mpp/jobs/university-recruiting/internships",
    "eBay": "https://www.ebayinc.com/careers/university-recruiting/internships",
    "Shopify": "https://www.shopify.com/careers/university-recruiting/internships",
    "Wix": "https://www.wix.com/careers/university-recruiting/internships",
    "Squarespace": "https://www.squarespace.com/careers/university-recruiting/internships",
    
    "Weebly": "https://www.weebly.com/careers/university-recruiting/internships",
    "WordPress": "https://wordpress.com/careers/university-recruiting/internships",
    "Blogger": "https://www.blogger.com/careers/university-recruiting/internships",
    "Tumblr": "https://www.tumblr.com/careers/university-recruiting/internships",
    "Medium": "https://medium.com/careers/university-recruiting/internships",
    "Substack": "https://substack.com/careers/university-recruiting/internships"
}

full_time_carrier_distionary_india = {
    "Google": "https://careers.google.com/jobs/results/?employment_type=FULL_TIME&location=India",
    "Microsoft": "https://careers.microsoft.com/students/us/en/search-results?keywords=full-time&location=India",
    "Amazon": "https://www.amazon.jobs/en/locations/india",
    "Meta": "https://www.metacareers.com/jobs?location=India&employment_type=FULL_TIME",
    "Apple": "https://jobs.apple.com/en-in/search?location=India&jobType=Full-Time",
    "IBM": "https://www.ibm.com/employment/in-en/entrylevel.html",
    "Accenture": "https://www.accenture.com/in-en/careers/jobsearch?jk=full-time&location=India",
    "TCS": "https://www.tcs.com/careers/entry-level-jobs",
    "Wipro": "https://careers.wipro.com/careers/home?location=India&jobType=Full-Time",
    "Infosys": "https://www.infosys.com/careers/entry-level.html",
    "Cognizant": "https://careers.cognizant.com/global/en/search-results?keywords=full-time&location=India",
    "HCL": "https://www.hcltech.com/careers/entry-level-jobs",
    "Capgemini": "https://www.capgemini.com/in-en/careers/job-search/?location=India&jobType=Full-Time",
    "Tech Mahindra": "https://careers.techmahindra.com/careers/home?location=India&jobType=Full-Time",
    "L&T": "https://careers.larsentoubro.com/careers/home?location=India&jobType=Full-Time",
    "Zensar": "https://www.zensar.com/careers/entry-level-jobs",
    "Mphasis": "https://www.mphasis.com/careers/entry-level-jobs.html",
    "Mindtree": "https://www.mindtree.com/careers/entry-level-jobs",
    "Hexaware": "https://www.hexaware.com/careers/entry-level-jobs",
    "Zebra Technologies": "https://www.zebra.com/us/en/careers.html",
    "Qualcomm": "https://www.qualcomm.com/company/careers/university-recruiting/full-time",
    "NVIDIA": "https://www.nvidia.com/en-us/about-nvidia/careers/university-recruiting/full-time/",
    "Intel": "https://www.intel.com/content/www/us/en/jobs/locations/india.html",
    "Cisco": "https://jobs.cisco.com/jobs/SearchJobs/?3=Full-Time&4=India",
    "Salesforce": "https://www.salesforce.com/company/careers/university-recruiting/full-time/",
    "SAP": "https://www.sap.com/about/careers/university-recruiting/full-time.html",
    "Oracle": "https://www.oracle.com/corporate/careers/students-and-grads/full-time.html",
    "Adobe": "https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced/job/India/Full-Time-Software-Development--India--2024--2025--Internship--Full-Time--Remote_JR-100100",
    "VMware": "https://careers.vmware.com/main/jobs?location=India&jobType=Full-Time",
    "ServiceNow": "https://www.servicenow.com/careers/university-recruiting/full-time.html",
    "Atlassian": "https://www.atlassian.com/company/careers/university-recruiting/full-time",
    "Slack": "https://slack.com/careers/university-recruiting/full-time",
    "Zoom": "https://zoom.us/careers/university-recruiting/full-time",
    "Dropbox": "https://www.dropbox.com/jobs/university-recruiting/full-time",
    "LinkedIn": "https://careers.linkedin.com/students/full-time",
    "Twitter": "https://careers.twitter.com/en/students/full-time.html",
    "Snapchat": "https://www.snap.com/en-US/jobs/university-recruiting/full-time",
    "Pinterest": "https://www.pinterestcareers.com/university-recruiting/full-time",
    "Reddit": "https://www.redditinc.com/careers/university-recruiting/full-time",
    "Spotify": "https://www.spotifyjobs.com/university-recruiting/full-time",
    "Netflix": "https://jobs.netflix.com/full-time",
    "Uber": "https://www.uber.com/global/en/careers/university-recruiting/full-time",
    "Lyft": "https://www.lyft.com/careers/university-recruiting/full-time",
    "Airbnb": "https://www.airbnb.com/careers/university-recruiting/full-time",
}

# Replace with your actual Gemini API Key

# Initialize Gemini Flash model
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

st.set_page_config(page_title="Resume Analyzer", page_icon=":guardsman:", layout="wide")
st.title("Job Application Analyzer")
st.subheader("Analyze your resume and get personalized feedback")
file = st.file_uploader("Upload your resume", type=["pdf"], label_visibility="visible")
companies = ["Google", "Microsoft", "Amazon", "Meta", "Apple", "IBM", "Accenture", "TCS", "Wipro", "Infosys", "Cognizant", "HCL", "Capgemini", "Tech Mahindra", "L&T", "Zensar", "Mphasis", "Mindtree", "Hexaware", "Zebra Technologies", "Qualcomm", "NVIDIA", "Intel", "Cisco", "Salesforce", "SAP", "Oracle", "Adobe", "VMware", "ServiceNow", "Atlassian", "Slack", "Zoom", "Dropbox", "LinkedIn", "Twitter", "Snapchat", "Pinterest", "Reddit", "Spotify", "Netflix", "Uber", "Lyft", "Airbnb", "DoorDash", "Postmates", "Instacart", "Stripe", "Square", "PayPal", "eBay", "Shopify", "Wix", "Squarespace", "Weebly", "WordPress", "Blogger", "Tumblr", "Medium", "Substack"]

if file is not None:
    # Save the uploaded file to a temporary location
    with open(file.name, "wb") as f:
        f.write(file.getbuffer())

    # Display a success message
    st.success("File uploaded successfully!")
    
    with pdfplumber.open(file.name) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
        response = model.generate_content(f"Give me only the array not json of all the companies in string format and in `ascending order of eligible probability` not name, where the candidate strictly strongly eligible for intern roles in 3rd year btech and in india : {text}, choose from these companies list: {str(companies)}, only give me the array in string format, don't add any extra formatting or text")
        st.write("Eligible Companies:", response.text)
        arrOfCompanies = response.text.split(", '")
        arrOfCompanies[0] = arrOfCompanies[0].replace("[", "").replace("'", "")
        arrOfCompanies[-1] = arrOfCompanies[-1].replace("]", "").replace("'", "")
        for i in range(len(arrOfCompanies)):
            arrOfCompanies[i] = arrOfCompanies[i].replace("'", "").replace("[", "").replace("]", "").strip()
        arrOfCompanies = [company.strip() for company in arrOfCompanies if company.strip()]
        # st.write("Eligible Companies Array:", arrOfCompanies)
        # response = model.generate_content(f"If he wants to apply in google or microsoft, then how can he refine his skills to get selected in these companies and what are the key improvments needed, give in very detailed explained way: {text}")
        # st.write("Refined Skills and Key Improvements:", response.text)
        # st.download_button("Download Extracted Text", response.text, file_name="extracted_text.txt", mime="text/plain")
        for company in arrOfCompanies:
            if company in intern_carrier_distionary_india:
                st.link_button(f"Apply for {company}", url=intern_carrier_distionary_india[company])
            elif company in full_time_carrier_distionary_india:
                st.link_button(f"Apply for {company}", url=full_time_carrier_distionary_india[company])
            else:
                st.write(f"No link available for {company}.")
    # Remove the temporary file after processing
    import os
    os.remove(file.name)
else:
    st.write("Available companies for internship and full-time roles in India:")
    st.write("Internship Roles:")
    for company, link in list(intern_carrier_distionary_india.items())[:10]:
        st.link_button(f"Apply for {company}", url=link)
    st.button("See all internship roles", key="internship_roles", on_click=lambda: st.write(intern_carrier_distionary_india))
    st.write("Full-Time Roles:")
    for company, link in list(full_time_carrier_distionary_india.items())[:10]:
        st.write(f"- {company}: {link}")
    st.write("Note: The links provided are for reference purposes only. Please check the respective company websites for the most up-to-date information on job openings and application processes.")