

OPERATORS = ["DRS", "REF"]

def three_tuples(line):
	threes = []
	cnt = 0
	for l in line:
		l = l.split()
		if len(l) == 4:
			c = "c" + str(cnt)
			threes.append([l[0], l[1], c])
			threes.append([c, "ARG0", l[2]])
			threes.append([c, "ARG1", l[3]])
			cnt += 1
		elif len(l) == 3:
			if l[1] in OPERATORS:
				threes.append(l)
			else:
				c = "c" + str(cnt)
				threes.append([l[0], l[1], c])
				threes.append([c, "ARG", l[2]])
	return threes

class Graph:

	def __init__(self):
		self.nodes = []
		self.edges = []

	def from_tuples(self, items: list):

		items = three_tuples(items)

		variable_to_node_index = {}
		node_index_to_variable = []
		for t in items:
			assert len(t) == 3
			if t[0] not in variable_to_node_index:
				variable_to_node_index[t[0]] = len(node_index_to_variable)
				node_index_to_variable.append(t[0])
			if t[-1] not in variable_to_node_index:
				variable_to_node_index[t[2]] = len(node_index_to_variable)
				node_index_to_variable.append(t[2])

		self.variable_to_node_index = variable_to_node_index
		self.node_index_to_variable = node_index_to_variable

		self.nodes = [ [] for i in range(len(node_index_to_variable))]
		self.edges = [ [] for i in range(len(node_index_to_variable))]
		for t in items:
			assert len(t) == 3
			if len(t) == 3:
				fr = variable_to_node_index[t[0]]
				to = variable_to_node_index[t[2]]
				self.nodes[fr].append(to)
				self.edges[fr].append("$TO$"+t[1])

				self.nodes[to].append(fr)
				self.edges[to].append("$FR$"+t[1])
	def shows(self):
		print(self.node_index_to_variable)
		for nodes in self.nodes:
			print(nodes)
		for edges in self.edges:
			print(edges)

class Graph2:

	def __init__(self):
		pass

	def from_tuples(self, items: list):

		variable_to_node_index = {}
		node_index_to_variable = []
		for t in items:
			t = t.split()
			assert len(t) == 3 or len(t) == 4
			if t[1] == "EQU":
				t[1] = "Equ"
			if t[0] not in variable_to_node_index:
				variable_to_node_index[t[0]] = len(node_index_to_variable)
				node_index_to_variable.append(t[0])
			if t[2] not in variable_to_node_index:
				variable_to_node_index[t[2]] = len(node_index_to_variable)
				node_index_to_variable.append(t[2])
			if len(t) == 4 and t[3] not in variable_to_node_index:
				variable_to_node_index[t[3]] = len(node_index_to_variable)
				node_index_to_variable.append(t[3])

		self.variable_to_node_index = variable_to_node_index
		self.node_index_to_variable = node_index_to_variable

		self.nodes = [ [] for i in range(len(node_index_to_variable))]
		self.edges = [ [] for i in range(len(node_index_to_variable))]

		self.edge_num = 0
		for t in items:
			t = t.split()
			assert len(t) == 3 or len(t) == 4
			if t[1] == "EQU":
				t[1] = "Equ"
			if len(t) == 3:
				fr = variable_to_node_index[t[0]]
				to = variable_to_node_index[t[2]]
				self.nodes[fr].append(to)
				self.edges[fr].append("$TO$"+t[1]+"$ARG")
				self.edge_num += 1
				#if True:
				if not t[1].isupper():
					self.nodes[to].append(fr)
					self.edges[to].append("$FR$"+t[1]+"$ARG")
					self.edge_num += 1
					pass
			if len(t) == 4:
				fr = variable_to_node_index[t[0]]
				to1 = variable_to_node_index[t[2]]
				to2 = variable_to_node_index[t[3]]
				self.nodes[fr].append(to1)
				self.edges[fr].append("$TO$"+t[1]+"$ARG1")
				self.nodes[to1].append(to2)
				self.edges[to1].append("$TO$"+t[1]+"$ARG2")
				self.edge_num += 2
				#if True:
				if not t[1].isupper():
					self.nodes[to1].append(fr)
					self.edges[to1].append("$FR$"+t[1]+"$ARG1")
					self.nodes[to2].append(to1)
					self.edges[to2].append("$FR$"+t[1]+"$ARG2")
					self.edge_num += 2
					pass


	def shows(self):
		print(self.node_index_to_variable)
		for nodes in self.nodes:
			print(nodes)
		for edges in self.edges:
			print(edges)


