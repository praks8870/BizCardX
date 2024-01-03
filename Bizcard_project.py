import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import cv2
import easyocr
from streamlit_option_menu import option_menu
import psycopg2
import re
import os
from tempfile import NamedTemporaryFile
import numpy as np
import vobject

st.set_page_config(page_title="Bizcard Data Extraction",
                   layout='wide',
                   initial_sidebar_state='expanded')
st.title("BizCardX: Extracting Business Card Data with OCR")

st.markdown("""
    <style>
        .stApp {
            background-image: url("https://wallpaper-mania.com/wp-content/uploads/2018/09/High_resolution_wallpaper_background_ID_77700001323.jpg");
            background-size: cover;
        }

        [data-testid="stSidebar"] {
            background-image: url('https://wallpaper-mania.com/wp-content/uploads/2018/09/High_resolution_wallpaper_background_ID_77700459179.jpg');
            background-size: cover;
        }
    </style>
""", unsafe_allow_html = True)

mydb = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="123456"
)

mycursor = mydb.cursor()

reader = easyocr.Reader(['en'])


def create_table():
    query = """CREATE TABLE IF NOT EXISTS bizcard (
                name TEXT,
                designation TEXT,
                company TEXT,
                phone VARCHAR(255) PRIMARY KEY,
                mail VARCHAR(255),
                website VARCHAR(255),
                address VARCHAR(255),
                state VARCHAR(255),
                pincode NUMERIC,
                card BYTEA
            )
        """

    mycursor.execute(query)
    mydb.commit()
    print("Table created successfully.")


create_table()


#Extract Data from the Uploaded file
def ocr_extract(card_path):
    reader = easyocr.Reader(['en'])
    result = reader.readtext(card_path)

    img = cv2.imread(card_path)

    for detection in result:
        points = detection[0]
        (tl, tr, br, bl) = points
        tl = (int(tl[0]), int(tl[1]))
        tr = (int(tr[0]), int(tr[1]))
        br = (int(br[0]), int(br[1]))
        bl = (int(bl[0]), int(bl[1]))

        cv2.rectangle(img, tl, br, (0, 0, 255), 2)

    fig, ax = plt.subplots()
    ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    ax.set_title('Highlighted Words')
    ax.axis('off')
    st.pyplot(fig)

#Save uploaded file
def save_file(card):
    os.makedirs("uploaded cards", exist_ok=True)
    file_path = os.path.join("uploaded cards", card.name)

    # Save the file
    with open(file_path, "wb") as f:
        f.write(card.getbuffer())

    return file_path


#Convert the iimage to binary data to store it into a database
def binary_conv(card):
    with open(card, "rb") as image_file:
        bin_data = image_file.read()
    return bin_data

#Create a dataset using the extracted data from the uploaded card
def create_df(path):
    data = []

    entry = {'name': None,
            'designation': None,
            'company': None,
            'phone': None,
            'mail': None,
            'website': None,
            'address': None,
            'state': None,
            'pincode': None,
            'card': None
            }

    for ent, i in enumerate(path):
        if ent == 0:
            entry['name'] = i
        if ent == 1:
            entry['designation'] = i
        if ent == len(path) - 1:
            entry['company'] = i
        if "-" in i:
            entry['phone'] = i
        if "@" in i:
            entry['mail'] = i
        if 'www' in i.lower() or 'www.' in i.lower():
            entry['website'] = i
        if re.findall('^[0-9].+, [a-zA-Z]+', i):
            entry['address'] = i
        if re.findall('[a-zA-Z] +[0-9]', i):
            index = re.search(r'[,\s]', i).start()
            k = i[:index]
            entry['state'] = k
        sm = re.findall('[a-zA-Z]+[ ,\-]+([0-9]+)', i)
        if sm:
            l = sm[0]
            entry['pincode'] = l

        entry['card'] = binary_conv(temp_file_path)

    data.append(entry)

    df = pd.DataFrame(data)
    return df


def insert_data_into_sql(df):
    for i, row in df.iterrows():
        query_insert = """INSERT INTO bizcard(
                    name, designation, company, phone, mail, website, address, state, pincode, card)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (phone)
                    DO NOTHING;
                    """
        mycursor.execute(query_insert, tuple(row))
        mydb.commit()


def update_data(uploaded_card):
    query2 = """update bizcard set name = %s, designation = %s, company = %s, phone = %s, mail = %s, website = %s, address = %s, state = %s, pincode = %s
                where name = %s"""

    values = (name, designation, company, phone, mail, website, address, state, pincode, uploaded_card)

    mycursor.execute(query2, values)
    mydb.commit()


#Update the data to the PGSQL database 
def update_data2(phone):
    query2 = """update bizcard set name = %s, designation = %s, company = %s, phone = %s, mail = %s, website = %s, address = %s, state = %s, pincode = %s
                where phone = %s"""

    values = (name, designation, company, phone, mail, website, address, state, pincode, phone)

    mycursor.execute(query2, values)
    mydb.commit()

#Load data in the uploaded image
def load_data(uploaded_card):
    query1 = f"""select * from bizcard
                             where name = '{uploaded_card}'"""
                            
    mycursor.execute(query1)
    mydb.commit()

    return mycursor.fetchone()

#View data from PGSQL database
def view_data(names):
    query4 = f"""select * from bizcard
                             where name = '{names}'"""
                            
    mycursor.execute(query4)
    mydb.commit()

    return mycursor.fetchall()

#Convert the binary file back to an image file
def conv_bin_to_image(names):
    
    query5 = f"""select card from bizcard
                where name = '{names}'"""
    mycursor.execute(query5)
    mydb.commit()
    
    data = mycursor.fetchone()
    
    binary = data[0]

    image_np_array = np.frombuffer(binary, dtype=np.uint8)

    image_cv2 = cv2.imdecode(image_np_array, cv2.IMREAD_COLOR)

    # Convert BGR to RGB
    image_rgb = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2RGB)

    figsize = (15 , 15)

    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(image_rgb)
    ax.set_title("Preview of Saved Card")
    ax.axis('off')
    st.pyplot(fig)



# Configure Streamlit buttons to change color if clicked
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False


with st.sidebar:
    selected = option_menu(None, ['Home', 'Data', 'Saved Cards'],
                            icons=["house-door-fill", "tools"],
                            default_index=0,
                            orientation="v",
                            styles={"nav-link": {"font-size": "30px", "text-align": "centre", "margin": "0px",
                                                "--hover-color": "#33A5FF"},
                                    "icon": {"font-size": "30px"},
                                    "container": {"max-width": "6000px"},
                                    "nav-link-selected": {"background-color": "#33A5FF"}})

# file_path = save_file(card)

if selected == "Home":
    col1,col2 =st.columns(2, gap = 'medium')

    col1.markdown("### :blue[Title] : BizCardX Data Extractions")
    col1.markdown("### :blue[Overview] : This project is about to extract the contact information from a business card or a visiting card and to upload the data into a database and view it anytime you want, And this project uses ocr function to get the data and using Python script to decode and store then using streamlit to give a simple and interactive application to view and interfae with the data.")
    col1.markdown("### :blue[Technologies Used] : Python, Streamlit, Pandas, Matplotlib, PostgreSql, Psycopg2, Opencv, Regular Expressions, EasyOcr")



if selected == "Data":
    card = st.file_uploader("Upload your card here", label_visibility="collapsed", type=['png', 'jpg', 'jpeg'])

    if card is not None:
        # Save the uploaded file temporarily
        temp_file = NamedTemporaryFile(delete=False)
        temp_file_path = temp_file.name
        temp_file.write(card.read())
        temp_file.close()

        path = reader.readtext(temp_file_path, detail = 0, paragraph = False)

        file_path = save_file(card)

        df = create_df(path)
        first_row = df.iloc[0]
        uploaded_card = first_row['name']

        col1, col2 = st.columns([1, 2])
        with col1:
            #Extracting the data from the uploaded image
            ocr_extract(file_path)
            st.text("Extracted Data")
            data_container = st.empty()  # Create an empty container
            st.session_state.button_clicked = not st.session_state.button_clicked
            
            if st.button("Extract", key='extract_button', help="Click to extract data"):
                insert_data_into_sql(df)
                data_container.write(df)
            

        with col2:
            
            # load the data which is extracted from the uploaded card
            d = load_data(uploaded_card)

            if d is not None:
                name_input = st.text_input("Name", d[0])
                designation_input = st.text_input("Designation", d[1])
                company_input = st.text_input("Company", d[2])
                phone_input = st.text_input("Phone", d[3])
                mail_input = st.text_input("Mail_ID", d[4])
                website_input = st.text_input("Website", d[5])
                address_input = st.text_input("Address", d[6])
                state_input = st.text_input("State", d[7])
                pincode_input = st.text_input("Pincode", d[8])

                if st.button("Update Data"):
                    # Get values from input variables
                    name = name_input
                    designation = designation_input
                    company = company_input
                    phone = phone_input
                    mail = mail_input
                    website = website_input
                    address = address_input
                    state = state_input
                    pincode = pincode_input

                    update_data(uploaded_card)
                    st.success("Data Uploaded to Database")


            else:
                st.warning(f"No data found for the name {uploaded_card}.")



        # Remove the temporary file
        os.remove(temp_file_path)



if selected == "Saved Cards":

    tab1, tab2 = st.tabs(["$\huge View $", "$\huge Edit / Delete $"])

    with tab1:
        #view the saved card data
        query3 = """SELECT name from bizcard"""

        mycursor.execute(query3)
        mydb.commit()

        n = mycursor.fetchall()
        name_data = pd.DataFrame(n)

        names = st.selectbox("Select a name", name_data[0].tolist(), key = "box_tab1")

        col1, col2 = st.columns([1, 2])

        if st.button("View"):
            #view the saved image
            d = view_data(names)
            df_view = pd.DataFrame(d, columns=[desc[0] for desc in mycursor.description])
            st.write(df_view)

            conv_bin_to_image(names)

            
    with tab2:       
        #load the data for editing and deleting
        query3 = """SELECT name from bizcard"""

        mycursor.execute(query3)
        mydb.commit()

        n = mycursor.fetchall()
        name_data = pd.DataFrame(n)

        names2 = st.selectbox("Select a name", name_data[0].tolist(), key = "box_tab2")

        f = view_data(names2)
        df_view2 = pd.DataFrame(f, columns=[desc[0] for desc in mycursor.description])
        st.write(df_view2)

        d = load_data(names2)

        if d is not None:
            # Edit the data from the database using text input
            name_input = st.text_input("Name", d[0])
            designation_input = st.text_input("Designation", d[1])
            company_input = st.text_input("Company", d[2])
            phone_input = st.text_input("Phone", d[3])
            mail_input = st.text_input("Mail_ID", d[4])
            website_input = st.text_input("Website", d[5])
            address_input = st.text_input("Address", d[6])
            state_input = st.text_input("State", d[7])
            pincode_input = st.text_input("Pincode", d[8])

            if st.button("Update Data"):
                # Get values from input variables
                name = name_input
                designation = designation_input
                company = company_input
                phone = phone_input
                mail = mail_input
                website = website_input
                address = address_input
                state = state_input
                pincode = pincode_input

                update_data(names2)
                st.success("Data Uploaded to Database")

            if st.button("Delete Data"):
                #for deleting the data from database for the selected name
                query6 = f"""DELETE FROM bizcard
                            where name = '{names2}'"""
                
                mycursor.execute(query6)
                mydb.commit()

                st.error("Data Deleted Successfully")


        else:
            st.warning(f"No data found for the name.")

