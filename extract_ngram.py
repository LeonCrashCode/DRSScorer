

class Extractor:
	def __init__(self, ngram=4, struct_ngram=4):

		self.ngram = ngram
		self.struct_ngram = struct_ngram

	def extract_ngram(self, graph, paths):
		self.g = graph
		self.length = len(self.g.nodes)
		self.paths = paths
		for i in range(self.length):
			state = [i, 0, 0, set(), []]
			self.traversal(state)
			# for path in self.paths:
			# 	print(path)
			# print(len(self.paths))
			# exit(-1)
			

	def traversal(self, state):
		i, step, struct_step = state[:3]
		if step == self.ngram or struct_step == self.struct_ngram:
		#if step + struct_step == self.ngram:
			self.paths.append(" ".join(state[-1]))
			return 

		for n, e in zip(self.g.nodes[i], self.g.edges[i]):

			act = str(i)+"_"+str(n)+e
			if act in state[-2]:
				continue

			state[0] = n
			if not e.isupper():
				state[1] += 1
			else:
				state[2] += 1
			state[-2].add(act)
			state[-1].append(e)

			self.traversal(state)

			state[0] = i
			if not e.isupper():
				state[1] -= 1
			else:
				state[2] -= 1
			state[-2].remove(act)
			state[-1].pop()
