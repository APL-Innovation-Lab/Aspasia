import streamlit as st
import pandas as pd
from openai import OpenAI
from streamlit_option_menu import option_menu
import requests
from app import knowledge, knowledge_summary, timeline_data, resources_search, resource_clicked, path, paths_summary, path_prompt_submitted, knowledge_prompt_submitted, knowledge_builder_viewed, path_builder_viewed, chat_viewed, convert_df, quiz, quiz_response, chat_submitted, get_resources
from streamlit_timeline import timeline
from streamlit_card import card
import graphviz
import uuid
from markdown_pdf import MarkdownPdf
from markdown_pdf import Section

if 'org' not in st.session_state:
    st.session_state.org = 'Austin Public Library'
if 'chat_system_message' not in st.session_state:
    st.session_state.chat_system_message = """
                            You are an AI mentor named after Aspasia, a fifth century metic rhetorician and intellectual. You are a helpful, creative, and friendly companion on a user's journey of learning and self-improvement. You explain things thoughtfully and ask questions periodically. You are a project founded by Maxwell Knowles and this is a bespoke version built for APL Innovate to serve the Austin community.
                            
                            APL Innovate is Austin Public Library’s digital makerspace for collaboration and creation. We are providing community access to state-of-the-art computer hardware and software to create digital content such as podcasts, videos, 3D renderings, music, and more. From Apple to Windows, Adobe to Audacity, APL Innovate gives you the tech tools to polish your digital content and upskill your digital craft.

                            Check out our upcoming programs. 

                            After you visit, tell us what you #MadeAtAPL

                            Location & Hours
                            The digital makerspace is comprised of the Innovation Lab (Room 523) and the Innovation Lounge, both located on the 5th floor of the Central Library.

                            Address
                            Central Library - 5th Floor
                            710 W. Cesar Chavez St.
                            Austin, Texas 78701
                            Google Map | Parking

                            Operating Hours
                            Tuesday - Thursday: 11 a.m. - 7 p.m.
                            Friday - Saturday: 10 a.m. - 4 p.m.

                            Please contact the Library's Makerspace staff with any questions:

                            512-974-7442
                            Lib.InnovationLab@austintexas.gov 

                            Reserve a Makerspace Computer
                            The Library's Use Rules apply to the Innovation Lab (Room 523) and Innovation Lounge or when using any resources related to APL Innovate.

                            Reservations available for 2 hours and can be made in advance by text or online. 

                            For same-day reservations:
                            Text Austin Library Innovate to 512-898-7734
                            For same-day and future reservations: Reserve Online
                            Innovation Lab (Room 523)

                            Apple Mac Pro Tower (2)
                            Room capacity: 4
                            If the reserving party is more than 15 minutes late, they forfeit the reservation.
                            Innovation Lounge

                            Apple M1 iMac (5)
                            Dell Windows Desktop (8)
                        """
if 'chat_intro_message' not in st.session_state:
    st.session_state.chat_intro_message = "Hello! I'm an AI mentor named after Aspasia, a fifth century metic rhetorician and intellectual. You can think of me as a helpful, creative, and friendly companion on your journey of learning and self-improvement at the Austin Public Library (APL). Let's start a _*learning path*_. **What is your goal today?**"
if 'resources_link' not in st.session_state:
    st.session_state.resources_link = "https://raw.githubusercontent.com/maxwellknowles/CGU/main/APL%20x%20Aspasia%20-%20apl_resources_embeddings%20(1).csv"
if 'resources_repo' not in st.session_state:
    st.session_state.resources_repo = ""
if 'knowledge_breakdown' not in st.session_state:
    st.session_state.knowledge_breakdown = ''
if 'knowledge_summary' not in st.session_state:
    st.session_state.knowledge_summary = ''
if 'path_breakdown' not in st.session_state:
    st.session_state.path_breakdown = ''
if 'paths_summary' not in st.session_state:
    st.session_state.paths_summary = ''
if 'timeline' not in st.session_state:
    st.session_state.timeline = ''
if 'resources' not in st.session_state:
    st.session_state.resources = ''
if 'path_resources' not in st.session_state:
    st.session_state.path_resources = ''
if 'knowledge_prompt' not in st.session_state:
    st.session_state.knowledge_prompt = ''
if 'path_prompt' not in st.session_state:
    st.session_state.path_prompt = ''
#Tracking
if 'mixpanel' not in st.session_state:
    st.session_state.mixpanel = str(uuid.uuid4())

#PAGE CONFIGURATION
st.set_page_config(page_title="Aspasia x "+st.session_state.org, page_icon=":brain:", layout="wide", menu_items={'About': "Aspasia is raising consciousness and reinventing paths to knowledge for all."})

st.session_state.resources_repo = get_resources(st.session_state.resources_link)

with st.sidebar:
    if st.session_state.org != "Aspasia":
        st.write("**Public Alpha**")
    choose = option_menu("Aspasia: AI-Powered Learning & Path Building for Anyone, Anywhere", ["AspasiaGPT: Your Tutor & Guide", "Knowledge Builder", "Path Builder"],
                                    icons=['lightbulb', 'door-open', 'chat'],
                                    menu_icon="stars", default_index=0, orientation="vertical",
                                    styles={
                "container": {"padding": "5!important", "background-color": "white"},
                "icon": {"black": "white", "font-size": "25px"}, 
                "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#BBBBBD"},
                "nav-link-selected": {"background-color": "#192B25"},
            }
            )
    if st.session_state.org != "Aspasia":
        st.write("This is a free functional prototype for individuals to use in the pursuit of stronger civic engagement, economic viability, and intellectual dialogue. \n\nContact maxknowles27@gmail.com if you spot an error, have a feature request, or want to collaborate on a bespoke version for your organization.")

#START DASHBOARD
st.title('Aspasia for '+st.session_state.org)

@st.cache_resource()
def get_client():
    client = OpenAI(api_key=st.secrets["openai_key"], organization=st.secrets["organization"])
    return client

client = get_client()

st.write("Learning & Path Building for Anyone, Anywhere")

st.divider()

if choose == 'Knowledge Builder':

    knowledge_builder_viewed(st.session_state.org)

    st.header('Knowledge Builder')

    col1, col2 = st.columns([1,3], gap='large')
    with col1:
        prompt = st.text_area("What do you want to learn about?", value=st.session_state.knowledge_prompt)
        if prompt != '':
            st.session_state.knowledge_prompt = prompt
        submit_button = st.button("Submit")
    
    with col2:
        st.write("**About this tool**")
        st.write("Aspasia's knowledge builder is an experimental tool that abstracts the most critical dimensions of a topic to rapidly build context. Recommended resources, an interactive timeline, a brief quiz, and a downloadable PDF are surfaced dynamically with AI. Further engagement may continue through AspasiaGPT as well.")

    if submit_button:
        #KNOWLEDGE SUMMARY
        knowledge_prompt_submitted(prompt,st.session_state.org)
        with st.spinner("Drafting summary"):
            st.session_state.knowledge_summary = knowledge_summary(st.session_state.knowledge_prompt)
    
    #KNOWLEDGE FOUNDATIONS
    if st.session_state.knowledge_summary != '':
        st.subheader('Summary')
        st.markdown(st.session_state.knowledge_summary)
        with st.spinner("Establishing foundations"):
            st.session_state.knowledge_breakdown = knowledge(st.session_state.knowledge_prompt)
    
    if st.session_state.knowledge_breakdown != '':

        st.subheader("Foundations")

        with st.expander("Explore Foundational Knowledge", expanded=True):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.subheader(st.session_state.knowledge_breakdown['historical context']['title'])
                st.markdown(st.session_state.knowledge_breakdown['historical context']['content'])
            with col2:
                st.subheader(st.session_state.knowledge_breakdown['purpose']['title'])
                st.markdown(st.session_state.knowledge_breakdown['purpose']['content'])
            with col3:
                st.subheader(st.session_state.knowledge_breakdown['key functions or steps']['title'])
                st.markdown(st.session_state.knowledge_breakdown['key functions or steps']['content'])
            with col4:  
                st.subheader(st.session_state.knowledge_breakdown['ways to learn more']['title'])
                st.markdown(st.session_state.knowledge_breakdown['ways to learn more']['content'])    

    #CREATE TIMELINE
    if st.session_state.knowledge_breakdown != '':
        with st.spinner("Generating interactive timeline"):
            st.session_state.timeline = timeline_data(st.session_state.knowledge_prompt)

    #SHOW TIMELINE
    if st.session_state.timeline != '':
        timeline(st.session_state.timeline)

    #QUIZ    
    if st.session_state.knowledge_summary != '':
        with st.spinner("Generating quiz..."):
            quiz_specs = quiz(st.session_state.knowledge_summary)

        st.subheader("Quiz")
        with st.expander("Take a brief quiz...", expanded=True):
            st.write("Knowledge builders include an AI-generated quiz to help test your comprehension and build retention.")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("#### Question 1")
                st.write(quiz_specs['questions'][0]['question'])
                answers = []
                answers_df = pd.DataFrame(quiz_specs['questions'][0]['answers'])
                correct = answers_df[(answers_df['correct']==True)].reset_index(drop=True)
                response = st.radio("Select the best answer", answers_df['answer'],index=None)
                if response:
                    quiz_response(quiz_specs['questions'][0]['question'],response,st.session_state.org)
                    st.info("**Correct Response:** "+correct['answer'][0])
            with col2:
                st.markdown("#### Question 2")
                st.write(quiz_specs['questions'][1]['question'])
                answers = []
                answers_df = pd.DataFrame(quiz_specs['questions'][1]['answers'])
                correct = answers_df[(answers_df['correct']==True)].reset_index(drop=True)
                response = st.radio("Select the best answer", answers_df['answer'],index=None)
                if response:
                    quiz_response(quiz_specs['questions'][1]['question'],response,st.session_state.org)
                    st.info("**Correct Response:** "+correct['answer'][0])
            with col3:
                st.markdown("#### Question 3")
                st.write(quiz_specs['questions'][2]['question'])
                answers = []
                answers_df = pd.DataFrame(quiz_specs['questions'][2]['answers'])
                correct = answers_df[(answers_df['correct']==True)].reset_index(drop=True)
                response = st.radio("Select the best answer", answers_df['answer'],index=None)
                if response:
                    quiz_response(quiz_specs['questions'][2]['question'],response,st.session_state.org)
                    st.info("**Correct Response:** "+correct['answer'][0])

    #FIND RESOURCES
    if st.session_state.knowledge_breakdown != '':
        with st.spinner("Generating inexpensive recommended resources"):
            st.session_state.resources = resources_search(st.session_state.knowledge_prompt,st.session_state.resources_repo)

    #SHOW RESOURCES
    if isinstance(st.session_state.resources, pd.DataFrame):
        st.subheader("Recommended Resources")
        with st.expander("Free and inexpensive resources for your continued learning...", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                res = card(
                title=st.session_state.resources['resource'][0],
                text=st.session_state.resources['description'][0],
                styles={
                    "card": {
                        "width": "250px"
                    }
                },
                url=st.session_state.resources['link'][0],
                on_click=resource_clicked(prompt,st.session_state.resources['resource'][0],st.session_state.org)
                )
            with col2:
                res = card(
                title=st.session_state.resources['resource'][1],
                text=st.session_state.resources['description'][1],
                styles={
                    "card": {
                        "width": "250px"
                    }
                },
                url=st.session_state.resources['link'][1],
                on_click=resource_clicked(prompt,st.session_state.resources['resource'][1],st.session_state.org)
                )
            with col3:
                res = card(
                title=st.session_state.resources['resource'][2],
                text=st.session_state.resources['description'][2],
                styles={
                    "card": {
                        "width": "250px"
                    }
                },
                url=st.session_state.resources['link'][2],
                on_click=resource_clicked(prompt,st.session_state.resources['resource'][2],st.session_state.org)
                )

    if st.session_state.knowledge_breakdown != '':
        with st.expander("**Start A Learning Cycle?**"):
            st.write("Continue learning with a curated three-day series of AI-generated emails to help you build a habit and strengthen retention!")
            email = st.text_input("Enter email")
            topic = st.text_input("Enter topic", value="I want to learn about: "+st.session_state.knowledge_prompt)
            if st.button("Begin Learning Cycle"):
                if email:
                    requests.post("https://hooks.zapier.com/hooks/catch/8373893/3sm4sak/",json={'details':{'email':email, 'prompt':topic}})
                    st.success("The email entered will receive the first lesson shortly!")
                else:
                    st.error("Please enter an email.")

        text = "# Aspasia Knowledge Builer: "+st.session_state.knowledge_prompt+"\n\n"
        text += "## Summary\n\n"
        text += st.session_state.knowledge_summary+'\n\n'
        text += "## Foundations\n\n"
        text += "#### "+st.session_state.knowledge_breakdown['historical context']['title']+"\n\n"
        text += st.session_state.knowledge_breakdown['historical context']['content']+'\n\n'
        text += "#### "+st.session_state.knowledge_breakdown['purpose']['title']+"\n\n"
        text += st.session_state.knowledge_breakdown['purpose']['content']+'\n\n'
        text += "#### "+st.session_state.knowledge_breakdown['key functions or steps']['title']+"\n\n"
        text += st.session_state.knowledge_breakdown['key functions or steps']['content']+'\n\n'
        text += "#### "+st.session_state.knowledge_breakdown['ways to learn more']['title']+"\n\n"
        text += st.session_state.knowledge_breakdown['ways to learn more']['content']+'\n\n'
        pdf = MarkdownPdf(toc_level=2)
        pdf.add_section(Section(text))
        pdf.meta["title"] = "Aspasia Knowledge Builder"
        pdf.save("aspasia_knowledge_builder.pdf")

        with open("aspasia_knowledge_builder.pdf", "rb") as pdf_file:
            PDFbyte = pdf_file.read()

        st.download_button(label="Download PDF",
            data=PDFbyte,
            file_name="aspasia_knowledge_builder.pdf",
            mime='application/octet-stream')

if choose == 'Path Builder':

    path_builder_viewed(st.session_state.org)

    st.header("Path Builder")

    col1, col2 = st.columns([1,3], gap='large')
    with col1:
        prompt = st.text_area("What goal do you want to build paths towards achieving?", value=st.session_state.path_prompt)
        if prompt:
            st.session_state.path_prompt = prompt

        if st.button("Generate Paths"):
            path_prompt_submitted(prompt,st.session_state.org)
            with st.spinner("Generating Summary"):
                st.session_state.paths_summary = paths_summary(st.session_state.path_prompt)
    
    with col2:
        st.write("**About this tool**")
        st.write("Aspasia's path builder aspires to help anyone, anywhere think through the different ways they might achieve a goal or solve a problem. Whether you do or don't have financial resources, a good school or library, a strong network, or family support, _*we want to help you find ways to achieve all the good you can!*_")

    if st.session_state.paths_summary != '':
        st.subheader("Summary")
        st.session_state.paths_summary
        st.write("You can continue learning by clicking to chat with Aspasia, your AI personal mentor.")

    if st.session_state.paths_summary != '':
        st.subheader("Paths")
        with st.spinner("Generating paths"):
            st.session_state.path_breakdown = path(st.session_state.path_prompt)

        paths = st.session_state.path_breakdown
        paths_list = []
        for i in range(len(paths['paths'])):
            paths_list.append(paths['paths'][i]['title'])
        path_select = st.selectbox('Select Path', paths_list)
        for i in range(len(paths['paths'])):
            if paths['paths'][i]['title'] == path_select:
                st.write("**"+paths['paths'][i]['title']+"**")
                graph = graphviz.Digraph()
                for j in range(len(paths['paths'][i]['steps'])):
                    if j > 0:
                        graph.edge(paths['paths'][i]['steps'][j-1]['step'], paths['paths'][i]['steps'][j]['step'])
                st.graphviz_chart(graph)

        with st.spinner("Generating inexpensive recommended resources"):
            st.session_state.path_resources = resources_search(st.session_state.path_prompt,st.session_state.resources_repo)

    #SHOW RESOURCES
    if isinstance(st.session_state.path_resources, pd.DataFrame):
        st.subheader("Resources for your journey...")
        col1, col2, col3 = st.columns(3)
        with col1:
            res = card(
            title=st.session_state.path_resources['resource'][0],
            text=st.session_state.path_resources['description'][0] + " Click to explore this resource.",
            styles={
                "card": {
                    "width": "250px"
                }
            },
            url=st.session_state.path_resources['link'][0],
            on_click=resource_clicked(prompt,st.session_state.path_resources['resource'][0],st.session_state.org)
            )
        with col2:
            res = card(
            title=st.session_state.path_resources['resource'][1],
            text=st.session_state.path_resources['description'][1] + " Click to explore this resource.",
            styles={
                "card": {
                    "width": "250px"
                }
            },
            url=st.session_state.path_resources['link'][1],
            on_click=resource_clicked(prompt,st.session_state.path_resources['resource'][1],st.session_state.org)
            )
        with col3:
            res = card(
            title=st.session_state.path_resources['resource'][2],
            text=st.session_state.path_resources['description'][2] + " Click to explore this resource.",
            styles={
                "card": {
                    "width": "250px"
                }
            },
            url=st.session_state.path_resources['link'][2],
            on_click=resource_clicked(prompt,st.session_state.path_resources['resource'][2],st.session_state.org)
            )
    
    if st.session_state.path_breakdown != '':
        df = pd.DataFrame(st.session_state.path_breakdown)
        csv = convert_df(df)
        st.download_button(
            label=f"Download Paths",
            data=csv,
            file_name=f'aspasia.csv',
            mime='text/csv',
            use_container_width=True
            )

if choose == 'AspasiaGPT: Your Tutor & Guide':

    chat_viewed(st.session_state.org)

    st.header('AspasiaGPT')

    st.markdown("###### Start a chat or continue your line of growth from the knowledge and path builders. Unlike most AI chat interfaces, AspasiaGPT will often ask _*you*_ questions to prompt reflection or improve comprehension.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": st.session_state.chat_system_message},
            {"role": "assistant", "content": st.session_state.chat_intro_message},
            ]

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        else:
            pass

    if prompt := st.chat_input("How can Aspasia help?") or len(st.session_state.messages) == 1:
        if len(st.session_state.messages) == 1 and (st.session_state.knowledge_prompt != '' or st.session_state.path_prompt != ''):
            if st.session_state.knowledge_prompt != '':
                prompt = st.session_state.knowledge_prompt
            else:
                prompt = st.session_state.path_prompt
            st.session_state.messages.append({"role": "user", "content": prompt})
            #with st.chat_message("user", avatar="💭"):
                #st.markdown(prompt)

        if len(st.session_state.messages) > 1:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="💭"):
                st.markdown(prompt)

        if len(st.session_state.messages) > 1:
            with st.chat_message("assistant", avatar="🧠"):
                message_placeholder = st.empty()
                full_response = ""
                for response in client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True):
                    if response.choices[0].delta.content == None:
                        pass
                    else:
                        full_response += response.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                chat_submitted(prompt,full_response,st.session_state.org)
        
        chat_resources = resources_search(prompt,st.session_state.resources_repo)
        st.write("Highlighted resourcse from Austin Public Library...")
        col1, col2, col3 = st.columns(3)
        with col1:
            with st.expander(chat_resources['resource'][0]):
                st.write(chat_resources['description'][0])
                st.write(chat_resources['link'][0])
        with col2:
            with st.expander(chat_resources['resource'][1]):
                st.write(chat_resources['description'][1])
                st.write(chat_resources['link'][1])
        with col3:
            with st.expander(chat_resources['resource'][2]):
                st.write(chat_resources['description'][2])
                st.write(chat_resources['link'][2])

        #SPECIAL ACTIONS: LEARNING CYCLES AND PDF DOWNLOAD
        with st.expander("**Actions**"):
            st.markdown("#### Start a learning cycle...")
            st.write("Continue learning with a curated three-day series of AI-generated emails to help you build a habit and strengthen retention!")
            email = st.text_input("Enter email")
            topic = st.text_input("Enter topic", value="I want to learn about: "+st.session_state.knowledge_prompt)
            if st.button("Begin Learning Cycle"):
                if email:
                    requests.post("https://hooks.zapier.com/hooks/catch/8373893/3sm4sak/",json={'details':{'email':email, 'prompt':topic}})
                    st.success("The email entered will receive the first lesson shortly!")
                else:
                    st.error("Please enter an email.")

            text = "# AspasiaGPT Tutoring Thread\n\n"
            for i in range(len(st.session_state.messages)):
                if st.session_state.messages[i]["role"] != "system":
                    text += "**"+st.session_state.messages[i]['role']+"**" + '\n\n' + st.session_state.messages[i]['content'] + '\n\n'
                else:
                    pass
                            
            st.markdown("#### Download PDF for this tutoring session")

            pdf = MarkdownPdf(toc_level=2)
            pdf.add_section(Section(text))
            pdf.meta["title"] = "Aspasia GPT Tutoring"
            pdf.save("aspasiagpt_tutoring.pdf")

            with open("aspasiagpt_tutoring.pdf", "rb") as pdf_file:
                PDFbyte = pdf_file.read()

            st.download_button(label="Download PDF",
                data=PDFbyte,
                file_name="aspasiagpt_tutoring.pdf",
                mime='application/octet-stream')
