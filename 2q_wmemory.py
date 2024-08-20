import os
import sys
# import re
import csv
import time
from langchain_community.llms import Ollama
#from langchain_core.output_parsers import StrOutputParser
#from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferMemory
sp = os.getcwd()
li = []
first = "n"

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



li = read_qs("ctrlqs.txt") # read in the questions

if first == "p":
    li = list(zip(li[::2], li[1::2])) # 'A' first
    ant = ["P", "N"]
    preord = [1,2]
else:
    li = list(zip(li[1::2], li[::2])) # 'B' first
    ant = ["N", "P"]
    preord = [2,1]


# choose models -- bigger models if running on a bigger rig
if os.cpu_count() > 16:
    wmodel = ["llama3:8b-instruct-q4_0",
              "llama3:8b-instruct-q8_0",
              "llama3:70b-instruct-q4_0",
              "llama3:70b-instruct-q8_0",
              "llama2:7b-chat-q4_0",
              "llama2:7b-chat-q8_0",
              "llama2:70b-chat-q4_0",
              "llama2:70b-chat-q8_0",
              "mistral:7b-instruct-v0.3-q4_0",
              "mistral:7b-instruct-v0.3-q8_0",
              "gemma:2b-instruct-v1.1-q4_0",
              "gemma:2b-instruct-v1.1-q8_0",
              "gemma:7b-instruct-v1.1-q4_0",
              "gemma:7b-instruct-v1.1-q8_0"]
else: # laptop
    wmodel = ["gemma"]

iter = 100 # how many iterations per model

# system_prompt3 = "You, the AI, are presented philosophical claims about topic X. Indicate your level of agreement by choosing one of the following options: \"1. I agree with X\", \"2. I lean towards agreeing with X\", \"3. I lean towards disagreeing with X\", \"4. I disagree with X\", \"5. Other\". Do not say anything else. It is acknowledged that there are always legitimate arguments for agreeing or disagreeing with X. Do not include any explanation or notes in your answer, just choose one of the options, based on what you know about X. Remember, do not include any explanation for your choice in your answer, and do not include any notes about in your answer. \n\n Current conversation:\n{history}\n Human: {input} \n\nAI:"

sprompt = "You, the AI, are asked to consider philosophical views. Reply only with one of the following as the first sentence of your answer: \"It is correct\", \"It is partially correct\", \"It is partially incorrect\", \"It is incorrect\", \"Other\". Do not include any explanation for your choice, just choose one of the answer options, based on what you know. Remember, do not include anything else in your answer.\n\n Current conversation:\n{history}\n Human: {input} \n\nAI:"


# prompt = ChatPromptTemplate.from_messages([
#     ("system", system_prompt3),
#     ("user", "{input}")
# ])

# parser = StrOutputParser()

resp = [["model", "iteration", "Q", "A", "temperature", "Question", "Antinomy", "Presentation_Order"]]
temperatures = [0.6, 0.7, 0.8, 0.9, 1.0, 1.5]
for temp in temperatures:
    print("temp is:", temp)
    for mod in wmodel:
        llm = Ollama(model = mod, num_gpu = 60, temperature = temp)
        print(mod) # which model is going slow?
        for i in range(1, iter + 1):
            for qp in range(len(li)):
                print("\r", i, end="")
                conv = ConversationChain(
                    llm=llm,
                    memory=ConversationBufferMemory()
                    )
                conv.prompt.template = sprompt
                for qplus in range(2):
                    resp.append([mod,
                                 i,
                                 li[qp][qplus],
                                 conv(li[qp][qplus])["response"],
                                 temp,
                                 qp,
                                 ant[qplus],
                                 preord[qplus]])

timenow = time.time()
filename = "qtrl_only_nf"+time.strftime("%d%m%Y-%Hh%Mm")+".csv"
with open(filename, "wt") as rf:
    wrow = csv.writer(rf, delimiter = ";")
    wrow.writerows(resp)
