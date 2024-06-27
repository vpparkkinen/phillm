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

li = read_qs("tf_small.txt") # read in the questions

li = list(zip(li[::2], li[1::2]))


# choose models -- bigger models if running on a bigger rig
if os.cpu_count() > 16:
    wmodel = ["llama2-uncensored:7b-chat-q4_0",
              "llama2-uncensored:7b-chat-q5_0",
              "llama2-uncensored:7b-chat-q8_0"]
else: # laptop
    wmodel = ["gemma"]

 # which models to use
iter = 1 # how many iterations per model

system_prompt3 = "You are presented with a philosophical claims about topic X. Indicate your level of agreement by choosing one of the following options: \"1. I agree with X\", \"2. I lean towards agreeing with X\", \"3. I lean towards disagreeing with X\", \"4. I disagree with X\", \"5. Other\". Do not say anything else. It is acknowledged that there are always legitimate arguments for agreeing or disagreeing with X. Do not include any explanation or notes in your answer, just choose one of the options, based on what you know about X. Remember, do not include any explanation for your choice in your answer, and do not include any notes about in your answer. \n\n Current conversation:\n{history}\nHuman: {input}\nAI:"


# prompt = ChatPromptTemplate.from_messages([
#     ("system", system_prompt3),
#     ("user", "{input}")
# ])

# parser = StrOutputParser()





resp = [["model", "iteration", "Q", "A", "temperature"]]
# pitch the questions to each model `iter` times
# do we want to vary temperature, too?
temp = 1
for mod in wmodel:
    llm = Ollama(model = mod, num_gpu = 60, temperature = temp)
    #chain = prompt | llm | parser
    print(mod) # which model is going slow?
    for i in range(1, iter + 1):
        for qp in range(len(li)):
            print(i)
            conv = ConversationChain(
                llm=llm,
                memory=ConversationBufferMemory()
            )
            conv.prompt.template = system_prompt3
            for qplus in range(2):
                print("qp is ", qp, "qplus is ", qplus)
                resp.append([mod,
                             i,
                             li[qp][qplus],
                             conv(li[qp][qplus])["response"],
                             temp])

timenow = time.time()
filename = "2qconv_"+time.strftime("%d/%m/%Y-%H:%M")+".csv"
with open(filename, "wt") as rf:
    wrow = csv.writer(rf, delimiter = ";")
    wrow.writerows(resp)
