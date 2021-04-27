'''
    | PROJECT MODULE 
    |====================================
    | Project SenTagalog
'''

from string import punctuation
import json 
import pandas as pd 
import pickle 
import re 

LOW_MEMORY = False

#################
# PROJECT CLASS #
################# 

class Project: 
    def __init__(self, **kwargs): 
        self.verbose = kwargs.get("verbose", False) 

        # resources inventory
        self.sources = {
            "contractions" : {
                "tl" : "helpers/resources/contract-tl.json", 
                "en" : "helpers/resources/contract-en.json"
            }, 
            "emojis" : {
                "all"            : "helpers/resources/emojis-all.txt"
            }, 
            "pos_keywords" : {
                "tl"             : "helpers/resources/pos-tl.txt", 
                "en"             : "helpers/resources/pos-en.txt"
            }
        } 

        # resource objects container 
        self.resources = {
            "punctuations" : list(punctuation)
        }

    #####################################
    # RESOURCE LOADING AND PREPARATIONS #
    ##################################### 

    # loads and prepare listed resources in the resources inventory
    def bootstrap(self):
        for resource in self.sources: 
            components = self.sources[resource] 
            if resource not in self.resources: 
                self.resources[resource] = {} 
            for component in components: 
                component_file = components[component] 
                #print(component_file)
                self.resources[resource][component] = \
                    self.get_from_file(component_file) 
    
    # load resource contents from file (automatically 
    # identify file type through extension) 
    def get_from_file(self, file): 
        filename_toks = file.split(".")
        ext = filename_toks[-1] 

        # if a json file, process through the JSON library 
        if ext == "json": 
            content = open(file, encoding='utf8').read() 
            data = json.loads(content) 
            return data

        # if a text file, split file contents line by line 
        # and return as array 
        elif ext == "txt": 
            content = open(file, encoding='utf8').read() 
            data = content.split("\n")
            return data 

        # if a csv file, use the Python pandas library to load 
        # the file and return a dataframe object 
        elif ext == "csv": 
            return pd.read_csv(file, low_memory=LOW_MEMORY)

    # hashes resources for faster accessing 
    def hash_resources(self): 
        wordlists = {} 
        emojis = {} 

        
        # hash emojis 
        for set in self.resources["emojis"]: 
            emojis[set] = {} 
            for emoji in self.resources["emojis"][set]:
                emojis[set][emoji] = True

        self.resources["emojis"] = emojis
