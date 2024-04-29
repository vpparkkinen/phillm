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
    wmodel = ["llama3", "mistral:7b-text-q8_0", "gemma"]
else: # laptop
    wmodel = ["llama3", "gemma"]

 # which models to use
iter = 1 # how many iterations per model

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are being surveyed about your opinions towards statements concerning philosophical issues such as the mind-body problem, the trolley problem, or the ethics of abortion. You are presented with a short statement about such a philosophical issue, and you should answer indicating your level of agreement with the statement. Start your answer by stating your level of agreement with the presented statement by choosing one of the following: \"I agree\", \"I lean towards areeing\", \"I disagree\", \"I lean towards disagreeing\". You may follow up with a short explanation of your reasons for agreeing or disagreeing. It is acknowledged that there often is no single correct answer. "),
    ("user", "{input}")
])

parser = StrOutputParser()

resp = [["model", "iteration", "Q", "A"]]

# pitch the questions to each model `iter` times
# do we want to vary temperature, too?
for mod in wmodel:
    llm = Ollama(model = mod)
    chain = prompt | llm | parser
    for i in range(1, iter + 1):
        for val in li:
            resp.append([mod,
                         i,
                         val,
                         chain.invoke({"input": val})])


with open("res.csv", "wt") as rf:
    wrow = csv.writer(rf, delimiter = ";")
    wrow.writerows(resp)
