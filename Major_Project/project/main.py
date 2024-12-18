import streamlit as st
from scrape import scrape_Websites,split_dom_content,clean_body_content,extract_body_content
from parse import parse_with_ollama

st.title('AI Web Scraper')
url = st.text_input("Enter any website URL:")

if st.button("Scrape Site"):
    st.write("Scraping the website")
    result = scrape_Websites(url)
    body_content = extract_body_content(result)
    clean_content = clean_body_content(body_content)

    st.session_state.dom_content = clean_content

    with st.expander("View Dom Content"):
        st.text_area("Dom Content",clean_content,height=300)

if 'dom_content' in st.session_state:
    parse_description = st.text_area("Want me to explain, analyze or organize the extracted data for you ?")

    if st.button('Parse Information'):
        if parse_description:
            st.write('Parsing the content')

            dom_chunks = split_dom_content(st.session_state.dom_content)
            result = parse_with_ollama(dom_chunks,parse_description)
            st.write(result)