YouTube Data Harvesting and Warehousing using SQL and Streamlit

This project aims to harvest and analyze data from YouTube using the YouTube Data API, store it in mysql and  analyze the youtube channel information.

Prerequisites:
Before running the scripts, make sure you have the following dependencies installed:
- `Python` 3.x installed on your system
- Enable YouTube Data API (API key)
 

Install the following packages in the python environment
-	`sqlite3 package`(for mysql interaction) - this will be part of python no need to install separately
-	`isodate package` (for duration convertion)
- 	`pandas package` (for data manipulation and analysis)
-	`streamlit package` (for User Interface and interactive data visualization)
-	`Google Client Library` for YouTube Data API for data retrieval from youtube

You can install the required Python packages using pip:

•	pip install streamlit
•	pip install isodate
•	pip install pandas
•	pip install google-api-python-client
	
The Project consist of the following files:

1. app.py
This file contains the code for Scrapping data from YouTube using the YouTube Data API v3. It provides functions to generate output in JSON format and upload the data to mysql.
This file implements a graphical user interface (GUI) using Streamlit. The GUI allows users to interact with the project functionalities. It provides options to retrieve data from YouTube, upload it to mysql, view the migrated data, and perform selective data analysis.
2. db.py
This file handles the connection and interaction with the mysql database.


Steps to Enable YouTube Data API v3

1. Create a Google Cloud Platform Project:
Go to the Google Cloud Platform console: https://console.cloud.google.com/
Create a new project or select an existing one.
2. Enable the YouTube Data API v3:
In the Google Cloud Platform console, navigate to the API & Services section.
Search for "YouTube Data API v3" and enable it.
3. Create API Credentials:
In the API & Services section, click on "Credentials".
Click "Create credentials" and select "API key".
A new API key will be generated. Copy and save this key securely.
Important Note: Treat your API key as a secret. Avoid sharing it publicly or hardcoding it into your application.

Using the API Key:

Once you have your API key, you can use it to authenticate your requests to the YouTube Data API v3. You'll typically need to include it as a parameter in your API requests.
(I Used this key app.py)



App Execution


1.Run below command in Visual studio 
C:\Users\Karthik\OneDrive\Documents\Datas_AIML\Projects\MiniProject_1(Youtube Data Harvasting)> streamlit run app.py
