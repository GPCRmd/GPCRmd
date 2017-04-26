import numpy as np
import mdtraj as md

def parser(filename):
    #'dynadb/b2ar_isoprot/b2ar.psf'
    chargesfh=open(filename,'r')
    atom_flag=0
    atoms=dict()
    for line in chargesfh:
        if '!NBOND' in line:
            atom_flag=0
        if atom_flag==1 and line.strip(): #line.strip() prevents using empty lines bc empty string evaluates to False
            fields=line.split()
            charge=fields[6]
            if 'E' in charge:
                charge= float(charge[:charge.rfind('E')]) * 10**float(charge[charge.rfind('E')+1:])
            atoms[fields[0]]=[float(charge),fields[5],fields[3],fields[2]] # charge, atom type, resname, resid
        if '!NATOM' in line:
            atom_flag=1

    return atoms

def compute_interaction(traj,atom1,atom2,atoms,contact_threshold=0,fpt=0.1):
    '''Uses 0-based mdtraj atom indexing. atoms is a dictionary with the partial charge of every atom index, 1-based.
    contact_threshold defines the absolute magnitude of the force to be considered as a repulsive or a attraction contact,
    fpt decides the percentage of frames in which the contact must be above the contact_threshold to be considered a contact. '''
    atom_pairs=np.array([[atom1,atom2]])
    distances=md.compute_distances(traj, atom_pairs) #atom_pairs must be mdtraj indices => PDB atom index-1 
    distances=(distances/10**9)**2 #convert to meters
    tocoulombs=0.0000000000000000001602
    charge=(atoms[str(atom1+1)][0]*atoms[str(atom2+1)][0])*tocoulombs**2  # -*- and +*+ give + result. -*+ or +*- return - result. Atraction is -, Repulsion is +. this indexes are PDB indexes!
    interaction=(charge/distances)*8.98755*10**9
    interaction=interaction*10**9 #newtons to nanonewtons
    contact=(sum(sum(abs(interaction)>contact_threshold))/len(traj))>=fpt
    return interaction,contact


def saline_bridges(traj,atoms,distance_threshold=0.5, percentage_threshold=0.1):
    '''Uses psf charges'''
    salt_bridges_atoms=[]
    salt_bridges_residues=[]
    for residue in traj.topology.residues:
        if residue.name in ['ASP','GLU','ARG','LYS','TYR','HIS','HSD','SER']:
            for atom in residue.atoms:
                if abs(atoms[str(atom.index+1)][0])>0.6:
                    salt_bridges_atoms.append(atom.index+1)

    for atom_index in salt_bridges_atoms:
        for atom_index2 in salt_bridges_atoms:
            if atoms[str(atom_index)][0]*atoms[str(atom_index2)][0]<0 and atoms[str(atom_index)][3]!=atoms[str(atom_index2)][3]: #opposite charges and different residues
                distances=md.compute_distances(traj, np.array([[atom_index,atom_index2]]))
                if (sum(distances < distance_threshold)[0]/len(traj)) > percentage_threshold: # stable saline brigde across simulation
                    if [atoms[str(atom_index)][3], str(atom_index), '----', atoms[str(atom_index2)][3], str(atom_index2) ] not in salt_bridges_residues and [atoms[str(atom_index2)][3], str(atom_index2), '----', atoms[str(atom_index)][3], str(atom_index) ] not in salt_bridges_residues:
                        salt_bridges_residues.append( [atoms[str(atom_index)][3], str(atom_index), '----', atoms[str(atom_index2)][3], str(atom_index2) ] )

    return salt_bridges_residues


def true_saline_bridges(traj,atoms,distance_threshold=0.4, percentage_threshold=0.1):    
    '''uses only combinations between asp, glu, arg and lys'''
    percentage_threshold=percentage_threshold/100
    salt_bridges_atoms=[]
    salt_bridges_residues=[]
    cdis=[]
    for residue in traj.topology.residues:
        if residue.name in ['ASP','GLU','ARG','LYS']:
            caindex= [atom.index for atom in residue.atoms if atom.name == 'CA'][0]
            for atom in residue.atoms:
                cdis.append([caindex,atom.index])

    distance=md.compute_distances(traj[0], np.array(cdis),periodic=False)
    distancedic=dict()
    for i in range(len(cdis)): #iterate for each ca-atom.index pair
        try:
            if distance[0][i]>distancedic[cdis[i][0]][0]: #if distance from another atom is bigger, pick that atom index and distance
                distancedic[cdis[i][0]]=[distance[0][i],cdis[i][1]]
        except KeyError:
            distancedic[cdis[i][0]]=[distance[0][i],cdis[i][1]] # distance['ca']=[maxdis,atom_index]

    for keys in distancedic:
        salt_bridges_atoms.append(int(distancedic[keys][1])+1) #pick the most distal atom and add one to go to 1-based indexing.

    combinations=[]
    for atom_index in range(len(salt_bridges_atoms)):
        for atom_index2 in range(atom_index+1,len(salt_bridges_atoms)):
            atom1=atoms[str(salt_bridges_atoms[atom_index])]
            atom2=atoms[str(salt_bridges_atoms[atom_index2])]
            resid1=int(atom1[3])
            resid2=int(atom2[3])
            chained=abs(resid2-resid1)<4
            if {atom1[2],atom2[2]} in [{'ASP','ARG'},{'ASP','LYS'},{'GLU','LYS'},{'GLU','ARG'}] and not chained: #is this a correct combination?
                combinations.append([salt_bridges_atoms[atom_index],salt_bridges_atoms[atom_index2]])
    combinations=np.array(combinations)
    distances=md.compute_distances(traj,combinations)
    mean_distance=np.sum(distances,axis=0)/len(traj) < distance_threshold
    frequency= np.sum(distances < distance_threshold,axis=0)/len(traj)
    distances= frequency > percentage_threshold
    salt_bridges_residues=combinations[distances] #logical mask to the combinations
    combfreq=np.concatenate((combinations,np.array([frequency]).T),axis=1) # atom1,atom2, freq

    salt_bridges_residues=combfreq[distances]



    return salt_bridges_residues

if False:
    import numpy as np
    import mdtraj as md   
    t=md.load('dynadb/b2ar_isoprot/b2ar.dcd',top='dynadb/b2ar_isoprot/build.pdb')
    from dynadb import psf_parser as psf
    atoms=psf.parser('dynadb/b2ar_isoprot/b2ar.psf')
    b=psf.compute_interaction(t[:5],0,1,atoms,contact_threshold=0,fpt=0.1)
    frametime=(t[:4].time).reshape(len(t[:4].time),1)
    tograph=np.concatenate([b[0],frametime],axis=1).tolist()

