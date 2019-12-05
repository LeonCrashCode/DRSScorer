from graph import Graph, Graph2
from extract_ngram import Extractor
from collections import Counter
from wordnet_dict_en import en_sense_dict
import multiprocessing
import sys
import time
import math
N = int(sys.argv[3])

weights = []
for item in sys.argv[4:]:
	weights.append(float(item))

assert len(weights) == N+1
M = 4
ncpu = 1

def rewrite(line):
	line = line.split()
	if len(line) == 3:
		line[1] = en_sense_dict.get(line[1], line[1])
	return " ".join(line)
def readitems(filename):
	lines = [[]]
	for line in open(filename):
		line = line.strip()
		if line == "":
			lines.append([])
		else:
			line = rewrite(line)
			if line not in lines[-1]:
				lines[-1].append(line)

	if len(lines[-1]) == 0:
		lines.pop()
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


	# print(hyp_count)
	# print(ref_count)
	ngrams = list(hyp_count.keys() | ref_count.keys())

	clipped_counts = {
		ngram: min(hyp_count.get(ngram, 0), ref_count.get(ngram, 0)) for ngram in ngrams
	}

	# print(clipped_counts)
	numerator = sum(clipped_counts.values())
	pdenominator = max(0, sum(hyp_count.values()))
	rdenominator = max(0, sum(ref_count.values()))

	return numerator, pdenominator, rdenominator


def get_f1(numerators, p_denominators, r_denominators):
	if p_denominators == 0 and r_denominators == 0:
		return "skip", "skip", "skip"
	p = numerators*1.0 / p_denominators if p_denominators != 0 else 0
	r = numerators*1.0 / r_denominators if r_denominators != 0 else 0
	f1 = 2 * p * r / (p+r) if p + r != 0 else 0
	return p, r, f1

def worker(procnum, hyps, refs, extractor, return_dict):
	g_hyp = Graph2()
	g_ref = Graph2()

	numerators = 0
	p_denominators = 0
	r_denominators = 0
	for j, (hyp, ref) in enumerate(zip(hyps, refs)):
		#print(procnum, j)
		hyp_ngrams = []
		ref_ngrams = []

		g_hyp.from_tuples(hyp)
		g_ref.from_tuples(ref)

		# g_hyp.shows()
		extractor.extract_ngram(g_hyp, hyp_ngrams)
		extractor.extract_ngram(g_ref, ref_ngrams)

		#print(hyp_ngrams)
		#print(ref_ngrams)

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


	zero_grams = 0.0
	for hyp, ref in zip(hyps, refs):
		gram_hyps = 0.0
		d = {}
		for clause in hyp:
			clause = clause.split()
			if clause[0] not in d:
				d[clause[0]] = 1
			for item in clause[2:]:
				if item not in d:
					d[item] = 1
		gram_hyps += len(d.keys())

		gram_refs = 0.0
		d = {}
		for clause in ref:
			clause = clause.split()
			if clause[0] not in d:
				d[clause[0]] = 1
			for item in clause[2:]:
				if item not in d:
					d[item] = 1
		gram_refs += len(d.keys())

		zero_grams += min(gram_refs, gram_hyps) / max(gram_refs, gram_hyps)

	zero_grams /= len(hyps)
	
	# extractors = []
	# for i in range(N+1):
	# 	for j in range(M+1):
	# 		if i + j == 0:
	# 			continue
	# 		extractors.append(Extractor(i, j))
	extractors = [Extractor(i+1, M) for i in range(N)]
	sumlog_f = 0
	sumlog_p = 0
	sumlog_r = 0
	all_time = 0

	Numerators = [0 for i in range(N)]
	p_Denominators = [0 for i in range(N)]
	r_Denominators = [0 for i in range(N)]

	if ncpu == 1:
		
		for i in range(N):

			start_time = time.time()
			extractor = extractors[i]

			return_dict = {}
			worker(0, hyps, refs, extractor, return_dict)
			numerators = return_dict[0][0]
			p_denominators = return_dict[0][1]
			r_denominators = return_dict[0][2]

			Numerators[i] = numerators
			p_Denominators[i] = p_denominators
			r_Denominators[i] = r_denominators

			elapsed_time = time.time() - start_time
			all_time += elapsed_time
			print(i+1, "grams time:", elapsed_time)
	else:
		bin_size = int(len(hyps) / ncpu)
		if len(hyps) % ncpu != 0:
			bin_size += 1
		hyps_p = []
		refs_p = []
		for i in range(ncpu):
			hyps_p.append(hyps[i*bin_size:(i+1)*bin_size])
			refs_p.append(refs[i*bin_size:(i+1)*bin_size])

		for i in range(N):
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

			Numerators[i] = numerators
			p_Denominators[i] = p_denominators
			r_Denominators[i] = r_denominators

			elapsed_time = time.time() - start_time
			all_time += elapsed_time
			print(i+1, "grams time:", elapsed_time)

	max_N = 0

	sumlog_f = [0 for i in range(N)]
	sumlog_p = [0 for i in range(N)]
	sumlog_r = [0 for i in range(N)]
	for i in range(N):
		if r_Denominators[i] == 0:
			continue
		else:
			max_N += 1
			p, r, f = get_f1(Numerators[i], p_Denominators[i], r_Denominators[i])
			print(i+1, "grams score:", p, r, f)
			sumlog_f[i] += math.log(f if f != 0 else 1e-3)
			sumlog_p[i] += math.log(p if p != 0 else 1e-3)
			sumlog_r[i] += math.log(r if r != 0 else 1e-3)
	
	i = 0
	while i < max_N:
		j = max_N
		while j < N:
			weights[i] += weights[j] / (N-max_N)
			j += 1
		i += 1

	final_f = 0
	final_p = 0
	final_r = 0
	for i in range(max_N):
		final_f += weights[i] * sumlog_f[i]
		final_p += weights[i] * sumlog_p[i]
		final_r += weights[i] * sumlog_r[i]

	final_p += weights[-1] * math.log(zero_grams)
	final_r += weights[-1] * math.log(zero_grams)
	final_f += weights[-1] * math.log(zero_grams)

	print(math.exp(final_p), math.exp(final_r), math.exp(final_f), all_time)

		


