import os
import json
import sys

'''
B-tree or binary tree not implemented since they give approximately the same time complexity
The space complexity, implementation, and handling of trees is worse than a sorted list, so they are not used
This works only because the corpus is static. In case of a dynamic corpus, trees provide ease of addtion and deletion
'''

def find(permuterm_list, query): #Function using binary search on sorted list of tokens
	lo, hi = 0, len(permuterm_list)
	while lo<hi: #Finds lower bound, which is the index of the first token that DOES satisfy the query
		mid=lo+(hi-lo)//2
		temp=permuterm_list[mid][:len(query)] 
		'''
		Only considering till length of query term in order to get equality between "$auto" query and "$automa" middle term
		If query term is longer than middle element, it implies that the token won't match the query, so it doesn't need to be considered separately
		String splicing takes care of the case where len(query) > len(middle element)
		'''
		if query <= temp:
			hi=mid
		else:
			lo=mid+1

	start_idx=lo

	lo, hi = 0, len(permuterm_list)
	while lo<hi: # Finds upper bound, which is the first element that DOES NOT satisfy the query
		mid=lo+(hi-lo)//2
		temp=permuterm_list[mid][:len(query)] #Same reasoning as lower bound
		if query >= temp:
			lo=mid+1
		else:
			hi=mid
	end_idx=lo

	return permuterm_list[start_idx:end_idx] #All elements between the two indices satisfy the query

posting_list={}
permuterm_list=[]

with open(os.path.join(os.getcwd(), 'posting_list.json'), 'r') as post_list:
	posting_list=json.load(post_list) #Loading the posting list generated in task 3

with open(os.path.join(os.getcwd(), 'permu_dict.txt'), 'r') as dictionary:
	permuterm_list = dictionary.readline().split() #Loading the sorted token list to use as a dictionary

with open(os.path.join(os.getcwd(), str(sys.argv[1]).strip()), 'r') as query_list: #reading the queries from the input file
	with open(os.path.join(os.getcwd(), "RESULTS1_18EC10020.txt"), 'w') as answer_file: #opening result file to write answers for each query as soon as they are obtained
		queries=query_list.readlines() # Gets all the queries and puts them in a list
		#print(queries)
		for query in queries:
			if query.find('\n')!=-1:
				query=query[:query.find('\n')] #removing newline at the end of input if it exists
			if query == "":
				continue
			idx=query.find('*')
			actual_query=query[idx+1:]+"$"+query[:idx] #creating necessary permuterm to search in the term dictionary
			match_list=find(permuterm_list, actual_query) # List of terms satisfying the query
			answer=""

			for match in match_list:
				idx1=match.find('$')
				word=match[idx1+1:]+match[:idx1] #Getting the original word from its permuterm

				# Adding matches from posting list to the answer
				answer+=word+": "
				for key in posting_list[word].keys():
					for elem in posting_list[word][key]:
						answer+="<{0}, {1}>".format(key, elem)+','
				answer+='; ' #separating matches by semi-colon
			
			#Writing the answer for each query, separated by newline
			answer_file.write(answer+"\n")
