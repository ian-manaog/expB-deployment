'''
    | PREPROCESSING MODULE 
    |====================================
    | Project SenTagalog
'''
import os
import re
import pickle

def load_pickle(file):   
    data = open(file, "rb")
    return pickle.load(data)

######################
# PREPROCESSOR CLASS #
###################### 
class Preprocessor: 
    def __init__(self, project=None, **kwargs):

        self.verbose = kwargs.get("verbose", False) 
        self.project = project
        
        self.params = {
            "remove_links" : True,
            "remove_emojis" : True, 
            "remove_usernames" : True, 
            "remove_hashtags" : True, 
            "remove_pos_keywords" : True, 
            "remove_punctuations" : True, 
            "remove_non_word_characters" : True, 
            "remove_numbers" : True, 
            "lowercase_text" : True,
            "word_non_word_character_separation" : True, 
            "word_contraction_expansion" : True
        }

        # bindings (in order)
        self.bindings = {
            "remove_links" : self.remove_links, 
            "remove_emojis" : self.remove_emojis, 
            "remove_usernames" : self.remove_usernames,
            "remove_hashtags" : self.remove_hashtags, 
            "remove_pos_keywords" : self.remove_pos_keywords,
            "remove_punctuations" : self.remove_punctuations, 
            "remove_non_word_characters" : self.remove_non_word_chars,
            "remove_numbers" : self.remove_numbers, 
            "lowercase_text" : self.lowercase_text, 
            "word_non_word_character_separation" : self.word_non_word_char_sep, 
            "word_contraction_expansion" : self.word_contraction_expansion, 
            "next_word_negation": self.apply_next_word_negation
        }


        # preprocessing flow 
        self.flow = [
            "lowercase_text", 
            "remove_links", 
            "remove_emojis", 
            "remove_usernames", 
            "remove_numbers",
            "remove_hashtags", 
            "remove_punctuations",
            "word_contraction_expansion", 
            "word_non_word_character_separation", 
            "next_word_negation",
            "remove_pos_keywords"
        ]

        # word characters 
        self.word_chars = [
            "a", "b", "c", "d", "e", 
            "f", "g", "h", "i", "j", 
            "k", "l", "m", "n", "o", 
            "p", "q", "r", "s", "t", 
            "u", "v", "w", "x", "y", 
            "z", "0", "1", "2", "3", 
            "4", "5", "6", "7", "8",
            "9", "-"
        ]

        # negators 
        self.negators = [
            "no", "not", 
            "hindi", "di"
        ]
        
        # stem cache 
        file = "helpers/resources/cache/stem_cache.pickle"
        if os.path.isfile(file):
            self.stem_cache = load_pickle(file)
        else: 
            self.stem_cache = {
                "en": {}, 
                "tl": {}
            }

        self.high_logging = True

    def remove_links(self, text): 
        text = text[:]
        text = re.sub(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', "", text)

        return text
    
    def remove_emojis(self, text): 
        text = text[:]
        emojis = self.project.resources["emojis"]["all"] 
        for emoji in emojis:
            text = text.replace(emoji, "") 

        return text

    def remove_usernames(self, text): 
        text = text[:]
        text = re.sub("@[a-zA-Z0-9_]+", "", text)
        return text
    
    def remove_hashtags(self, text): 
        text = text[:]
        text = re.sub("#[a-zA-Z0-9_]+", "", text)
        return text

    def remove_pos_keywords(self, text): 
        text = text[:]
        text = text.replace("’", "'")
        tokens = text.split(" ")
        pos_keywords = self.project.resources["pos_keywords"]
        ntokens = []
        for token in tokens: 
            if token not in pos_keywords["en"] and token not in pos_keywords["tl"]: 
                ntokens.append(token)
        return " ".join(ntokens) 
        
    def remove_punctuations(self, text): 
        text = text[:]
        puncs = self.project.resources["punctuations"]
        
        text = text.replace("’", "'")

        if "#" in puncs:
            puncs.remove("#")
        for punc in puncs:
            if punc != "'":
                text = text.replace(punc, "")

        return text
    
    def remove_numbers(self, text): 
        text = text[:]
        text = re.sub(r'''[0-9]+''', "", text) 
        return text

    def remove_non_word_chars(self, text): 
        text = text[:]
        ntext = ""
        for i in range(len(text)): 
            char = text[i]
            if char not in self.word_chars: 
                ntext += char 
        return ntext
            
    def lowercase_text(self, text):
        text = text[:]
        text = text.lower()
        return text

    def word_non_word_char_sep(self, text): 
        text = text[:]
        ntext = ""
        for i in range(len(text)):
            char = text[i] 
            if char not in self.word_chars and char != " ": 
                ntext += " " + char + " " 
            else: 
                ntext += char
        return ntext
    
    def word_contraction_expansion(self, text):
        tokens = text.split(" ")
        ntokens = [] 
        contractions = self.project.resources["contractions"]
        for i in range(len(tokens)): 
            token = tokens[i]
            expanded = False
            for lang in contractions:
                if token in contractions[lang] and not expanded: 
                    ntokens.append(contractions[lang][token])
                    expanded = True 
            if expanded == False: 
                ntokens.append(token)
        text = " ".join(ntokens)
        text = text.replace("'s", "")
        return text
    


    def apply_next_word_negation(self, text): 
        tokens = text.split(" ")
        ntokens = [] 
        puncs = self.project.resources["punctuations"]
        i = 0
        while i < len(tokens): 
            token = tokens[i]
            if token in self.negators: 
                if i < len(tokens) - 1:
                    if tokens[i+1] not in puncs:
                        ntokens.append("NOT~" + tokens[i + 1])
                        i += 2
                    else: 
                        ntokens.append(token)
                        i += 1
                else: 
                    i += 1
            else: 
                ntokens.append(token)
                i += 1
        return " ".join(ntokens)



    def tokenize_text(self, text): 
        return text.split(" ") 

    def dump_sc(self): 
        stem_cache = open("helpers/resources/cache/stem_cache.pickle", "wb") 
        pickle.dump(self.stem_cache, stem_cache)
        stem_cache.close()


    # ========= PREPROCESSING FUNCTION         ========== #
    
    # Preprocess Function (for Single Text)
    # Parameters 
    def preprocess(self, text, **kwargs): 
        text_ = text 

        # preprocessing flow 
        flow = self.flow 

        # loop through the flow and check if preprocessing step 
        # is applied
        for step in flow: 
            if self.is_enabled(step): 
                text_ = self.get_func(step)(text_)

        self.dump_sc()

        return re.sub("\s+", " ", text_)
          
    # Preprocess an array of text step by step
    def bulk_preprocess(self, texts): 
        if self.verbose: 
            print("Preprocessing Texts...")
        ntexts = texts[0:]         
        # preprocessing flow 
        flow = self.flow 
        
        # loop through the flow and check if preprocessing step 
        # is applied 
        for i in range(len(flow)):
            step = flow[i]  
            if self.is_enabled(step): 
                if self.verbose: 
                    print("Applying preprocessing step (" + str(i + 1) + "/" + str(len(flow)) + "): " + step)
                for j in range(len(ntexts)):
                    if self.verbose and self.high_logging:
                        print("Preprocessing text " + str(j + 1) + " of " + str(len(ntexts)), end="\r")
                    step_func = self.get_func(step)
                    ntext = str(ntexts[j]) 
                    ntexts[j] = step_func(ntext)  
        
        for i in range(len(ntexts)): 
            ntexts[i] = re.sub(r' +', ' ', str(ntexts[i])).strip()

        self.dump_sc()
        if self.verbose:
            print("\n")
        return ntexts               
    
    def transform(self, texts): 
        return self.bulk_preprocess(texts)

    # get the function for a preprocessing step
    def get_func(self, step):
        return self.bindings[step]
    
    # check if a preprocessing step is enabled 
    def is_enabled(self, step): 
        return self.params[step]

    # activates all preprocessing steps
    def activate_all(self): 
        for binding in self.bindings: 
            self.params[binding] = True 
    
    # deactivates all preprocessing steps
    def deactivate_all(self): 
        for binding in self.bindings: 
            self.params[binding] = False  

    # activate a certain preprocessing step 
    def activate(self, step): 
        self.params[step] = True

    # deactivates a certain preprocessing step 
    def deactivate(self, step): 
        self.params[step] = False 
