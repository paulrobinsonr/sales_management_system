import streamlit as st

st.set_page_config(
    page_title='Sales Management System',
    page_icon='📒',
    layout='centered'
    )
st.markdown(
    """
    <style>
    .stApp {
        background-color: #5FACD3;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown("""
<style>
.stApp{ color: black;}
</style>
""", unsafe_allow_html=True
)

st.title('📒 Sales Management System')
st.caption('Please Login To Continue🔐')
st.subheader('Super Admin Login')

st.markdown("""
<style>
.stTextInput input {
border : 2px solid #000000;}
</style>
""", unsafe_allow_html=True)


#box into white color

# st.markdown("""
# <style>
# .stTextInput input { background-color: #FFFFFF; }
# </style>
# """, unsafe_allow_html=True)

# font color change for user and password

# st.markdown("""
# <style>
# label { color: black!important:
# font-weight: bold; }</style>
# """, unsafe_allow_html=True)
# #css code for text input box
# st.markdown("""
# <style>

# ...
# YOUR CSS HERE
# ...

# </style>
# """, unsafe_allow_html=True)

username = st.text_input('Username')
password = st.text_input('Password', type='password')

login=st.button('Login')

#login button color change
st.markdown("""
<style>

/* Login Button */
.stButton > button {

    background-color: #0E4C92 !important;   /* Blue */
    color: white !important;                /* Text color */

    border: none;
    border-radius: 8px;

    font-size: 18px;
    font-weight: bold;

    height: 45px;
    width: 150px;
}

.stButton > button:hover {

    background-color: #1565C0 !important;

}

</style>
""", unsafe_allow_html=True)


