import streamlit as st
import os
import openai
import csv
import json
import pandas as pd
import redis


st.set_page_config(
    page_title="AI Chef",
    page_icon="🤖")


@st.cache_data
def redis_call(host, port, password):

    r = redis.Redis(
        host=host,
        port=port,
        password=password)

    keys = r.keys()
    values = r.mget(keys)

    data = {}

    for key, value in zip(keys, values):
        data[f"{key.decode()}"] = f"{value.decode()}"

    return data


st.image("./sample data/dalle_cover_lynx.png", use_column_width=True)
st.title("🤖 AI Chef")


data = redis_call(host=os.getenv('RD_HOST'),
                  port=os.getenv('RD_PORT'),
                  password=os.getenv('RD_PASS'))

OPENAI_API_KEY = st.sidebar.text_input('Your OpenAI API')

cuisine = st.sidebar.selectbox('Type of Cuisine',
                               ["Random", "Chinese", "French", "Greek", "Indian", "Italian", "Japanese", "Korean", "Mexican", "Middle Eastern", "Spanish", "Thai"])

nutrition = st.sidebar.selectbox('Nutrition Target',
                                 ["Any", "Weight Loss", "Balanced", "Muscle Gain", "Cheat Day Meal"])

portion = st.sidebar.select_slider('Number of Portions/People',
                                   options=[1, 2, 3, 4, 5, "custom"])

if portion == "custom":
    portion = st.sidebar.text_input("Number of People")

prep_time = st.sidebar.select_slider('Maximum Preparation Time (in minutes)',
                                     options=[15, 30, 45, 60, 'Unlimited'])


# openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


@st.cache_data
def recipe_generator(data, cuisine, nutrition, portion, prep_time):
    response = openai.Completion.create(
        # model="text-ada-001",
        model="text-davinci-003",
        prompt=f"suggest a recipe and cooking steps based on the items in this json file {data} in {cuisine} cuisine style, with {nutrition} nutrition target in mind. The recipe should be for {portion} persons and within {prep_time} of preparation and cooking time. Don't use all the ingredients and use the best possible combination economically and realistically. Also provide the total calor0ie count of the meal.",
        temperature=0.7,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response


cook = st.sidebar.button('Give me something to Cook!', key='cook')

if cook:
    recipe = recipe_generator(data, cuisine, nutrition, portion, prep_time)
    st.write(recipe['choices'][0]['text'])

    with open("./sample data/response_dump.txt", "a") as file:
        file.write(
            f"Inputs:- Cuisine: {cuisine}, Nutrition: {nutrition}, Portion: {portion}, Prep_time: {prep_time}\nOutput:-\n{recipe}\n\n")
