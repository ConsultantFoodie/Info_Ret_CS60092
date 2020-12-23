import os
import re
import json
from bs4 import BeautifulSoup as bs

val=0 #Global variable to map files from 0 to N-1

def extract_date(date_string): # Using Regex to extract date from input string
	date_pattern = r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})\,?\s+(\d{4})'
	date = re.search(date_pattern, date_string)
	return date.group(0)

def extract_participants(para_list): #Function to extract participants
	strong_tag_cnt = 0
	participant_list = []
	para_cnt = 0

	for para in para_list:
		if para.find("strong"):
			strong_tag_cnt += 1 # Keeping count of <strong> tags. General part is that the list of participants lies between the first and third <strong> tags
		elif strong_tag_cnt > 0 and strong_tag_cnt <= 2:
			participant_list.append(para.text)

		if strong_tag_cnt > 2: # After the third <strong> tag, list of participants will be over
			break

		para_cnt += 1 # Keeping count of <p> tags to resume search for presentation content from this point

	return participant_list, para_cnt

def extract_presentation(para_list, para_cnt): #Function to extract presentation content as a dict
	presentation_dict = {}
	para_cnt_new = para_cnt # Again counting <p> tags to return next search point

	key=""
	# Possible string that mark the beginning of Q and A session in absence of tag id
	break_list = ["Question-and-Answer Session", "Question-And-Answer Session", "Question-and-Answers Session", "Question-And-Answers Session", "Questions-and-Answer Session", "Question-and Answer Session"]

	for para in para_list:
		if para.has_attr('id') and para.get('id') == 'question-answer-session': # This marks the start of the questionnaire
			break

		if para.text.strip() in break_list: # If tag id is missing, these are the possible alternatives to find the start of questionnaire, i.e. end of presentation
			break

		if para.find("strong"): # For presentation, each strong tag marks a speaker
			key = para.text
		else:
			if key not in presentation_dict.keys(): #Adding speaker if not present
				presentation_dict[key] = []

			presentation_dict[key].append(para.text) #Adding speaker statement to list of strings

		para_cnt_new += 1

	return presentation_dict, para_cnt_new

def extract_q_a(para_list): # Function to extract questionnaire
	q_a_dict={}
	statement_cnt=1
	statement_dict={}
	key=""

	for para in para_list:
		if para.find("strong"): # <strong> tags mark speakers
			key = para.text
			if "Speaker" in statement_dict.keys():
				q_a_dict[str(statement_cnt)]=statement_dict.copy() # Adding a copy since the same dict is being reused in the loop
				statement_cnt += 1 # Without .copy() any change in statement_dict will also appear in q_a_dict
				statement_dict.clear() # Clearing dict for new speaker

			statement_dict["Speaker"] = key
			statement_dict["Remarks"] = []
		elif key != "":
			statement_dict["Remarks"].append(para.text) #Adding speaker statement to list of strings


	q_a_dict[str(statement_cnt)]=statement_dict.copy() #Corner case for final speaker, since the statement_dict is added only when a new speaker is encountered
	return q_a_dict

global_dict={} #Global Dict for storing mapping of actual file name to an integer from 0 to N-1


try: # Creating a new folder to store nested dicts
	os.mkdir(os.path.join(os.getcwd(), "ECTNestedDict"))
except:
	pass #No handling needed if the folder already exists


# Assumes all files are already present in ECT directory which is in the same folder as all the four programs. Scraper scrapes limited files only as mentioned.
# Please ensure that all the html files are present in the ECT directory. All intermediate files and directories will be made in the current working directory.
for filename in os.listdir(os.path.join(os.getcwd(), "ECT")):
	temp_dict = {}
	global_dict[val]=filename # Adding mapping of filename to integer

	with open(os.path.join(os.getcwd(), "ECT", filename), 'r') as f:
		soup=bs(f, 'html.parser')
		content = soup.find("div", attrs={'id':'a-body'})
		para_list = content.find_all("p") # Getting all <p> tags since the html file as all data inside <p> tags
		date_string = ""
		for elem in para_list[:5]: # Taking first 5 paragraphs to find date since some transcripts don't have the date in the first paragraph
			date_string+=elem.text + " " # Generating string to search in uing RegEx


		# Calling all relevant functions and building dictionary for each transcript
		temp_dict["Date"] = extract_date(date_string)

		participant_list, para_cnt = extract_participants(para_list)
		temp_dict["Participants"] = participant_list

		presentation_dict, para_cnt = extract_presentation(para_list[para_cnt:], para_cnt)
		temp_dict["Presentation"] = presentation_dict

		temp_dict["Questionnaire"] = extract_q_a(para_list[para_cnt+1:])


	with open(os.path.join(os.getcwd(), "ECTNestedDict", "Dict_"+str(val)+".json"), 'w') as json_file:
		json.dump(temp_dict, json_file)

	val += 1 # Incrementing variable used to map filenames


with open(os.path.join(os.getcwd(), "Keys2Names.json"), 'w') as keys_file:
	json.dump(global_dict, keys_file) #This file contains the mapping of the integer to the original file name in "ECT" folder for future reference

try: # Creating an ECTText file to store all the text data from the nested dicts.
	os.mkdir(os.path.join(os.getcwd(), "ECTText")) # Keys like "Date", "Participants", "Presentation", "Questionnaire" not included
except: 
	pass #No handling needed if folder exists

for filename in os.listdir(os.path.join(os.getcwd(), "ECTNestedDict")):
	with open(os.path.join(os.getcwd(), "ECTNestedDict", filename), 'r') as file: # Reading the nested dict for each file to create ECTText
		number = filename.split('.json')[0].split('_')[1] # Extracting file number to maintain the original mapping
		nested_dict = json.load(file)

		with open(os.path.join(os.getcwd(), "ECTText", "Text_"+number+".txt"), 'w') as write_file:
			#For each key, checking if it exists as a precaution. There exist files without Questionnaire, so this prevents any runtime errors
			if "Date" in nested_dict.keys():
				write_file.write(nested_dict["Date"] + " ")

			if "Participants" in nested_dict.keys():
				for participant in nested_dict["Participants"]:
					write_file.write(participant + " ")

			if "Presentation" in nested_dict.keys():
				for key in nested_dict["Presentation"].keys():
					write_file.write(key + " ")
					for line in nested_dict["Presentation"][key]:
						write_file.write(line + " ")

			if "Questionnaire" in nested_dict.keys():
				for key in nested_dict["Questionnaire"].keys():
					write_file.write(key + " ")
					if "Remarks" in nested_dict["Questionnaire"][key].keys(): # Precaution if "Remarks" does not exist
						for line in nested_dict["Questionnaire"][key]["Remarks"]:
							write_file.write(line + " ")

		#print("Done with "+number) # Output to keep track of file being processed. Enable if necessary
	