from .customized_errors import ParsingError

import re

def check_sequence(seqstr,allow_gaps=True,allow_stop=False):
  w = re.compile(r'^\s+$')
  rec = re.compile(r'^[A-Z\s]+$')
  seqstr2 = seqstr
  if seqstr2 == "":
      return False
  if allow_gaps:
      seqstr2 = seqstr2.replace('-','')
  if allow_stop:
      seqstr2 = seqstr2.replace('*','')
  seqst2 = seqstr2.replace('\n','')
  return bool(rec.match(seqstr2) and not w.match(seqstr2))
def check_fasta(fastastr,allow_stop=False):
  if fastastr.replace('\n','') == "":
     return False
  lines = fastastr.split('\n')
  seqcounter = 0
  hcounter = 0
  for el in lines:
     if el.find('>') == 0:
       if seqcounter == 0 and hcounter > 0:
          return False
       seqcounter = 0
       hcounter += 1
       continue
     if el == '':
       continue
     if not check_sequence(el,allow_gaps=True,allow_stop=False):
       return False
     seqcounter += len(el)
  if seqcounter > 0:
    return True
  else:
    return False
def get_mutations(fastastr,refseq):
        '''Get the sequence from a fasta file, compare this sequence with the one given in the pdb.
         Do an alignment to check if the resids are corrupted in the pdb. Returns a table showing
         the changes in the pdb numbering according to the fasta.'''
        data = dict()
        ws = re.compile(r'\s+')
        lines = fastastr.split('\n')
        flag = 0
        fastalist = []
        for el in lines:
                el=el.strip()
                if el.find('>') == 0 and flag < 2:
                        fastalist.append('')
                        flag += 1
                        continue
                elif '>' in el and flag < 2:
                        raise ParsingError('More than two sequences has been given.')
                elif el == '':
                  continue
                else:
                        fastalist[-1] += ws.sub('',el)
        print(fastalist)
        if fastalist[0].replace('-','') != refseq:
          raise ParsingError('First sequence in alignment is not the cannonical sequence.')
        if len(fastalist[0]) != len(fastalist[1]):
          raise ParsingError('Sequences does not have the same length in fasta alignment.')
        fastaref = fastalist[0]
        fastamut = fastalist[1]
        del fastalist

        i=0
        mismatchlist=list()
        
        while i < len(fastaref):   
                
                if fastaref[i] != fastamut[i]:
                  mismatch = dict()
                  mismatch['resid'] = i + 1
                  mismatch['from'] = fastaref[i]
                  mismatch['to'] = fastamut[i]
                  mismatchlist.append(mismatch)
                i += 1
        data["mutations"] = mismatchlist
        data["mutsequence"] = fastamut.replace('-','')
        return (data)