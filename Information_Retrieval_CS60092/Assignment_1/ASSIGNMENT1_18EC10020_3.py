import os
import string
import nltk
import json
from nltk.tokenize import SpaceTokenizer 
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet, stopwords

# Downloading nltk requirements in case they don't exist in the environment
nltk.download('wordnet')
nltk.download('stopwords')

#Creating Lemmatizer and Tokenizer objects. Space tokenizer used.
lemmatizer = WordNetLemmatizer()
tk = SpaceTokenizer() 

# Getting set of stopwords in English
stop_words = set(stopwords.words('english'))

try: #Creating folder for intermediate files which are the ECTText files after removing punctuation and stopwords, and performing lemmatization
	os.mkdir(os.path.join(os.getcwd(), "ECTLemma"))
except:
	pass #No handling needed if directory exists

var=0 #In order to count the number of files already processed.
posting_list={}

def isValid(word): # Function to check if the string has non-alphabet characters. Input will be in lowercase.
	for letter in word:
		if letter<'a' or letter>'z':
			return False
	return True

# FILE POSITIONS WILL MATCH WITH FILES IN ECTTEXT, NOT ECTLEMMA. POSITIONS CALCULATED PRIOR TO STOP WORD REMOVAL, BUT AFTER REMOVING PUNCTUATIONS AS MENTIONED

for filename in os.listdir(os.path.join(os.getcwd(), "ECTText")):
	with open(os.path.join(os.getcwd(), "ECTText", filename), 'r') as f:
		file=f.readline() # Since the text was space-separated, it counts as a single line
		translation_table = dict((ord(char), None) for char in string.punctuation) # Mapping all punctuation characters to None for removal
		translation_table[ord('-')]=' ' # Only hyphenated words will be separated.
		translation_table[ord('–')]=None
		file=file.translate(translation_table) # Using string functions to replace all punctuation with None according to translate table

		word_list=[] #For making lemmatized text file without stopwords and punctuation
		file_number=int(filename.split(".txt")[0].split("_")[1])

		pos_in_doc = 0 # Zero indexing for position within document
		for word in tk.tokenize(file): # Tokenzing
			#Case folding in order to reduce number of keys. May lead to lack of context from words such as SAIL and sail, BEST and best. But context not necessary for assignment
			word = word.lower()

			if word != "" and isValid(word): #Only counting non-empty strings with english alphabets
				if word not in stop_words: # Not counting stop words
					lemma_word = lemmatizer.lemmatize(word) #Lemmatization assuming default part of speech (Noun) in order to improve runtime as requested for ease of grading
					word_list.append(lemma_word)
					# Dict structure is <DOC ID> : [LIST OF POSITIONS] in interest of saving space. <DOC_ID, POSITION> for each position will be costly in space for frequent words
					if lemma_word not in posting_list.keys(): #Adding word in dict if not present
						posting_list[lemma_word]={}
					if file_number not in posting_list[lemma_word].keys(): #Adding doc number if first appearance of word
						posting_list[lemma_word][file_number]=[]
					posting_list[lemma_word][file_number].append(pos_in_doc) #Adding position
			if word!="":
				pos_in_doc += 1 #Incrementing position for every word, stop words included to match position with ECTText and not ECTLemma


		with open(os.path.join(os.getcwd(), "ECTLemma", "Lemma_"+str(file_number)+".txt"), 'w') as lemma_file:
			lemma_file.write(" ".join(word_list)) #Storing Lemma file for confirming stopword, punctuation removal and lemmatization for grading. Not really needed for code to work

		# Uncomment if need to confirm whether code is running or not
		# print("Done with {0}".format(var))
		# var+=1


with open(os.path.join(os.getcwd(), 'posting_list.json'), 'w') as work:
	json.dump(posting_list, work) # Saving posting list in .json for use in Task 4.


dictionary=[] #creating dictionary of words with permuterms
for key in posting_list.keys():
	permu_key = key + "$" # Adding a marker
	for num in range(1,len(permu_key)+1): #creating permuterms using string splicing 
		permuterm=permu_key[num:]+permu_key[:num]
		dictionary.append(permuterm)

dictionary.sort() # Sorting using the normal string comparison function by default, since we need lexicographical sorting

with open(os.path.join(os.getcwd(), 'permu_dict.txt'), 'w') as dict_file:
	dict_file.write(" ".join(dictionary)) #Storing sorted permuterm dict
		