
def run(args):
  assert len(args) == 1
  json_file = args[0]
  import json

  with open(json_file, 'rb') as f:
    results = json.load(f)

  n_indexed = []
  fraction_indexed = []
  n_spots = []
  n_lattices = []

  for r in results:
    n_spots.append(r['n_spots_total'])
    if 'n_indexed' in r:
      n_indexed.append(r['n_indexed'])
      fraction_indexed.append(r['fraction_indexed'])
      n_lattices.append(len(r['lattices']))
    else:
      n_indexed.append(0)
      fraction_indexed.append(0)
      n_lattices.append(0)

  import matplotlib
  matplotlib.use('Agg')
  from matplotlib import pyplot
  
  blue = '#3498db'
  red = '#e74c3c'

  marker = 'o'
  alpha = 0.5
  lw = 0

  pyplot.scatter(n_spots, n_indexed, marker=marker, alpha=alpha, c=blue, lw=lw)
  xlim = pyplot.xlim()
  ylim = pyplot.ylim()
  pyplot.plot([0, max(n_spots)], [0, max(n_spots)], c=red)
  pyplot.xlim(0, xlim[1])
  pyplot.ylim(0, ylim[1])
  pyplot.xlabel('# spots')
  pyplot.ylabel('# indexed')
  pyplot.savefig('n_spots_vs_n_indexed.png')
  pyplot.clf()

  pyplot.scatter(
    n_spots, fraction_indexed, marker=marker, alpha=alpha, c=blue, lw=lw)
  pyplot.xlim(0, pyplot.xlim()[1])
  pyplot.ylim(0, pyplot.ylim()[1])
  pyplot.xlabel('# spots')
  pyplot.ylabel('Fraction indexed')
  pyplot.savefig('n_spots_vs_fraction_indexed.png')
  pyplot.clf()

  pyplot.scatter(
    n_indexed, fraction_indexed, marker=marker, alpha=alpha, c=blue, lw=lw)
  pyplot.xlim(0, pyplot.xlim()[1])
  pyplot.ylim(0, pyplot.ylim()[1])
  pyplot.xlabel('# indexed')
  pyplot.ylabel('Fraction indexed')
  pyplot.savefig('n_indexed_vs_fraction_indexed.png')
  pyplot.clf()

  pyplot.scatter(
    n_spots, n_lattices, marker=marker, alpha=alpha, c=blue, lw=lw)
  pyplot.xlim(0, pyplot.xlim()[1])
  pyplot.ylim(0, pyplot.ylim()[1])
  pyplot.xlabel('# spots')
  pyplot.ylabel('# lattices')
  pyplot.savefig('n_spots_vs_n_lattices.png')
  pyplot.clf()

if __name__ == '__main__':
  import sys
  run(sys.argv[1:])
