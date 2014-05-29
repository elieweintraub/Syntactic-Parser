#Elie Weintraub 
#ECE 467: Natural Language Processing
#
#CKY_driver.py - A syntactic parser program that uses the CKY library

from CKY import *
from nltk.tree import *
from nltk.draw import tree

#################################### Helper Functions #############################################
def printAndWrite(str,fileObj):
	""" Prints string to stdout and writes it to file specified by fileObj (appending a '\n') """
	print str
	fileObj.write(str+'\n')
	

################################### Driver Program #################################################

print 'welcome to the syntactic parser program:'
print '-------------------------------------------'

#Get user input
input_filename = raw_input('Please specify the file containing the sentence or sentences to parse : ')

grammar_filename = raw_input('Please specify the file containing the CFG : ')

convert = input('Is the CFG already in flexible or strict Chomsky Normal Form (0) or does the grammar need to be converted to flexible CNF (1) : ')
if convert:
	CNF_grammar_filename = raw_input('Please specify the name for the file containing the CFG converted to flexible CNF: ')

output_filename = raw_input('Please specify the name for the file containing the parsed sentence or sentences: ')

display = input('Do you want to see the parses displayed on the screen (1) or not (0): ' )

print

#Create Parser and Grammar Objects
parser = Parser()
g = Grammar(grammar_filename);
if convert:
	g_original = g
	g = g_original.convertToFlexibleCNF(CNF_grammar_filename)

#Main routine	
with open(output_filename,'w') as out:
	with open(input_filename,'r') as sentences:
		for sentence in sentences:		
			#Parse sentence
			sentence = sentence.strip()
			printAndWrite('Parsing sentence: '+sentence, out)
			trees, output_str, _ = parser.CKYParse(sentence,g)
			out.write(output_str+'\n')
			#Convert back to original form (if applicable)
			if convert:
				trees = [tree.unchomsky(g_original) for tree in trees]
			#Write trees to file
			for i,tree in enumerate(trees):
				t = tree.returnTree()
				out.write(str(i+1)+') '+t+'\n')
			#Print trees to screen 
			if trees and display:
				print '\nIf there are multiple parses they will now be displayed sequentially in a window.'
				print "DON'T FORGET TO CLOSE OUT EACH WINDOW IN ORDER TO PROCEED!\n"
				for i,tree in enumerate(trees):	
					t = tree.returnTree()
					Tree(t).draw()
					if i<len(trees)-1:
						another = input('Do you want to see another parse (1) or not (0): ' )
						if another:
							continue
						else:
							break
							
			printAndWrite('', out)
			
print "Thank you for using the Syntactic Parser Program!"				
			
		