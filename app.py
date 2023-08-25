import streamlit as st
from streamlit_chat import message
import pandas as pd

from src.search_handler import SearchHandler


# config
model_path = 'jhgan/ko-sroberta-multitask'

index_path = 'data/qa_dataset.h5'
qa_dataset_path = 'data/qa_dataset.csv'
prd_info_path = 'data/kbank_prd_info.csv'
key = '***'
    
if __name__ == "__main__":

    # load datset
    qa_df = pd.read_csv(qa_dataset_path, sep="|")
    prd_df = pd.read_csv(
                         prd_info_path, sep="|",
                         names=['category', 'pd_nm', 'pd_info']
                        )

    items = qa_df.to_dict(orient='index')

    prd_infos = {}
    for _, row in prd_df.iterrows():
        prd_infos[row[1]] = row[2]
        
    # load search handler
    search_handler = SearchHandler(items, prd_infos)
    search_handler.load_index(index_path)
    search_handler.load_model(model_path)
    search_handler.set_openai_key(key)

    # streamlit main
    st.header("DataBiz Kbank Chat-bot (Demo)")
    st.markdown("Scenario1. RAG(고객Q&A)")

    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    if 'past' not in st.session_state:
        st.session_state['past'] = []
        
    with st.form('form', clear_on_submit=True):
        user_input = st.text_input('You: ', '', key='input')
        submitted = st.form_submit_button('Send')

    if submitted and user_input:
        
        response = search_handler.get_response(user_input)
        
        st.session_state.past.append(user_input)
        st.session_state.generated.append(response)
        
    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])-1, -1, -1):
            message(st.session_state['past'][i],
                    is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))
