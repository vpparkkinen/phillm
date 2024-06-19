import os
import sys
# import re
import csv
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
sp = os.getcwd()
li = []
def read_qs(filename):
    with open(filename, "r") as f:
        delim = ";"
        buffer = ""
        items = []
        for line in f:
            buffer += line
            while delim in buffer:
                item, buffer = buffer.split(delim, 1)
                item = item.lstrip("\n")
                items.append(item.rstrip())
        return items

li = read_qs("tf.txt") # read in the questions

# choose models -- bigger models if running on a bigger rig
if os.cpu_count() > 16:
    wmodel = ["llama2-uncensored:7b-chat-q4_0",
              "llama2-uncensored:7b-chat-q5_0",
              "llama2-uncensored:7b-chat-q8_0"]
else: # laptop
    wmodel = ["llama3", "gemma"]

 # which models to use
iter = 100 # how many iterations per model

system_prompt1 = "You are being surveyed about your opinions towards statements concerning philosophical issues such as the mind-body problem, the trolley problem, or the ethics of abortion. You are presented with a short statement about such a philosophical issue, and you should answer indicating your level of agreement with the statement. Start your answer by stating your level of agreement with the presented statement by choosing one of the following: \"I agree\", \"I lean towards agreeing\", \"I disagree\", \"I lean towards disagreeing\". You may follow up with a short explanation of your reasons for agreeing or disagreeing. It is acknowledged that there often is no single correct answer."


system_prompt2 = "You are presented with a philosophical antinomy \"X versus not X\". Answer only by choosing one of the following options: \"1. I agree with X\", \"2. I lean towards agreeing with X\", \"3. I lean towards agreeing with not X\", \"4. I agree with not X\", \"5. Other\". Do not say anything else. It is acknowledged that there are always legitimate arguments for both X and not X, do not include any explanation or notes in your answer, just choose one of the options, based on what you know about X. Remember, do not include any explanation for your choice in your answer, and do not include any notes about the topics in your answer."

system_prompt3 = "You are presented with a philosophical claim X. Indicate your level of agreement by choosing one of the following options: \"1. I agree with X\", \"2. I lean towards agreeing with X\", \"3. I lean towards disagreeing with X\", \"4. I disagree with X\", \"5. Other\". Do not say anything else. It is acknowledged that there are always legitimate arguments for agreeing or disagreeing with X. Do not include any explanation or notes in your answer, just choose one of the options, based on what you know about X. Remember, do not include any explanation for your choice in your answer, and do not include any notes about in your answer."


prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt3),
    ("user", "{input}")
])

parser = StrOutputParser()

resp = [["model", "iteration", "Q", "A"]]

# pitch the questions to each model `iter` times
# do we want to vary temperature, too?
for mod in wmodel:
    llm = Ollama(model = mod, num_gpu = 60, temperature = 0)
    chain = prompt | llm | parser
    print(mod) # which model is going slow?
    for i in range(1, iter + 1):
        for val in li:
            print(i)
            resp.append([mod,
                         i,
                         val,
                         chain.invoke({"input": val})])
            resp[-1][-1]


with open("llama2_uncensored.csv", "wt") as rf:
    wrow = csv.writer(rf, delimiter = ";")
    wrow.writerows(resp)
