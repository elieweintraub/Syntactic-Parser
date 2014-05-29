#Elie Weintraub 
#ECE 467: Natural Language Processing
#
#CKY.py - A library defining classes for a syntactic parser that uses the CKY algorithm

import nltk,itertools,copy

class Tree:
	""" A class to represent a parse tree """
	def __init__(self,node_value):
		""" Initializes the parse tree"""
		self._node_value = node_value
		self._children = []
			
	def node_value(self):
		""" Returns the node value of the current node """
		return self._node_value
			
	def children(self):
		""" Returns the children of the current node as a list """
		return self._children
	
	def unchomsky (self, original_grammar):
		""" Returns a new tree using the original form of the grammar 
			Wrapper to the _unchomsky() method that first makes a deep copy """
			
		newTree = copy.deepcopy(self)
		newTree._unchomsky(original_grammar)
		return newTree
		
	def _unchomsky(self, original_grammar):
		""" Helper for the unchomsky() method """
		#Promote children nodes of introduced symbols
		old_len = len(self._children)
		new_len = None
		while(new_len != old_len):
			old_len = len(self._children)
			for i,child in enumerate(self._children):
				if child._node_value not in original_grammar.symbols():
					self._children.pop(i)
					self._children[i:i] = child._children
			new_len = len(self._children)
		
		#Recursively call _unchomsky() on each child
		for child in self._children:
			child._unchomsky(original_grammar)
		
	def printTree(self):
		""" Prints the parse tree
			Wrapper to the _printTree() method that adds a newline to the end """
		self._printTree()
		print 
		
	def _printTree(self):
		""" Helper to the printTree() method """
		print '( '+self._node_value,
		for child in self._children:
			if child._children == []:
				print child._node_value,
			else:
				child._printTree()
		print ')',	
	
	def returnTree(self):
		""" Returns  a string representation of the parse tree 
		    Wrapper to the _returnTree() method  that enforces equal spacing """
		return ' '.join(self._returnTree().split())
	
	def _returnTree(self):
		""" Helper to the returnTree() method """
		tree = '( ' + self._node_value
		for child in self._children:
			if child._children == []:
				tree += ' ' + child._node_value + ' '
			else:
				tree += ' ' + child._returnTree()
		tree += ') '
		return tree
		
class Production:
	""" A class that stores and allows access to the lhs and rhs of a given production"""
	def __init__(self,lhs,rhs):
		""" Initializes data members of the production """
		self._lhs = lhs
		self._rhs = rhs
		
	def __str__(self):
		""" Returns string representation of the production """
		return ' -> '.join([self._lhs,self._rhs])
	
	def __repr__(self):
		""" Returns string representation of the production """
		return ' -> '.join([self._lhs,self._rhs])

	def lhs(self):
		""" Returns the left-hand side of the production """
		return self._lhs
	
	def rhs(self):
		""" Returns the right-hand side of the production """
		return self._rhs
		
class Grammar:
	""" A class that represents a CFG """
	def __init__(self,filename):
		""" Initializes data members of the CFG """
		self._start_symbol,self._productions = self._loadCFG(filename)
		self._lhs_index,self._rhs_index = self._calcIndexes()
		self._terminals,self._nonterminals,self._symbols = self._calcSymbols()
	
	def __str__(self):
		""" Returns string representation of the grammar """
		return 'CFG with '+str(len(self._productions))+' productions'
	
	def __repr__(self):
		""" Returns string representation of the grammar """
		return 'CFG with '+str(len(self._productions))+' productions'
	
	def start_symbol(self):
		""" Returns the start symbol of the grammar """
		return self._start_symbol
		
	def productions(self):
		""" Returns the productions of the grammar as a list """
		return self._productions

	def terminals(self):
		""" Returns the terminal symbols of the grammar as a set """
		return self._terminals			
	
	def nonterminals(self):
		""" Returns the nonterminal symbols of the grammar as a set """
		return self._nonterminals	
	
	def symbols(self):
		""" Returns the symbols of the grammar as a set """
		return self._symbols
		
	def isTerminal(self,symbol):
		""" Returns true if the given symbol is a terminal symbol """
		return symbol in self._rhs_index and symbol not in self._lhs_index
	
	def isNonterminal(self,symbol):
		""" Returns true if the given symbol is a nonterminal symbol """
		return symbol in self._lhs_index	
	
	def getProdsByRhs(self,rhs):
		""" Returns a list of productions from the grammar's production list filtered by the rhs"""
		return self._rhs_index.get(rhs,[])
		
	def getProdsByLhs(self,lhs):
		""" Returns a list of productions from the grammar's production list filtered by the lhs"""
		return self._lhs_index.get(lhs,[])
	
	def convertToFlexibleCNF(self,filename):
		""" Returns a new grammar object that is the original CFG converted to flexible CNF """
		with open(filename,'w') as CFG:
			# Define start symbol
			CFG.write('%start ' + self._start_symbol + '\n')
			
			# Write all productions, transforming productions as necessary so that all productions have the form  A -> B, A -> b, or A ->B C
			productions_set = set()  # used to ensure no duplicate productions are produced in the conversion process
			productions = []
			for p in self._productions:
				rhs = p.rhs().split()
				lhs = p.lhs()
				if len(rhs) >= 2:
					# Convert terminals within productions to dummy nonterminals
					terminals = [(symbol,n) for (symbol,n) in enumerate(rhs) if self.isTerminal(symbol)]
					for (terminal,n) in terminals:
						dummy = terminal.strip('"') if not self.isNonterminal(terminal.strip('"')) else 'DUMMY_'+terminal
						production = dummy + ' -> ' + rhs[n] + '\n' 
						if production not in productions_set:
							productions_set.add(production)
							productions.append(production)
						rhs[n] = dummy
						
					# Binarize productions(if production is already binary this block will simply add the production unchanged)	
					for i in range(len(rhs)-1):
						combined ='+'.join(rhs[:-1])
						new_rhs = [combined, rhs[-1]]
						production = lhs + ' -> ' + ' '.join(new_rhs) + '\n'
						if production not in productions_set:
							productions_set.add(production)
							productions.append(production)
						lhs = combined	
						rhs = rhs[:-1]
				else:
					# len(rhs) == 1: Copy production directly  
					production = p.lhs() + ' -> ' + p.rhs() + '\n'
					if production not in productions_set: # this should ALWAYS be true if original grammar doesn't contain duplicates
						productions_set.add(production)
						productions.append(production)
			
			for production in productions:
				CFG.write(production)
			
		#Construct the new grammar object and return it
		CNF = Grammar(filename)

		return CNF	
		
	def _loadCFG(self,filename):
		""" Reads in a CFG text-file returning the start symbol and list of productions """
		start_symbol = None
		productions = []
		productions_set = set() # used to ensure no duplicate productions are included
		with open(filename,'r') as CFG:
			for line in CFG:
				symbols = line.split()
				if len(symbols)>0:
					# Comments
					if symbols[0][0] == '#':
						pass
						
					# Start symbol
					elif symbols[0] == '%start':
						if len(symbols) < 2:
							raise Exception('Incorrect formating!')
						else: 
							start_symbol = symbols[1]	
					
					#Productions
					elif len(symbols) < 3 or symbols[1] != '->':
						raise Exception('Incorrect formating!')	
					else:
						lhs = symbols[0]
						rhs_list = " ".join(symbols[2:]).split('|')
						for rhs in rhs_list:
							production = Production(lhs,rhs.strip())
							if production not in productions_set: 
								productions_set.add(production)
								productions.append(production)
							
		#Default start_symbol to lhs of first production if no %start in file 
		if start_symbol == None:
			start_symbol = productions[0].lhs()
		
		#Return list of productions and start_symbol
		return start_symbol, productions
			
	def _calcIndexes(self):
		""" Given a list of productions creates two mappings of productions: one keyed by the lhs and the other keyed by the rhs """
		lhs_index = {}
		rhs_index = {}
		for p in self._productions:
			lhs_index.setdefault(p.lhs(),[]).append(p)
			rhs_index.setdefault(p.rhs(),[]).append(p)
		return lhs_index,rhs_index
	
	def _calcSymbols(self):
		""" Given a list of productions creates three sets: one of terminal symbols, one of nonterminal symbols, and one with both """
		terminals = set()
		nonterminals = set()
		symbols = set()
		for p in self._productions:
			nonterminals.add(p.lhs())
			terminals=terminals.union({symbol for symbol in p.rhs().split() if self.isTerminal(symbol)})
		symbols = terminals.union(nonterminals)
		return terminals,nonterminals,symbols
		
class Parser:
	"""A class that supports various parsing and recognizing related functions and utilities """		
	def CKYRecognize(self,sentence,grammar):
		""" A recognizer that uses the CKY algorithm.
			Note: This version accepts CFGs in strict Chomsky Normal Form or weak Chomsky Normal Form
			Returns: (output_str, table)                                                              """
		#Split sentence into tokens 
		tokens = sentence.split()
		n_tokens = len(tokens)
		
		#Initialize bottom-up dynamic programming table
		table = [[set() for j in range(n_tokens+1)] for i in range(n_tokens+1)]
		
		#Base case: Fill table with the preterminals of each of the terminal symbols in the given sentence
		#This fills in the superdiagonal (i.e. the diagonal above the main diagonal)
		for j in range(n_tokens):
			token='"'+tokens[j]+'"'
			if not grammar.isTerminal(token):
				output_str = 'The sentence, "' +sentence+'", is not accepted by the given grammar since the token, '+token+', is not part of the lexicon!'
				print output_str
				return (output_str, table)
			table[j][j+1] = {p.lhs() for p in grammar.getProdsByRhs(token)}
		
		#Fill the rest of the table using a bottom up approach
		for j in range(1,n_tokens+1):
			for i in range(j-1,-1,-1):
				#Check for binary productions 
				for k in range(i+1,j):
					for  B,C in itertools.product(table[i][k],table[k][j]):
						rhs = ' '.join([B,C])
						table[i][j] = table[i][j].union( { p.lhs() for p in grammar.getProdsByRhs(rhs) } )
				#Check for unit productions (extension to base algorithm)
				for rhs in table[i][j]:
					table[i][j] = table[i][j].union( { p.lhs() for p in grammar.getProdsByRhs(rhs) } )
		#Check if sentence is recognized
		if grammar.start_symbol() not in table[0][n_tokens]:
			output_str = 'The sentence, "' +sentence+'", is not accepted by the given grammar!'
		else:
			output_str = 'The sentence, "' +sentence+'", is accepted by the given grammar!'
		print output_str
		return (output_str, table)
		
	def CKYParse(self,sentence,grammar):
		""" A parser that uses a version of the CKY algorithm extended with back-pointers.
			Note: This version accepts CFGs in strict Chomsky Normal Form or weak Chomsky Normal Form
			Returns: (trees, output_str, table)                                                       """
		trees = []
		
		#Split sentence into tokens 
		tokens = sentence.split()
		n_tokens = len(tokens)

		#Initialize bottom-up dynamic programming table
		table = [[[] for j in range(n_tokens+1)] for i in range(n_tokens+1)]

		#Base case: Fill table with the preterminals of each of the terminal symbols in the given sentence
		#This fills in the superdiagonal (i.e. the diagonal above the main diagonal) 
		#Also fill the first column with the tokens, themselves
		for j in range(n_tokens):
			token='"'+tokens[j]+'"'
			if not grammar.isTerminal(token):
				output_str = 'The sentence, "' +sentence+'", is not accepted by the given grammar since the token, '+token+', is not part of the lexicon!'
				print output_str
				return (trees, output_str, table)
			table[j][j+1] = [(p.lhs(),None) for p in grammar.getProdsByRhs(token)]	
			table[j][0] = token	

		#Fill the rest of the table using a bottom up approach
		for j in range(1,n_tokens+1):
			for i in range(j-1,-1,-1):
				#Check for binary productions	
				for k in range(i+1,j):
					for  nB,(B,back_ptrs) in enumerate(table[i][k]):
						for nC,(C,back_ptrs) in enumerate(table[k][j]):
							B_back_ptr = (i,k,nB)
							C_back_ptr = (k,j,nC)
							back_ptrs = [B_back_ptr,C_back_ptr]
							rhs = ' '.join([B,C])
							table[i][j].extend( [ (p.lhs(),back_ptrs) for p in grammar.getProdsByRhs(rhs) ] )
				#Check for unit productions (extension to base algorithm)
				for n,(rhs,back_ptrs) in enumerate(table[i][j]):
					back_ptrs = [(i,j,n)]
					table[i][j].extend( [ (p.lhs(),back_ptrs) for p in grammar.getProdsByRhs(rhs) ] )	
		#Check if sentence is recognized 
		if grammar.start_symbol() not in [symbol for (symbol,back_ptrs) in table[0][n_tokens]]:
			output_str = 'The sentence, "' +sentence+'", is not accepted by the given grammar!'
			print output_str
			return (trees, output_str, table)
		else:
			#Construct parse trees for given sentence
			for (symbol,back_ptrs) in table[0][n_tokens]:
				if symbol == grammar.start_symbol():
					tree = Tree(symbol)
					self._construct_tree(tree,back_ptrs,table)
					trees.append(tree)
			
			output_str = 'The sentence, "' +sentence+'", is accepted by the given grammar and has '+str(len(trees))+' valid'
			output_str += ' parse!' if len(trees) == 1 else  ' parses!'
			print output_str
			return (trees, output_str, table)	
	
	def _construct_tree(self,tree,back_ptrs,table):
		""" Helper function that constructs the parse tree specified by (symbol,back_ptrs,table) """
		for back_ptr in back_ptrs:
			symbol,back_ptrs = table[back_ptr[0]][back_ptr[1]][back_ptr[2]]
			child=Tree(symbol)
			tree.children().append(child)
			if back_ptrs: # Recursively call on children symbols (non-terminals)
				self._construct_tree(child,back_ptrs,table)
			else:         # Base case: insert leaf node (terminal symbol) and return
				child.children().append(Tree(table[back_ptr[0]][0]))
				