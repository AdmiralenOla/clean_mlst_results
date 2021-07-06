#!/usr/bin/env python

import sys
import re
import csv
import argparse

def my_args():
	parser = argparse.ArgumentParser(
		description='Clean up MLST result files')
	parser.add_argument('mlst_results_file',
		help='File with MLST script results.')
	parser.add_argument('--outfile',
		help='File to store clean results to (Default: stdout)')
	args = parser.parse_args()

	return args


def main():
	args = my_args()
	try:
		myfile = csv.reader(open(args.mlst_results_file,'r'), skipinitialspace=False, delimiter='\t')
	except Exception as e:
		sys.exit('Failed to open %s' % args.mlst_results_file)

	baseheader = ['Isolate','Scheme','ST']
	result_schemes = {}
	results = {} 
	for row in myfile:
		alleles = [re.match('\w+\(([~?\-?\d+\??\,]+)\)',a).group(1) for a in row[3:]]
		isolatename = re.match('(.*).(fasta|fa)',row[0]).group(1)
		scheme = row[1]
		ST = row[2]
		if scheme == '-':
			if "Failed" in results:
				results["Failed"].append(isolatename)
			else:
				results["Failed"] = [isolatename]
				result_schemes["Failed"] = "Names of failed isolates"
			continue
		if scheme not in result_schemes:
			# This scheme not yet seen
			loci = [re.match('\w+',a).group() for a in row[3:]]
			result_schemes[scheme] = baseheader + loci
			results[scheme] = []
		
		res = [isolatename, scheme, ST] + alleles
		results[scheme].append(res)

	if args.outfile is not None:
		# Outfile has been set
		try:
			outfile = csv.writer(open(args.outfile,'w'),delimiter="\t")
		except:
			sys.exit("Could not open outfile %s" % args.outfile)
		for scheme in results:
			outfile.writerow([scheme])
			if scheme != "Failed":
				outfile.writerow(result_schemes[scheme])
				for r in results[scheme]:
					outfile.writerow(r)
			else:
				outfile.writerow([result_schemes[scheme]])
				outfile.writerow(results[scheme])
			outfile.writerow("")

	else:
		for scheme in results:
			print(scheme + ":")
			if scheme != "Failed":
				print("\t".join([r for r in result_schemes[scheme]]))
				for r in results[scheme]:
					print("\t".join(r))
			else:
				print(result_schemes[scheme])
				print("\n".join([r for r in results[scheme]]))
			print("\n")

if __name__ == '__main__':
	main()
