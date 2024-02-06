# import necessary files
import os
import streamlit as st
from PIL import Image

st.set_page_config(page_title='Team Members & Contributions', page_icon=':computer:', layout='wide')

# create title and underline
st.title("Meet the Team")
st.markdown("<hr><br>", unsafe_allow_html=True)

# create 3 columns
headshot1, headshot2, headshot3 = st.columns(3)

# set a common image width
image_width = 300

# load image into streamlit with caption
dir_path = os.path.dirname(os.path.realpath('4_👨_💻_About_us.py'))

# create path to image of sam
rel_path_sam = "/pages/pictures/sam_urell.png"
abs_path_sam = dir_path + rel_path_sam


image_sam = Image.open(abs_path_sam)

# display image of sam in desired column
with headshot1:
    st.image(image_sam, width=image_width)

    # generate text in centred format
    st.markdown("""
              <div style='text-align: center;'>
                  <strong>Sam Urell</strong><br>
                  22465384<br>
                  Email: samuel.urell@ucdconnect.ie
              </div>
              """, unsafe_allow_html=True)

# create path to image of arnav
rel_path_arnav = "/pages/pictures/arnav_rattan.png"
abs_path_arnav = dir_path + rel_path_arnav

image_arnav = Image.open(abs_path_arnav)

# display image of arnav in desired column
with headshot2:
    st.image(image_arnav, width=image_width)

    # generate text in centred format
    st.markdown("""
        <div style='text-align: center;'>
            <strong>Arnav Rattan</strong><br>
            22204232<br>
            Email: arnav.rattan@ucdconnect.ie
        </div>
        """, unsafe_allow_html=True)

# create path to image of hugh
rel_path_hugh = "/pages/pictures/hugh_munro.png"
abs_path_hugh = dir_path + rel_path_hugh

image_hugh = Image.open(abs_path_hugh)

# display image of hugh in desired column
with headshot3:
    st.image(image_hugh, width=image_width)

    # generate text in centred format
    st.markdown("""
     <div style='text-align: center;'>
          <strong>Hugh Munro</strong><br>
          22347541<br>
          Email: hugh.munro@ucdconnect.ie
      </div>
      """, unsafe_allow_html=True)
