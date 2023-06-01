import os

def splitDB(filename,number_of_complexes_per_chunk=10000):
    '''Given a SDF file with ComplexExp information, splits the SDF file in chunks of a given number of complexExp.'''

    fh=open(filename,'r')
    counter=1
    indexes=[]
    for line in fh:
        if '$$$' in line:
            indexes.append(counter)
        counter+=1

    fh.close()

    finalindexes=[]

    complexcounter=1

    while complexcounter<len(indexes):
        if complexcounter % number_of_complexes_per_chunk==0:
            finalindexes.append(indexes[complexcounter-1])
        complexcounter+=1

    #ensure that the last line is included in the definitive indexes. Otherwise, a whole chunk will not be included.

    if finalindexes[-1]!=indexes[-1]:
        finalindexes.append(indexes[-1])

    finalindexes=[0]+finalindexes 
    bb=finalindexes

    i=0
    nameslist=[]
    while i<len(bb)-1:
        os.system('head -'+ str(bb[i+1]) +' '+filename+' > tmp.txt')
        os.system('tail -n ' + str(bb[i+1]-bb[i]) + ' tmp.txt > chunk'+str(i)+'_from'+str(bb[i])+'_to_'+str(bb[i+1])+'.sdf')
        nameslist.append('chunk'+str(i)+'_from'+str(bb[i])+'_to_'+str(bb[i+1])+'.sdf')
        i+=1

    return nameslist

splitDB('BindingDB_All_3D.sdf',number_of_complexes_per_chunk=20000) #probably 5000 is enough->40MB/chunk

