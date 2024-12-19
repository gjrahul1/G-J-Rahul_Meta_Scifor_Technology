import streamlit as st
from scrape import scrape_Websites,split_dom_content,clean_body_content,extract_body_content


st.title('Web Scraper')
url = st.text_input("Enter any website URL:")

if st.button("Scrape Site"):
    st.write("Scraping the website")
    result = scrape_Websites(url)
    body_content = extract_body_content(result)
    clean_content = clean_body_content(body_content)

    st.session_state.dom_content = clean_content

    with st.expander("View Dom Content"):
        st.text_area("Dom Content",clean_content,height=300)

