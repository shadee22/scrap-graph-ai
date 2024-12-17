import os
import subprocess
import json
import nest_asyncio
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperGraph
import streamlit as st
import datetime

# Run setup.sh to install Playwright browsers if not already set up
if not os.path.exists("setup_complete.txt"):
    subprocess.run(["bash", "setup.sh"], check=True)
    with open("setup_complete.txt", "w") as f:
        f.write("Setup Complete")

# Apply nest_asyncio for Jupyter/IPython environments
nest_asyncio.apply()

# Function to list all .txt files in the specified directory
def list_txt_files(directory="."):
    """
    List all .txt files in the specified directory.
    """
    return [file for file in os.listdir(directory) if file.endswith(".txt") and file != "requirements.txt"]

# Function to run the scraper
def run_scraper(source_url, description, api_key):
    """
    Run the scraper using SmartScraperGraph.
    """
    config = {
        "llm": {
            "model": "groq/llama-3.1-8b-instant",
            "api_key": api_key,  # User's API key
            "temperature": 0
        },
        "embeddings": {
            "model": "ollama/nomic-embed-text",
        },
    }
    try:
        smart_scraper_graph = SmartScraperGraph(
            prompt=f"website url: {source_url}. your task: {description}",
            source=source_url,
            config=config
        )
        return smart_scraper_graph.run()
    except Exception as e:
        return {"error": str(e)}

# Function to save results to a file
def save_result(result, source_url):
    """
    Save the scraping result to a file with a structured filename.
    """
    try:
        domain_name = source_url.split("//")[-1].split("/")[0]  # Extract domain name
        today_date = datetime.datetime.now().strftime("%Y-%m-%d")  # Get today's date
        filename = f"{today_date}_{domain_name}.txt"  # Filename format

        with open(filename, "w") as f:
            f.write(json.dumps(result, indent=4))  # Convert result to JSON
        return filename
    except Exception as e:
        return str(e)

# Streamlit App
if __name__ == "__main__":
    # Logo and Title
    st.image(
        "https://www.pulseid.com/wp-content/uploads/2023/11/pulse-logo-with-text-1.png",
        caption="All Rights Reserved by Pulse ID",
        width=200
    )
    st.title("Groq Llama-3.1-8b-instant Scraper")

    # Session state for persistence
    if "scraping_result" not in st.session_state:
        st.session_state.scraping_result = None

    # Input fields
    st.subheader("Input Parameters")
    source_url_input = st.text_input("Enter the source URL:", "https://perinim.github.io/projects/")
    description_input = st.text_area("Enter your task description:", "List me all the projects with their description.")
    api_key_input = st.text_input("Enter your Groq API Key:", type="password")  # Secure input for API key

    # Run Scraper Button
    if st.button("Run Scraper"):
        if api_key_input:  # Validate API Key
            with st.spinner("Scraping in progress..."):
                result = run_scraper(source_url_input, description_input, api_key_input)
                st.session_state.scraping_result = result  # Store result in session state
                st.success("Scraping completed successfully!")
        else:
            st.error("Please enter your Groq API Key.")

    # Display Results
    if st.session_state.scraping_result:
        st.subheader("Scraping Result")
        st.json(st.session_state.scraping_result)  # Display result in JSON format

        # Save Result Button
        if st.button("Save Result"):
            filename = save_result(st.session_state.scraping_result, source_url_input)
            if os.path.exists(filename):
                st.success(f"Result saved to `{filename}`")
            else:
                st.error(f"An error occurred: {filename}")

    # List Saved .txt Files
    st.subheader("List of Saved .txt Files")
    txt_files = list_txt_files()
    if txt_files:
        for file in txt_files:
            with open(file, "r") as f:
                st.download_button(label=f"Download {file}", data=f, file_name=file, mime="text/plain")
    else:
        st.info("No .txt files found in the current directory.")

# RUN COMMAND
#  python3 -m streamlit run scraper.py