import streamlit as st
st.title('Sales Management dashboard')

st.subheader('🔐 Super Admin Login')

username = st.text_input('Username')
password = st.text_input('Password', type='password')

login=st.button('Login')


