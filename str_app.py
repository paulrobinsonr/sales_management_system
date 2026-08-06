import streamlit as st
import pandas as pd
from database_local import get_connection

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'role' not in st.session_state:
    st.session_state.role = ''
if 'username' not in st.session_state:
    st.session_state.username = ''    

st.set_page_config(
    page_title='Sales Management System',
    page_icon='📒',
    layout='centered'
    )
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0D47A1;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# ----------SIDEBAR---------
if st.session_state.logged_in:
    with st.sidebar:
        st.title('📒 Sales Management ')
        st.divider()
        if st.button('📊 DashBoard and Reports',use_container_width=True):
            pass
        if st.button('📋 Data Entry Workspace',use_container_width=True):
            pass
        if st.button('🗃️ Advanced SQL Engine',use_container_width=True):
            pass

        st.markdown("<br>", unsafe_allow_html=True)
        st.divider()

        st.write(f"🧑‍💻 **{st.session_state.username}**")
        st.write(f"🔑 **{st.session_state.role}**")


        st.markdown("<br>", unsafe_allow_html=True)
        st.divider()

        if st.button('⬅️ Logout',use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.role = ''
            st.session_state.username = ''
            st.session_state.branch_id = None
            st.rerun()

##------------Main Dashboard----
    st.title('📊 Dashboard and Reports')   
    st.caption(f'Welcome back,{st.session_state.username}')
    st.divider()
    st.subheader('🔍 Filter Controls')
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
            if st.session_state.role=='Super Admin':
                       branch= st.selectbox("Branch", options=['ALL', 'Chennai', 'Madurai', 'Trichy', 'Kovai', 'Theni'])
            else:
                 branch=branch_name
                 st.text_input           
    with col2:
            product= st.selectbox("Product",options=['ALL','DATA Analysis','Python','Machine Learning','AI','Data Science'])
    with col3:
         from_date= st.date_input('From Date')
    with col4:
         to_date= st.date_input('To Date')   
    with col5:
         st.write('')
         st.write('')
         apply_filter=st.button('Apply') 
##------Stacts--------
    conn=get_connection()
    cursor=conn.cursor()
    query="""SELECT SUM(gross_sales),SUM(received_amount),
    SUM(gross_sales-received_amount) FROM customer_sales WHERE 1=1"""
    params=[]
    if branch!='ALL':
         query +=" AND branch_id=(SELECT branch_id FROM branches WHERE branch_name=%s)"
         params.append(branch.lower())

    if product !="ALL":
         query +=" AND product_name=%s"
         params.append(product) 

    query +=" AND date BETWEEN %s AND %s"
    params.append(from_date)
    params.append(to_date) 

    st.write(query)
    st.write(params)    

    cursor.execute(query,params)    
    result=cursor.fetchone()

    gross_sales=result[0] or 0
    received_amount=result[1] or 0
    pending_amount=result[2] or 0
    if gross_sales>0:
        collection_percentage=(received_amount/gross_sales)*100
    else:
        collection_percentage=0
    cursor.close()
    conn.close()                
##------------Financial Summary----------------
    st.divider()
    st.subheader('💰 Financial Summary')
    card1, card2, card3, card4 = st.columns(4)
    with card1:
         st.metric(label='Gross Sales',value=f'₹{gross_sales:,.0f}')  
    with card2:
         st.metric(label='Received Amount',value=f'₹{received_amount:,.0f}')
    with card3:   
         st.metric(label='Pending Amount',value=f'₹{pending_amount:,.0f}')
    with card4:
         st.metric(label='Collection %',value=f'{collection_percentage:.2f}%')  

    st.divider()
    st.subheader('📈 Customer Sales')

    conn=get_connection()
    cursor=conn.cursor()
    if st.session_state.role=='Super Admin':
         query="""SELECT sale_id,branch_id,date,name,mobile_number,product_name,gross_sales,
         received_amount,status FROM customer_sales"""
         cursor.execute(query)
    else:
         query="""SELECT sale_id,branch_id,date,name,mobile_number,product_name,gross_sales,
         received_amount,status FROM customer_sales WHERE branch_id=%s"""
         cursor.execute(query,(st.session_state.branch_id,))

    sales=cursor.fetchall()
    column_names=['Sale ID','Branch ID','Date','Customer Name','Mobile Number',
                  'Product Name','Gross Sales','Received Amount','Status']

    df=pd.DataFrame(sales,columns=column_names)
    st.dataframe(df,use_container_width=True, 
    hide_index=True )
    cursor.close()
    conn.close()

                                             
    



    st.stop()         
        





st.markdown("""
<style>
.stApp{ color: black;}
</style>
""", unsafe_allow_html=True
)


st.title('📒 Sales Management System')
st.subheader('Please Login To Continue🔐')
#st.subheader('Super Admin Login')

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

    background-color: #000000 !important;   /* Blue */
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

##sql connection

if login:
    if username.strip() =="" or password.strip() =="":
        st.warning('Please enter Username and Password')
    else:
        conn=get_connection()
        cursor=conn.cursor()

        query="SELECT * FROM users WHERE username=%s AND password=%s"
        cursor.execute(query,(username,password))
        user=cursor.fetchone()

        if user:
            # st.success('Login Successful')
            # st.write(f"Welcome, {user[1]}")
            # st.write(f"Role: {user[4]}") 
            st.session_state.logged_in = True
            st.session_state.username = user[1]
            st.session_state.branch_id = user[3]
            st.session_state.role = user[4]
            cursor.close()
            conn.close()

            st.rerun()


            # if user[4] == 'Super Admin':
            #     st.success('Super Admin Access Granted')
            # elif user[4] == 'Admin':
            #     st.success('Admin Access Granted')
        else:
            st.error('Invalid Username or Password')    

            cursor.close()
            conn.close()            

  


