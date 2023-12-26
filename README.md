# BizCardX

### BizCardX: Extracting Business Card Data with OCR

# About:

This project is about to extract the contact information from a business card or a visiting card and to upload the data into a database and view it anytime you want, And this project uses ocr function to get the data and using Python script to decode and store then using streamlit to give a simple and interactive application to view and interfae with the data.

# Technologies Used

1.Python
2.Streamlit
3.EasyOcr
4.Matplotlib
5.Regular Expression(re)
6.Opencv
7.PostgreSQL
8.Psycopg2
9.Pandas
10.Numpy

# Workflow

Step-1
Install and import the required libraries

Step-2
Connect to the database where you want to store your data

Step-3
Define the workflow in functional blocks. Like extracting the text data from the given input and and show that using Opencv or PIL, 
Then create path for storing and viewing the data. You need to convert the image into binary type for storing into the SQL database.

Step-4
Create Streamlit app with simple UI. The data would be processed by buttons and tabs.

Step-5
Create SQL queries to view, edit, store, and delete the data. The data was executed by buttons.


# Process
First opening the streamlit app I created it will show the homepage contents and there is a sidebar showing Home, Data, Saved Cards.
I the Data section you can extract the data from the uploaded business card. The there is infinite number of models used to make business cards. The alignments was nott same on every card and the extracted data may be 100% accurate for few type of cards only though we can't optimise the app for every cards all the time so there is an editing section given in the data extraction page. The extracted data can be checked and modified before saving the informaation into the SQL database. 

Then in the saved cards section there is two tabs where you can view in one tab and edit or delete the data in the second tab. Every operations has conducted by python scripting and SQL querries.


# Conclution
This app is created for everyday use for individual as well as business use it can store a large amount of data with very low memory consumption.
This app has an user friendly and simple UI which is was easier to navigate through sections.
