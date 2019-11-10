from graph import Graph, Graph2
from extract_ngram import Extractor
from collections import Counter

import multiprocessing
import sys
import time
import math
N = 4
M = 4
ncpu = 1
def readitems(filename):
	lines = [[]]
	for line in open(filename):
		line = line.strip()
		if line == "":
			lines.append([])
		else:
			lines[-1].append(line)
	return lines

def worker(procnum, refs, extractor):
	g_ref = Graph2()

	for j, ref in enumerate(refs):
		ref_ngrams = []
		g_ref.from_tuples(ref)
		extractor.extract_ngram(g_ref, ref_ngrams)
		print(len(g_ref.node_index_to_variable), g_ref.edge_num, len(ref_ngrams))

if __name__ == "__main__":
	refs = readitems(sys.argv[1])
	extractors = [Extractor(i+1, M) for i in range(N)]
	if ncpu == 1:
		for i in range(N):
			print("====",i)
			extractor = extractors[i]
			worker(0, refs, extractor)
	else:
		bin_size = int(len(hyps) / ncpu)
		if len(hyps) % ncpu != 0:
			bin_size += 1
		refs_p = []
		for i in range(ncpu):
			refs_p.append(refs[i*bin_size:(i+1)*bin_size])

		for i in range(N):
			print("====",i)
			extractor = extractors[i]
			
			numerators = 0
			p_denominators = 0
			r_denominators = 0

			manager = multiprocessing.Manager()

			jobs = []
			for j in range(ncpu):
				p = multiprocessing.Process(target=worker, args=(j, refs_p[j], extractor))
				jobs.append(p)
				p.start()

			for proc in jobs:
				proc.join()



		


