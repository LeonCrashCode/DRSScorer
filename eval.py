from graph import Graph, Graph2
from extract_ngram import Extractor
from collections import Counter

import multiprocessing
import sys
import time
N = 5
M = 4
ncpu = 2
def readitems(filename):
	lines = [[]]
	for line in open(filename):
		line = line.strip()
		if line == "":
			lines.append([])
		else:
			lines[-1].append(line)
	return lines

def sentence_score(hyp, ref):
	return corpus_score([hyp], [ref])

def corpus_score(hyps, refs):

	numerators = 0
	p_denominators = 0
	r_denominators = 0

	assert len(refs) == len(hyps), (
		"The number of hypotheses and their reference(s) should be the " "same "
	)

	for ref, hyp in zip(refs, hyps):
		
		n, p, r = modified_f1(ref, hyp, i)

		numerators += n
		p_denominators += p
		r_denominators += r

	return numerators, p_denominators, r_denominators
	# print(numerators)
	# print(p_denominators)
	# print(r_denominators)
	# p = numerators*1.0 / p_denominators
	# r = numerators*1.0 / r_denominators
	# f1 = 2 * p * r / (p+r)

	# return p, r, f1

def modified_f1(hyp, ref, i):
	
	hyp_count = Counter(hyp)
	ref_count = Counter(ref)


	ngrams = list(hyp_count.keys() | ref_count.keys())

	clipped_counts = {
		ngram: min(hyp_count.get(ngram, 0), ref_count.get(ngram, 0)) for ngram in ngrams
	}

	numerator = sum(clipped_counts.values())
	pdenominator = max(1, sum(hyp_count.values()))
	rdenominator = max(1, sum(ref_count.values()))


	return numerator, pdenominator, rdenominator


def get_f1(numerators, p_denominators, r_denominators):
	p = numerators*1.0 / p_denominators
	r = numerators*1.0 / r_denominators
	f1 = 2 * p * r / (p+r)
	return p, r, f1

def worker(procnum, hyps, refs, extractor, return_dict):
	g_hyp = Graph2()
	g_ref = Graph2()

	numerators = 0
	p_denominators = 0
	r_denominators = 0
	for j, (hyp, ref) in enumerate(zip(hyps, refs)):
		print(procnum, j)
		hyp_ngrams = []
		ref_ngrams = []

		g_hyp.from_tuples(hyp)
		g_ref.from_tuples(ref)

		# g_hyp.shows()
		extractor.extract_ngram(g_hyp, hyp_ngrams)
		extractor.extract_ngram(g_ref, ref_ngrams)
		# p, r, f = sentence_score(hyp_ngrams[-1], ref_ngrams[-1])
		# print(p,r,f)
		# exit(-1)
		n, p, r = sentence_score(hyp_ngrams, ref_ngrams)

		numerators += n
		p_denominators += p
		r_denominators += r

	return_dict[procnum] = [numerators, p_denominators, r_denominators]

if __name__ == "__main__":
	hyps = readitems(sys.argv[1])
	refs = readitems(sys.argv[2])

	extractors = [Extractor(i+1, M) for i in range(N)]

	bin_size = int(len(hyps) / ncpu)
	if len(hyps) % ncpu != 0:
		bin_size += 1
	print(bin_size)
	hyps_p = []
	refs_p = []
	for i in range(ncpu):
		hyps_p.append(hyps[i*bin_size:(i+1)*bin_size])
		refs_p.append(refs[i*bin_size:(i+1)*bin_size])

	for i in range(N):
		print(i)
		start_time = time.time()
		extractor = extractors[i]
		
		numerators = 0
		p_denominators = 0
		r_denominators = 0

		manager = multiprocessing.Manager()
		return_dict = manager.dict()

		jobs = []
		for j in range(ncpu):
			p = multiprocessing.Process(target=worker, args=(j, hyps_p[j], refs_p[j], extractor, return_dict))
			jobs.append(p)
			p.start()

		for proc in jobs:
			proc.join()


		for j in range(ncpu):
			numerators += return_dict[j][0]
			p_denominators += return_dict[j][1]
			r_denominators += return_dict[j][2]

		p, r, f = get_f1(numerators, p_denominators, r_denominators)
		elapsed_time = time.time() - start_time
		print(p, r, f, elapsed_time)

		


