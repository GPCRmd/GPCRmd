import argparse as ap
import sys
from pandas import DataFrame
from seaborn import heatmap
from matplotlib import pyplot

# Arguments
parser = ap.ArgumentParser(description="""
	This script creates a heatmap from a get_dynamics_contacts output file. 
	This heatmap is a discrete one, and indicates the presence/absence of interaction between a certain position
	and the ligand (Y-axis) in a certain frame (x-axis) 
	""")
parser.add_argument(
    '-i',
    dest='infile',
    action='store',
    help='(str) path to the get_dynamics_contacts to use as input'
)
parser.add_argument(
    '-l',
    dest = 'lig',
    action='store',
    help='(str) resname or chainID (peptidic ligands) of the ligand molecule'
)
parser.add_argument(
    '-w',
    dest = 'width',
    type = int,
    default = 0,
    action='store',
    help='(int) with of the output heatmap figure (default: half the number of frames)'
)
parser.add_argument(
    '-a',
    dest = 'height',
    type = int,
    default = 0,
    action='store',
    help='(int) height of the output heatmap figure (default: a tenth the number of positions)'
)
parser.add_argument(
    '-o',
    dest = 'outfile',
    action='store',
    default='frame_position',
    help='(str) name of the output file (default: outfile)'
)
parser.add_argument(
    '--byatom',
    dest = 'byatom',
    action='store_true',
    default=False,
    help='(bool) Plot by atoms instead of by residues (default: False)'
)
parser.add_argument(
	'-t',
	dest = 'itype',
	action = 'store',
	default = False,
	help = '(str) Select only interactions of a certain getContacts type (default: all types)'
)
args = parser.parse_args()

# Initial variables
infile = args.infile
outfile = args.outfile
lig = args.lig
width = args.width
byatom = args.byatom
itype = args.itype
height = args.height

# Open input file
pos_dict = {}
total_frames = int()
with open(infile, 'r') as dynfile:
	for line in dynfile:

		#Omit comment lines
		if line.startswith('#'):
			continue
		split_line = line.split()
		frame = split_line[0]

		# Omit line if not of the selected itype (if any itype was selected in the options)
		if (itype) and not (split_line[1].startswith(itype)):
			continue

		# Add frame entry, if not yet added
		if frame not in pos_dict:
			pos_dict[frame] = {}

		#If this line is of a ligand interaction, take the position which is not the ligand. Else omit the line
		if (split_line[2].startswith(lig+":")) or (":"+lig+":" in split_line[2]):
			recpos = split_line[3]
		elif (split_line[3].startswith(lig+":")) or (":"+lig+":" in split_line[3]):
			recpos = split_line[2]
		else:
			continue

		# Remove atom name. The plot is by residue, not atom
		if not byatom:
			recpos = recpos.rsplit(':',1)[0]

		# Store positions interacting with ligands in a dictionary
		pos_dict[frame][recpos] = 1

	total_frames = int(frame)

#Table time
df = DataFrame(pos_dict).fillna(0)

# Sort by residue number
df['posname'] = df.axes[0].values
df.set_axis(df['posname'].apply(lambda x: x.split(':',2)[2]), axis = 0, inplace = True)
df = df.sort_index()
df.set_axis(df['posname'], inplace = True)
df.drop(['posname'], axis = 1, inplace = True)

# Skip if no interactions ara avalible
if df.empty:
	sys.exit("No interactions avalible for the selected input file and paramters")

# CSV time
df.to_csv(outfile+'.tsv', sep = '\t')

# Determine size of plot
if not width:
	width = total_frames*0.5
if not height:
	height = len(df.columns)*0.1

fig, ax = pyplot.subplots(figsize=(width, height))

# Plotting time
myplot = heatmap(ax = ax, data = df, cbar = False,)
figure =myplot.get_figure()
figure.savefig(outfile+'.png')