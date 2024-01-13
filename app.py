import streamlit as st
import pandas as pd
import numpy as np
from openai import OpenAI
from mixpanel import Mixpanel
import mixpanel
import numpy as np
import json
import uuid

client = OpenAI(api_key=st.secrets["openai_key"], organization=st.secrets["organization"])

mp = Mixpanel(st.secrets["mixpanel"])
openai_model = "gpt-4-1106-preview"

#Tracking
if 'mixpanel' not in st.session_state:
    st.session_state.mixpanel = str(uuid.uuid4())

#FUNCTIONS
@st.cache_data()
def get_resources(link):
    resources = pd.read_csv(link)
    resources['embedding'] = resources['embedding'].apply(eval).apply(np.array)
    return resources

#download data as CSV
@st.cache_resource
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

@st.cache_data()
def knowledge(prompt):
    response = client.chat.completions.create(
        model=openai_model,
        messages = [
            {'role':'system','content':"You are an AI assistant that provides a json with a title and content for these fields for a given topic/objective: historical context, purpose, key functions or steps, ways to learn more. It should look like this: {'historical context': {'title': title,'content': content}, 'purpose': {'title': title,'content': content}, 'key functions or steps': {'title': title,'content': content},'ways to learn more': {'title': title,'content': content}}. Do not respond with anything but the json."},
            {'role':'user', 'content': "Here's what I want to learn about: "+prompt}
        ],
        response_format={ 'type': "json_object" }
    )
    response = json.loads(response.choices[0].message.content)
    return response

@st.cache_data()
def knowledge_summary(prompt):
    response = client.chat.completions.create(
        model=openai_model,
        messages = [
            {'role':'system','content':"You are a kind, helpful AI mentor and tutor helping users find paths to solve problems or achieve goals. You don't respond conversationally, but just provide content."},
            {'role':'user','content': "Please provide a paragraph summary. Here's what I want to learn about: "+prompt}
        ]
        )
    response = response.choices[0].message.content
    return response

@st.cache_data()
def quiz(lesson):
    response = client.chat.completions.create(model=openai_model,
        messages = [
            {'role':'system','content':"You are an AI assistant that provides a json with three questions with four multiple choice answers each for a given subject to test knowledge/build retention. It should look like this (for three questions): {'questions': [{'question':question, 'answers':[{'answer':answer, correct: true/false}...]}...]}. Do not respond with anything but the json."},
            {'role':'user', 'content': "Please provide some questions to test someone's retention of this lesson: "+lesson}
        ],
        response_format={ 'type': "json_object" }
        )
    response = json.loads(response.choices[0].message.content)
    return response

@st.cache_data()
def path(prompt):
    response = client.chat.completions.create(model=openai_model,
        messages = [
            {'role':'system','content':"You are an AI assistant that only provides a json with steps for three different paths someone can take that'll be graphed on a graphviz chart. It should look like this: {'paths': [0 {'title': path_title,'steps':[0 {'step':path_step}, 1 {'step':path_step}...]} 2...]}. I should be able to identify a path with code like this: response['paths'][i]['title']. I should be able to identify a step with code like this: response['paths'][i]['steps'][j]['step']. Do not respond with anything but the json."},
            {'role':'user', 'content': "Here's what I want to do: "+prompt}
        ],
        response_format={ 'type': "json_object" }
        )
    response = json.loads(response.choices[0].message.content)
    return response

@st.cache_data()
def paths_summary(prompt):
    response = client.chat.completions.create(model=openai_model,
        messages = [
            {'role':'system','content':"You are a kind, helpful AI mentor and tutor helping users find paths to solve problems or achieve goals. You don't respond conversationally, but just provide content."},
            {'role':'user','content': "Please provide a paragraph discussing some steps I may take. Here's what I want to do: "+prompt}
        ]
        )
    response = response.choices[0].message.content
    return response

@st.cache_data()
def timeline_data(prompt):
    response = client.chat.completions.create(model=openai_model,
        messages = [
            {'role':'system','content':"You are an AI assistant that provides a json with timeline data for a given topic/objective. Don't include an end year if there it isn't applicable. It should look like this (may be multiple events): {'title': {'text':{'headline': headline,'text':text}}, 'events':[{'start_date':{'year':year integer},'end_date':{'year':year integer}, 'text':{'headline':headline, 'text':text}},{'start_date':{'year':year integer},'end_date':{'year':year integer}, 'text':{'headline':headline, 'text':text}} ...]}."},
            {'role':'user', 'content': "Here's what I want to learn about: "+prompt}
        ],
        response_format={ 'type': "json_object" }
        )
    response = json.loads(response.choices[0].message.content)
    return response

#searching resources
@st.cache_data()
def resources_search(prompt,resources):
    try:
        embedding = client.embeddings.create(input=prompt, model='text-embedding-ada-002', encoding_format='float').data[0].embedding
        #resources['similarities'] = resources.embedding.apply(lambda x: client(x, embedding))
        resources['similarities'] = len(resources)
        for i in range(len(resources)):
            resources['similarities'][i] = np.dot(resources['embedding'][i], embedding)/(np.linalg.norm(resources['embedding'][i])*np.linalg.norm(embedding))
        recs = resources.sort_values('similarities', ascending=False).head(3)
        recs_df = recs.reset_index(drop=True)
    except:
        recs_df = ""
    return recs_df

def resource_clicked(prompt,resource,org):
    try:
        mp.track(distinct_id=st.session_state.mixpanel,event_name="Resource Clicked",properties={"Prompt":prompt,"Resource":resource,"Org":org})
    except mixpanel.MixpanelException:
        pass

def knowledge_builder_viewed(org):
    try:
        mp.track(distinct_id=st.session_state.mixpanel,event_name="Knowledge Builder Viewed", properties={"Org":org})
    except mixpanel.MixpanelException:
        pass

def path_builder_viewed(org):
    try:
        mp.track(distinct_id=st.session_state.mixpanel,event_name="Path Builder Viewed", properties={"Org":org})
    except mixpanel.MixpanelException:
        pass

def chat_viewed(org):
    try:
        mp.track(distinct_id=st.session_state.mixpanel,event_name="Chat Viewed", properties={"Org":org})
    except mixpanel.MixpanelException:
        pass

def knowledge_prompt_submitted(prompt, org):
    try:
        mp.track(distinct_id=st.session_state.mixpanel,event_name="Knowledge Prompt Submitted", properties={"Prompt":prompt,"Org":org})
    except mixpanel.MixpanelException:
        pass

def path_prompt_submitted(prompt, org):
    try:
        mp.track(distinct_id=st.session_state.mixpanel,event_name="Path Prompt Submitted", properties={"Prompt":prompt,"Org":org})
    except mixpanel.MixpanelException:
        pass

def quiz_response(question, answer, org):
    try:
        mp.track(distinct_id=st.session_state.mixpanel,event_name="Path Prompt Submitted", properties={"Question":question, "Response":answer, "Org":org})
    except mixpanel.MixpanelException:
        pass

def chat_submitted(prompt,response,org):
    try:
        mp.track(distinct_id=st.session_state.mixpanel,event_name="Chat Prompt Submitted", properties={"Question":prompt, "Response":response, "Org":org})
    except mixpanel.MixpanelException:
        pass
