from django.core.management.base import BaseCommand, CommandError
from django.db.models import F
from django.conf import settings

from modules.dynadb.models import DyndbModel, DyndbDynamics, DyndbFiles, DyndbModelComponents
from modules.dynadb.pipe4_6_0 import useline2, d

import re
import os
import gc
import MDAnalysis as mda
from MDAnalysis.analysis import align
from MDAnalysis.analysis.rms import rmsd
import urllib.request
import mdtraj as md
import pickle
import numpy as np
import transforms3d
import requests

class Command(BaseCommand):
    help = "Retrieves the transformation matrix corresponding to the alignment between our model PDBs and the x-ray PDBs. This will be used to align the ED map of the x-ray structure to our model and simulation."
    def add_arguments(self, parser):
        parser.add_argument(
           '--sub',
            dest='submission_id',
            nargs='*',
            action='store',
            default=False,
            help='Specify submission id(s) for which the matrix will be precomputed.'
        )
        parser.add_argument(
           '--dyn',
            dest='dynamics_id',
            nargs='*',
            action='store',
            type=int,
            default=False,
            help='Specify dynamics id(s) for which the matrix will be precomputed. '
        )
        parser.add_argument(
            '--ignore_publication',
            action='store_true',
            dest='ignore_publication',
            default=False,
            help='Consider both published and unpublished dynamics.',
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            dest='overwrite',
            default=False,
            help='Overwrites already generated matrices.',
        )

    def handle(self, *args, **options):
        def seq_from_pdb(filepath,sel_chain_li):
            fpdb=open(filepath,'r')
            onlyaa=""
            resnum_pre=False
            
            for line in fpdb:
                if useline2(line):
                    chain=line[21]
                    resnum=line[22:26].strip()
                    aa=line[17:20]
                    if not sel_chain_li or (chain in sel_chain_li):
                        if int(resnum)<1000:
                            if resnum != resnum_pre:
                                resnum_pre=resnum
                                try:
                                    onlyaa+=d[aa]
                                except: #Modified aminoacid
                                    onlyaa+="X"
            fpdb.close()
            return (onlyaa)
#        def remove_repetition(mylist):
#            rep_res=set()
#            newlist=[]
#            for a in mylist:
#                if mylist.count(a)>1:
#                    if a not in newlist:
#                        newlist.append(a)
#                    rep_res.add(a)
#                else:
#                    newlist.append(a)
#            return(newlist,rep_res)

        def remove_repetition(mylist):
            rep_res=set()
            newlist=[]
            last_a=None
            for a in mylist:
                if a==last_a:
                    rep_res.add(a)
                else:
                    newlist.append(a)
                last_a=a
            return(newlist,rep_res)



        cent_d = {'4iar': [ 19.35468795911534 , -15.3125 , 19.811693410600753 ],'4iaq': [ -13.00620777923979 , -19.905588942307695 , 20.793259436888707 ],
                '4nc3': [ -31.650524354109848 , -17.5875946969697 , -13.583319333205353 ],'5v54': [ -17.79380232766502 , -4.272187499999994 , 27.259359411303286 ],
                '4ib4': [ 31.17636020421887 , 16.783143939393938 , -15.09599221562975 ],'6bqh': [ 45.02292424542737 , 36.843055555555566 , 34.44007468075744 ],
                '6bqg': [ 11.971789637483997 , 28.569531250000004 , 29.739322638358537 ],'5n2s': [ 93.8519902680488 , 136.34182692307695 , 49.081368461353456 ],
                '5tud': [ 19.164048994079952 , -48.03520833333332 , 96.41594152281891 ],'5tvn': [ -31.563449826387657 , -16.883125000000007 , -10.458243328268694 ],
                '4uhr': [ -26.79046232110139 , 6.985937499999999 , -25.227217748733118 ],'5uen': [ 27.914120244571805 , 32.42083333333334 , 144.34671835629717 ]
                ,'3uzc': [ 24.896486488657548 , 24.783052884615387 , 28.333445962328735 ],'5g53': [ -39.383034429512286 , -6.708749999999995 , 15.109758994667049 ],
                '5n2r': [ 11.591435829096806 , 202.86862244897958 , 18.045874343166076 ],'5olo': [ 11.807248941054509 , 202.61058238636366 , 18.23020703062018 ],
                '3vg9': [ -44.0707401071948 , -8.564250000000001 , -12.74855731786036 ],'5iu8': [ -12.123031148346556 , -23.100643382352935 , 19.177289216219094 ],
                '5iub': [ -11.787542717728225 , -23.495800781250004 , 18.13777748717532 ],'5k2c': [ -7.266550650250057 , 68.09034288194445 , 54.174179078174845 ],
                '3rey': [ 31.72225873775439 , 26.08846153846154 , 28.31346697155895 ],'5vra': [ 7.651598722274034 , -23.14553179824562 , 15.968105760800146 ],
                '6aqf': [ 12.025919837075085 , 201.48833912037037 , 15.482202953154447 ],'2ydv': [ 23.955272534488344 , 19.110044642857147 , -22.5231398769212 ],
                '2ydo': [ -24.08842032714731 , 19.278187499999994 , -17.36849712621312 ],'5olh': [ -12.317485775020995 , -21.984555288461536 , 18.079320503958904 ],
                '5jtb': [ 8.092454138803424 , 23.40983072916667 , 52.427450582290916 ],'4eiy': [ 6.664678941697513 , -21.84068750000001 , 17.539596196950676 ],
                '5mzj': [ -11.776384795598837 , -23.474701286764706 , 17.754928419791035 ],'5mzp': [ -11.17921671725433 , -23.520480769230765 , 18.847544514109742 ],
                '5iua': [ -12.011481492764013 , -23.246770833333343 , 18.214101715905546 ],'3uza': [ 31.708079607689463 , 25.282271634615384 , 28.098548107520106 ],
                '5k2b': [ 16.387329335992426 , 203.74806134259262 , 16.579910888831733 ],'3eml': [ -3.99161052012764 , -1.748295454545449 , 28.43144814497762 ],
                '3pwh': [ 31.201881712422292 , 25.431971153846156 , 28.062096850619287 ],'3vga': [ 43.81534525446494 , -7.650213068181817 , 14.518102024526957 ],
                '5wf5': [ -19.90288415795215 , 2.6509943181818194 , -13.588112655177582 ],'3qak': [ -3.7352093684428596 , -0.44850852272726627 , 26.924501494955315 ],
                '5iu4': [ -11.230284292398832 , -23.59963942307693 , 18.350131607726475 ],'5wf6': [ -3.8879065481876403 , -0.46562499999999574 , 26.863808278278235 ],
                '5olv': [ -12.490132059966363 , -23.59216452205883 , 18.58729873723493 ],'5k2a': [ -7.158911575999447 , 68.10532407407408 , 53.93033603629735 ],
                '5nlx': [ -4.384075666044907 , 68.23797123015873 , 54.54129779351108 ],'5uvi': [ 12.58536634765512 , 22.00089285714286 , 15.73182432788117 ],
                '3rfm': [ 23.99456124080693 , -30.692187500000003 , -29.324670391748448 ],'5om1': [ 12.18170152519594 , 202.67711538461543 , 18.230638658218 ],
                '5uig': [ 168.69535587075933 , 22.845033482142853 , 20.79386630510725 ],'4ug2': [ 7.990178021190873 , -29.57421875 , 27.9691257228422 ],
                '5olg': [ -11.100243770377777 , -23.357747395833336 , 16.528312388398106 ],'5olz': [ -12.613585551677605 , -23.68495535714286 , 18.129292339774068 ],
                '5nm2': [ 7.2225617859558735 , -23.43880974264706 , 17.80549488303752 ],'5om4': [ -12.172865840638242 , -23.045955882352942 , 18.172630820055712 ],
                '5nm4': [ -5.555772040296105 , 66.31532451923078 , 54.06418561677668 ],'4zud': [ -35.1985342096201 , 67.64380091392954 , 25.116239271888823 ],
                '4yay': [ -11.659899167773808 , 12.113636363636363 , 38.53749243561466 ],'5k2d': [ 15.756393551719926 , 202.38834635416669 , 17.854639069993897 ],
                '5iu7': [ 7.684868881805876 , -23.12821180555555 , 19.040983198346154 ],'5ung': [ 11.559343094095953 , 7.9725446428571445 , -17.275539626089444 ],
                '5x33': [ 97.28395094440782 , 178.87255859375006 , 303.1462894936816 ],'5vbl': [ 187.15665778392574 , -16.607812499999994 , 30.88804688123105 ],
                '5unh': [ 109.1599982614322 , -73.86979166666667 , 23.522360880796747 ],'5o9h': [ 110.04086447887141 , -7.663124999999997 , 25.486207897733173 ],
                '5unf': [ 70.66072113632544 , 9.546710526315792 , 24.508891096398834 ],'6c1r': [ -5.0982585556992355 , 5.027941176470584 , -27.611061414869525 ],
                '6c1q': [ 4.194305756165793 , 31.43616071428572 , 26.982027182377827 ],'5xra': [ -40.44706975091608 , -139.53281249999995 , 279.5905412252097 ],
                '5tgz': [ 38.85349255106931 , 17.541666666666693 , 294.93274914074493 ],'5t1a': [ 10.12568680244873 , 18.41796875000001 , 184.61480605915312 ],
                '5xr8': [ -43.23756881288718 , -136.06315789473683 , 281.20103562245254 ],'5u09': [ 8.554566473625798 , -6.697916666666664 , 16.230419663981564 ],
                '5uiw': [ -136.84212733652865 , -106.37161458333333 , 644.9712272682357 ],'3oe0': [ 40.294839201374785 , 6.194243421052633 , 16.03267359824443 ],
                '3oe9': [ 9.012768593301814 , 10.076869086056735 , 3.792853912471095 ],'5lwe': [ 154.69388885418869 , 55.347938359020226 , 38.0848751927057 ],
                '3oe6': [ 5.21615456315388 , 21.22828947368421 , 43.26510319968415 ],'4mbs': [ 169.68358163623415 , 121.99687499999999 , 39.703690323757634 ],
                '6cm4': [ 22.75318885165904 , -0.47705592105262795 , 12.300129810806077 ],'4rws': [ 89.15865907716459 , 14.720520833333335 , 47.996169204242264 ],
                '3odu': [ 5.957961328194987 , 2.5106250000000045 , 41.54618068671616 ],'3oe8': [ -41.03751738714762 , 14.917248528580295 , 48.58105528063411 ],
                '5wiv': [ -14.130808473134785 , -13.21167763157895 , -15.25285716064106 ],'3pbl': [ -0.9255345554930106 , 2.8902343750000057 , 0.9781128078661965 ],
                '5xpr': [ -24.052811633132073 , -7.35260488411874 , -8.520326684951087 ],'5wiu': [ -14.410565533213298 , -13.01884920634921 , -14.981142185620225 ],
                '5glh': [ 17.78352755699775 , 32.67069444444444 , 3.649848113268895 ],'5tzy': [ -16.353606294455332 , -6.3949999999999925 , 31.93452174259611 ],
                '5gli': [ -10.083638511631623 , -28.278020833333336 , -12.66123678011942 ],'5kw2': [ 17.47340896888527 , 28.441250000000004 , 21.861730273206113 ],
                '3rze': [ 27.26697296760432 , 25.706770833333334 , 45.609857986241764 ],'4phu': [ -21.709769728901076 , -0.771718749999998 , 31.611242950289416 ],
                '4z35': [ -0.969655158041542 , -11.708333333333336 , 29.186429175006943 ],'4z34': [ -1.4370119629516154 , -12.01607142857143 , 31.22191382601622 ],
                '5xsz': [ -0.5289809620850807 , 16.794895833333328 , -27.477622481748583 ],'5x93': [ 8.555946698896859 , 28.19375 , -10.910083736217032 ],
                '5tzr': [ -20.948127981941408 , -0.37254464285714306 , 31.72449228998857 ],'4mqt': [ -1.8498148145951205 , -13.90556640625 , 17.99400252019106 ],
                '4z36': [ -0.962298670209579 , -12.12520833333334 , 28.86533861072717 ],'4mqs': [ -1.6898108906262177 , -15.510110294117641 , 18.163383487010535 ],
                '3uon': [ 10.66375663540586 , 3.9375 , 19.331356402265698 ],'4u14': [ 9.628280542427328 , 21.75104166666669 , 364.9459096634279 ],
                '5cxv': [ -15.382745148109802 , -17.614136904761907 , 58.70711045066341 ],'4u16': [ -36.0809367615211 , -1.799759615384616 , 5.386162638660128 ],
                '4u15': [ 34.108927203277815 , 89.05140625000001 , 57.61660943466899 ],'4daj': [ -12.061844508023093 , 5.91445639870085 , -1.134860624682446 ],
                '5t04': [ 232.22427753233495 , 12.09097222222223 , 92.013486049615 ],'4ea3': [ 18.697145830707633 , -36.120721726190474 , 18.256252383547988 ],
                '5dsg': [ 54.71952406493924 , 4.731031250000001 , 76.90664656453714 ],'5dhh': [ -17.15288199354815 , 46.25669642857144 , -20.600244439660386 ],
                '4xes': [ 6.2375635925799955 , -13.180588942307693 , -28.678006869165493 ],'5dhg': [ -18.68507652819931 , 50.07552083333332 , -18.089613567379963 ],
                '4bwb': [ 14.640003953179502 , -10.165049342105263 , -22.267879233753426 ],'4buo': [ 11.43633048238083 , -7.599000000000011 , -25.581667042624417 ],
                '3zev': [ -12.676908710911771 , 9.222443181818178 , -21.643419570001534 ],'4grv': [ 78.83282342105345 , -6.8696546052631575 , 32.62668932640496 ],
                '4xee': [ 20.29370366183821 , -30.534659090909088 , -28.315199251466446 ],'4bv0': [ -15.15048058336874 , -11.963920454545459 , 23.000049992904295 ],
                '4zj8': [ -4.821142534609491 , 15.79557291666667 , -33.12066488327793 ],'4zjc': [ -5.120151161570956 , 16.615625 , -33.675698140512395 ],
                '4s0v': [ 57.11712797406569 , 7.322798295454547 , 29.067129818762922 ],'5ws3': [ 37.10503274270689 , 40.64662499999999 , -31.9423443521127 ],
                '4xnw': [ 24.698061037364624 , 8.121402478581793 , -11.947121598191856 ],'4py0': [ 3.7632588504244424 , -13.73203125000001 , -11.766056092076838 ],
                '4ntj': [ 20.043525244792463 , 77.77798611111112 , 31.046938090852457 ],'4xnv': [ -15.098578941739763 , 13.389835274262158 , 18.108647973838266 ],
                '5wqc': [ 37.113340642482854 , 38.70015624999999 , -31.316748350449046 ],'4pxz': [ 35.79631753465974 , -6.103271484375 , 29.90935666439772 ],
                '5zkp': [ 39.583090705918856 , -10.484320044565358 , -16.80503379177452 ],'5zkq': [ 59.394937549678815 , -11.399888392857129 , 214.20199044225396 ],
                '5nj6': [ -21.79495091740475 , 33.69843750000001 , -15.971701346776115 ],'5ndd': [ 7.915993420241694 , 1.5549198412429135 , 43.09655078164296 ],
                '3vw7': [ -5.145429056628263 , -5.582031249999993 , 26.80638197889683 ],'5ndz': [ 7.0659244802292225 , 1.7607239241686088 , 43.55046317001221 ],
                '5dys': [ -44.084735399803755 , -6.389296716991051 , 40.69788481164866 ],'4j4q': [ 12.94516996338493 , 41.01404096655108 , 37.83139489977129 ],
                '3aym': [ 16.673102700342703 , 36.92483011393333 , 37.68108279074393 ],'2z73': [ 15.716232881891738 , 36.43845187693216 , 37.62850338917433 ],
                '1gzm': [ 25.73710379258607 , 15.358644797688555 , -0.8408855501618007 ],'5te3': [ 14.591816463151787 , 38.52586177518724 , 40.36945534822058 ]
                ,'6fk7': [ -230.10294166879808 , 41.76561870759927 , 38.44705363445101 ],'6fk6': [ -109.2691896708663 , -169.04285662237274 , 150.2074137418844 ],
                '4pxf': [ 134.84985472852966 , 250.2998144420174 , 38.657109227958664 ],'3oax': [ 12.12305205708114 , 47.19481026785715 , 1.280235492498619 ],
                '4ww3': [ 16.446281107778077 , 36.53466762733253 , 38.28444234388064 ],'3pqr': [ -41.707916535734704 , -7.471015581576108 , 37.98109083439878 ],
                '4bez': [ 25.80296406935825 , -31.104745752591093 , 39.49023255677231 ],'2i35': [ 44.00512357717902 , 142.98224756392602 , 1.8778571742092147 ],
                '4bey': [ 26.685582937107345 , -31.24360622470087 , 38.721878097862515 ],'2ziy': [ 32.19800504852081 , 6.796093750000001 , 17.14600130415798 ],
                '2hpy': [ 48.35611519866663 , 12.984548611111112 , 0.48500121462663515 ],'2j4y': [ -0.0005068703958102105 , 31.552192211213047 , 1.6236052650609238 ],
                '5wkt': [ 12.992409763369636 , 40.91084540897889 , 38.42192840352169 ],'5dgy': [ -23.254161936505028 , -9.750320102432752 , 171.33035216090383 ],
                '6fk8': [ 26.89664662554107 , 387.0012361313328 , 37.98356535689107 ],'6fkb': [ -229.45449113550313 , 41.624699134083 , 38.56196143635222 ]
                ,'4x1h': [ 12.62229060405798 , -39.3162001671201 , -38.47849754538532 ],'5te5': [ -18.04504564960959 , 35.972259576757445 , 0.6674568421716387 ],
                '2i37': [ -48.72985450275934 , 6.399972839456794 , 75.68993744914376 ],'2x72': [ 21.843742948648 , -30.812913233711654 , 41.43777018329873 ],
                '6fka': [ -353.78369232474563 , -168.7346055006532 , 153.43139946411975 ],'4a4m': [ 10.079349424789786 , 38.840838422045145 , 38.23265791596078 ],
                '6fkd': [ -230.59078482715756 , 41.772053757474616 , 41.85816163480658 ],'3c9m': [ -14.231265512547715 , 54.23033036302244 , -1.6136934940360597 ],
                '3ayn': [ 16.697966331792003 , 36.98141700111243 , 37.440212153239784 ],'4zwj': [ -22.988945945159543 , -10.377430555555534 , 169.1779676845768 ],
                '3pxo': [ -42.07723998706493 , -9.161939847927325 , 39.21440986758007 ],'5en0': [ -44.23462498060526 , -6.6604914090262675 , 39.34747409740265 ],
                '3c9l': [ -13.408859027418558 , 54.69175952347632 , -0.9060821803325005 ],'6fk9': [ -230.36420525629742 , 41.73129844159744 , 38.498627405193574 ],
                '6fkc': [ -352.19583094295706 , -168.2100236427856 , 150.27076848281075 ],'3dqb': [ -40.782739153233706 , -8.588536309093488 , 39.57140050290805 ],
                '2i36': [ -45.983363181913795 , 8.075957523228585 , 76.32100874467655 ],'3v2w': [ 21.359797285306175 , 16.333007812500004 , 9.678107281949593 ],
                '5wb1': [ 8.61526406231566 , 3.190625 , 28.91527997205599 ],'4xt1': [ 102.15889387642157 , 20.73534226190478 , 240.0040114681109 ],
                '3v2y': [ 19.33613583652106 , 16.96340460526316 , 9.315589890179695 ],'3cap': [ 18.324543178715963 , -33.391808872505955 , -32.93032941545706 ],
                '4xt3': [ -17.46750444601369 , -39.52564102564103 , -11.184099844538146 ],'5wb2': [ 25.33621651256729 , 14.965959821428577 , 46.13496389083416 ],
                '5zbh': [ 13.409275440793541 , 34.024951171875 , -30.824860373220638 ],'5zbq': [ -48.76397593284098 , -11.685491071428565 , 91.30320017465289 ],
                '2y04': [ -12.259596961932083 , -3.616666666666667 , 31.017470415877042 ],'2ycx': [ 38.91008839221763 , -10.850961538461547 , -25.451868738742043 ],
                '2y00': [ -11.847134600488136 , -3.781249999999993 , 31.082917310623166 ],'2y03': [ -11.553653344290623 , -2.264246323529413 , 30.86844548496401 ],
                '4amj': [ -11.717358940452087 , -1.1104910714285623 , 31.416304557078547 ],'5f8u': [ 22.291723217865382 , 18.791493055555563 , 17.428358627053903 ],
                '4ami': [ -9.585822462998486 , -2.528124999999992 , 26.65467308029408 ],'2ycy': [ 35.86709907545561 , 9.024107142857133 , -24.711837035836943 ],
                '5w0p': [ -25.842061265993422 , -0.5057227366255006 , 169.22676399534362 ],'2ycz': [ 46.874707273445935 , -16.417187500000004 , 28.725621510134424 ],
                '4bvn': [ -24.803659272520854 , -6.35369318181818 , 20.516016850418502 ],'2ycw': [ 34.37483828422178 , 8.55750000000001 , 28.262064858508307 ],
                '4gpo': [ -27.653730743330442 , -4.421527777777783 , 16.8860887360495 ],'3zpr': [ -11.296164819990892 , -5.066666666666659 , 31.140412989709624 ],
                '2vt4': [ 34.132749531727725 , 19.48971602710195 , -5.285392645400968 ],'2y02': [ -11.317512368133706 , -3.427777777777777 , 31.060860309108843 ],
                '5a8e': [ 24.550907037119124 , 66.79421875 , 21.9043064701424 ],'2y01': [ -11.102859901706818 , -3.8492187500000057 , 31.13604104948189 ],
                '3pds': [ 41.774421914183485 , 16.682291666666664 , 8.704764251478242 ],'5jqh': [ 10.493609995810445 , -5.7987980769230845 , -52.53655118979563 ],
                '3ny8': [ 11.554687577334795 , 5.891592261904764 , 27.585250186735333 ],'2r4r': [ 59.07931532420322 , 49.02585227272728 , 26.49638210165498 ],
                '3zpq': [ -11.14443782016421 , -2.710477941176471 , 31.204955358771294 ],'2rh1': [ -34.387680734588926 , 32.907291666666666 , 17.83901184382227 ],
                '5d5a': [ -35.37213151103987 , 32.91666666666667 , 18.266137273626267 ],'3sn6': [ 29.934260010787668 , 6.454999999999998 , 14.767235583405508 ],
                '3nya': [ -13.178608292608306 , 4.206944444444442 , -28.38790339578165 ],'4qkx': [ 11.881295254943835 , -10.080000000000002 , -35.99266246472374 ],
                '4lde': [ -11.961960423644655 , -24.466493055555564 , -36.488000017851505 ],'3p0g': [ 35.28516904720105 , 12.553750000000004 , 11.0512460654954 ],
                '5d5b': [ -35.271452306505324 , 33.125 , 18.289456364882135 ],'3d4s': [ 12.719325222737726 , 4.955729166666668 , 28.311687993981693 ],
                '3kj6': [ 58.11469026199177 , 49.13963068181819 , 26.388620266708397 ],'5d6l': [ 18.5479931996269 , 32.47296875000001 , 18.421166697111012 ],
                '4ldl': [ -11.887576112539332 , -23.889453125000006 , -36.838654255950026 ],'2r4s': [ 59.07931532420322 , 49.576704545454554 , 26.49638210165498 ],
                '3ny9': [ 12.902165522814581 , 5.87321428571429 , 28.54936029151402 ],'4gbr': [ 4.481420595294953 , 8.921875000000004 , 49.0824862293643 ],
                '5x7d': [ 12.211653926647143 , 5.407142857142862 , 27.549191782553503 ],'4ldo': [ -11.887576112539332 , -23.889453125000006 , -36.838654255950026 ],
                '4rwa': [ -52.7971522854387 , -20.989921875000007 , 24.71154889459136 ],'4ej4': [ 46.902822379482615 , 37.978658375167235 , 14.834823979512109 ]
                ,'6b73': [ 51.231613416002894 , -4.348557692307693 , -0.44977514948151054 ],'5c1m': [ -4.153633327877049 , 16.961538461538463 , -38.13080473171485 ],
                '4rwd': [ -29.3610268011234 , 10.2680625 , 23.637516314599537 ],'4dkl': [ -22.2339768652191 , 14.560416666666672 , -0.45826254776371655 ],
                '4n6h': [ -0.7540135379494508 , -73.15354166666667 , 66.997265660002 ],'5nx2': [ -10.290800741814866 , 20.967807372396315 , 3.104718439026314 ],
                '4k5y': [ -44.763105668019016 , -1.4526855468750028 , 43.67887141731971 ],'5vew': [ 21.725491846186145 , 21.193898309746444 , 41.724899757929926 ]
                ,'4djh': [ 4.56501258232041 , -37.766025641025635 , 31.364774831007743 ],'4z9g': [ -6.304810180979551 , 63.770742858115796 , -23.185879222104006 ],
                '5vex': [ 26.407102164210734 , -16.269766576724557 , -43.29555743583085 ],'5yqz': [ -16.03088994341618 , 14.605729166666668 , 2.9987253741733184 ],
                '4l6r': [ 14.16264141923898 , -11.663750000000007 , -33.454570277868214 ],'5ee7': [ -12.123966532174173 , 1.218323863636364 , -34.54313934832209 ],
                '5cgc': [ -18.72779123325624 , 23.897727272727273 , 24.165322791892656 ],'4oo9': [ -18.613448907413165 , 2.0937500000000036 , 24.36195682695327 ],
                '6ffh': [ -18.916186755277444 , 24.454687500000002 , 26.648003633129 ],'5cgd': [ -18.524848855593856 , 23.96466346153846 , 24.699972973858486 ],
                '4or2': [ 18.231061178005195 , -2.7046874999999986 , 32.25810889294229 ],'6ffi': [ -18.553874920619112 , 2.1706250000000047 , 25.302735084105436 ],
                '5xez': [ 44.38025994496962 , -60.82015625 , -44.62827722249091 ],'5l7d': [ -12.449706193222347 , 8.401666666666678 , 51.266925414035086 ],
                '5l7i': [ 4.551580470456024 , 35.16735249862953 , -56.60704604204257 ],'5xf1': [ 169.67817082973525 , 61.651288377193 , 5.353290895374428 ],
                '4qim': [ 4.027930337122555 , -9.148046875000002 , -42.94829901565676 ],'4jkv': [ -32.872929276236064 , 18.407812500000013 , 7.87976299592772 ],
                '5v57': [ -70.71415711429029 , -54.93729166666667 , 42.2387661325285 ],'4o9r': [ 59.85130373071877 , 33.863194444444446 , 52.549699660231155 ]
                ,'4n4w': [ -15.866395508409653 , -33.2625 , -10.243011984616032 ],'4qin': [ -18.950729674897218 , 33.99229166666666 , 8.138886696007859 ],
                '6d35': [ 8.488414631657648 , -39.9125 , 3.681897505191216 ],'6d32': [ 8.409039590320656 , -41.4693359375 , 3.527496297704843 ],
                '5v56': [ 24.89332673452249 , 48.01339285714287 , 72.91818505082546 ]}

        all_struc=requests.get('http://gpcrdb.org/services/structure/').json()
        all_struc_info={s["pdb_code"]:s for s in all_struc}
        root = settings.MEDIA_ROOT
        EDmap_path=os.path.join(root,"Precomputed/ED_map")
        if not os.path.isdir(EDmap_path):
            os.makedirs(EDmap_path)
        tmp_path=os.path.join(EDmap_path,"tmp")
        if not os.path.isdir(tmp_path):
            os.makedirs(tmp_path)

        if options['ignore_publication']:
            dynobj=DyndbDynamics.objects.all()
        else:
            dynobj=DyndbDynamics.objects.filter(is_published=True)
        if options['submission_id']:
            dynobj=dynobj.filter(submission_id__in=options['submission_id'])
        if options['dynamics_id']:
            print([d.id for d in dynobj])
            dynobj=dynobj.filter(id__in=options['dynamics_id'])
            print([d.id for d in dynobj])
        if dynobj == []:
            self.stdout.write(self.style.NOTICE("No dynamics found with specified conditions."))
############
        dynfiledata = dynobj.annotate(dyn_id=F('id'))
        dynfiledata = dynfiledata.annotate(file_path=F('dyndbfilesdynamics__id_files__filepath'))
        dynfiledata = dynfiledata.annotate(file_id=F('dyndbfilesdynamics__id_files__id'))
        dynfiledata = dynfiledata.annotate(file_is_traj=F('dyndbfilesdynamics__id_files__id_file_types__is_trajectory'))
        dynfiledata = dynfiledata.annotate(file_ext=F('dyndbfilesdynamics__id_files__id_file_types__extension'))
        dynfiledata = dynfiledata.values("dyn_id","file_path","file_id","file_is_traj","file_ext")


        dyn_dict = {}
        for dyn in dynfiledata:
            dyn_id=dyn["dyn_id"]
            if dyn_id not in dyn_dict:
                dyn_dict[dyn_id]={}
                dyn_dict[dyn_id]["dyn_id"]=dyn_id
                dyn_dict[dyn_id]["files"]={"traj":[], "pdb":[]}
                dyn_dict[dyn_id]["pdb_namechain"]=False
                dyn_dict[dyn_id]["chains"]=set()
                dyn_dict[dyn_id]["segments"]=set()
                dyn_dict[dyn_id]["lig_li"]=set()
            file_info={"id":dyn["file_id"],"path":dyn["file_path"]}
            if dyn["file_is_traj"]:
                dyn_dict[dyn_id]["files"]["traj"].append(file_info)
            elif dyn["file_ext"]=="pdb":
                dyn_dict[dyn_id]["files"]["pdb"].append(file_info)
        
        del dynfiledata

        dynmols = dynobj.annotate(dyn_id=F('id'))
        dynmols = dynmols.annotate(pdb_namechain=F("id_model__pdbid"))
        dynmols = dynmols.annotate(chain=F("id_model__dyndbmodeledresidues__chain"))
        dynmols = dynmols.annotate(seg=F("id_model__dyndbmodeledresidues__segid"))
        dynmols = dynmols.annotate(comp_resname=F("id_model__dyndbmodelcomponents__resname"))
        dynmols = dynmols.annotate(comp_type=F("id_model__dyndbmodelcomponents__type"))
        dynmols = dynmols.values("dyn_id","pdb_namechain","chain","seg","comp_resname","comp_type")

        for dyn in dynmols:
            dyn_id=dyn["dyn_id"]
            dyn_dict[dyn_id]["pdb_namechain"]=dyn["pdb_namechain"]
            if dyn["chain"]:
                dyn_dict[dyn_id]["chains"].add(dyn["chain"])
            if dyn["seg"]:
                dyn_dict[dyn_id]["segments"].add(dyn["seg"])
            if dyn["comp_type"]==1:
                dyn_dict[dyn_id]["lig_li"].add(dyn["comp_resname"])

        del dynmols
        del dynobj
        gc.collect()
############
        for dyn in sorted(dyn_dict.values(),key=lambda x:x["dyn_id"]):
            dyn_id=dyn["dyn_id"]

            pdbfile_li=dyn["files"]["pdb"]
            trajfile_li=dyn["files"]["traj"]
            if pdbfile_li:
                ref_filepath=pdbfile_li[0]["path"]
                if len(pdbfile_li) >1:
                    self.stdout.write(self.style.NOTICE("More than one coordinate file found for dyn %s. Only considering %s" % (dyn_id,ref_filepath)))
            else:
                self.stdout.write(self.style.NOTICE("No coordinate file found for dyn %s. Skipping. " % (dyn_id)))
                continue
            if not trajfile_li:
                self.stdout.write(self.style.NOTICE("No trajectory files found for dyn %s. Skipping. " % (dyn_id)))
                continue

            for trajfile in trajfile_li:
                traj_id=trajfile["id"]
                ref_traj_filepath=trajfile["path"]
                ref_fileroot=re.search("([\w_]*)\.\w*$",ref_traj_filepath).group(1)
                matrix_datafile=os.path.join(EDmap_path,"transfmatrix_%s_%s.data"%(dyn_id,traj_id))

                exists=os.path.isfile(matrix_datafile)
                obtain_matrix=False
                if exists:   
                    if options['overwrite']:
                        obtain_matrix=True
                        self.stdout.write(self.style.NOTICE("Alignment data of dyn %s, but will be overwritten." % dyn_id))
                    else:
                        self.stdout.write(self.style.NOTICE("Skipping dyn %s: file already exists."%dyn_id))
                else:
                    obtain_matrix=True
                if obtain_matrix:
                    self.stdout.write(self.style.NOTICE("\nObtaining matrix for dyn id %d, traj id %d"%(dyn_id,traj_id)))
                    try:
                        pdbid_wchain=dyn["pdb_namechain"]
                        if not pdbid_wchain:
                            self.stdout.write(self.style.ERROR("PDB not found. Skipping." ))
                            continue
                        if "." in pdbid_wchain:
                            (pdbid,pdbchain)=pdbid_wchain.split(".")
                            pdbchainli=[pdbchain]
                        else:
                            pdbid=pdbid_wchain
                            pdbchain=all_struc_info[pdbid]["preferred_chain"]
                            pdbchainli=[pdbchain]
                        pdburl="https://files.rcsb.org/download/"+pdbid+".pdb"
                        mobile_filepath=os.path.join(tmp_path,pdbid+".pdb")
                        urllib.request.urlretrieve(pdburl,mobile_filepath )

                        mobile = mda.Universe(mobile_filepath)
                        

                        #    ref = mda.Universe(ref_filepath)
                        #except ValueError:
                            # For some reason I cannot open that with MDanalysis. So I will open it with MDtraj and save (that can be opened). I will take the oportunity to filter only the protein and ligand
                        ref_filepath_filt=os.path.join(tmp_path,ref_fileroot+"_filt.pdb")
                        #------------- Traj test
                        #ref_struc=md.load(ref_filepath)
                        ref_struc=md.load_frame(ref_traj_filepath, 0, top=ref_filepath)
                        #-------------
                        lig_li=dyn["lig_li"]
                        lig_li=["resname "+lig for lig in lig_li]
                        res_sel=" or ".join(lig_li)
                        if res_sel:
                            fin_sel="protein or "+res_sel
                        else:
                            fin_sel="protein"
                        ref_struc_sel=ref_struc.topology.select(fin_sel)
                        ref_struc.atom_slice(atom_indices=ref_struc_sel,inplace=True)
                        ref_struc.save(ref_filepath_filt)
                        



                        ref = mda.Universe(ref_filepath_filt)

                        # Now I need to generate the fasta needed as input for fasta2select, which gives us the selection of mathing segments of the two structures
                        ref_chains=list(dyn["chains"])
                        ref_segids=list(dyn["segments"])
                        if not ref_segids:
                            ref_segids=list(ref.segments.segids)
                        ref_seq=seq_from_pdb(ref_filepath,ref_chains)
                        if not ref_seq:
                            self.stdout.write(self.style.ERROR("Error extracting sequence of reference structure. Skipping." ))
                            continue
                        mob_seq=seq_from_pdb(mobile_filepath,pdbchainli)
                        if not mob_seq:
                            if pdbchainli:
                                self.stdout.write(self.style.ERROR("Chain %s not found in mobile structure. Skipping." % pdbchain ))
                            else:
                                self.stdout.write(self.style.ERROR("Error extracting sequence of mobile structure. Skipping." ))
                            continue
                        fasta_filepath=os.path.join(tmp_path,"dyn_%s.fasta"%dyn_id)
                        f = open(fasta_filepath, "w+")
                        f.write("#Ref\n") 
                        f.write(ref_seq+"\n")
                        f.write("#Mob\n") 
                        f.write(mob_seq+"\n")
                        f.close()

                        aln_filepath=os.path.join(tmp_path,"dyn_%s.aln"%dyn_id)
                        ref_resids=[a.resid for a in ref.select_atoms('name CA and (%s)'%" or ".join(["segid %s"%sid for sid in ref_segids]))] 
                        if pdbchainli:
                            target_sel=mobile.select_atoms('segid %s'%pdbchain)
                            add_sel='segid %s and '%pdbchain
                        else:
                            target_sel=mobile.atoms
                            add_sel=""
                        
                        target_resids= list(target_sel.select_atoms('name CA').resids)  
                        # Remove possible repeated residues in mobile/target
                        (target_resids_filt,rep_res)=remove_repetition(target_resids)
                        target_resids_filt=[res for res  in target_resids_filt if res<1000]
        #[!]Problem detected: when the residues to filter are only in ref or only in mob, I create a difference in the number of selected res: I need to filter before obtaining the equivalences). I think the best option is to create a new mobile universe object where repeated elements are removed, after that we don;t need to dilter out repetitions anymore 
                       #remove_ids=set()
                       #for resid in rep_res:
                       #    atoms_extra=[num for num in target_sel.select_atoms('resid %s'%resid).ids if num % 2] #[!]I have seen that repeated atoms are contiguous at list, so I remove fort ex. even atom ids of the selection. I'm not sure if it's always like this
                       #    remove_ids.update(atoms_extra)
                       #remove_ids_str=' '.join([str(i) for i in remove_ids])
                        
                       #mobile=mda.Merge(mobile.select_atoms('not bynum %s'%remove_ids_str))

                        clustalw_path="clustalw"
                        
                        equivalent_res= mda.analysis.align.fasta2select(fasta_filepath, ref_resids=ref_resids, target_resids=target_resids_filt,
                            clustalw=clustalw_path, alnfilename=aln_filepath)

                        ref_segments_sel=" or ".join(["segid %s"%sid for sid in set(ref_segids)])
                        eqref_selection= "(%s) and (%s)"%(ref_segments_sel , equivalent_res["reference"])
                        eqmobile_selection= add_sel+"("+ equivalent_res["mobile"]+")"

                        #Time to obtain the rotation and translation
                        rep_res_sel=" or ".join(["resid "+str(r) for r in rep_res])
                        if rep_res_sel:
                            no_rep_res_sel="not (%s)"%rep_res_sel
                            mobile_atomsel=mobile.select_atoms(eqmobile_selection).select_atoms("name CA").select_atoms(no_rep_res_sel)
                            ref_atomsel=ref.select_atoms(eqref_selection).select_atoms("name CA").select_atoms(no_rep_res_sel)
                        else:
                            mobile_atomsel=mobile.select_atoms(eqmobile_selection).select_atoms("name CA")
                            ref_atomsel=ref.select_atoms(eqref_selection).select_atoms("name CA")

                        mobile0 = mobile_atomsel.positions - mobile_atomsel.center_of_mass()
                        ref0 = ref_atomsel.positions - ref_atomsel.center_of_mass()
                        #1) Align mobile to ref.
                        (mob_post,rmsd)=mda.analysis.align._fit_to(mobile_coordinates=mobile0, ref_coordinates=ref0, 
                                                   mobile_atoms=mobile.atoms, 
                                                   mobile_com=mobile_atomsel.center_of_mass(),
                                                   ref_com=ref.atoms.center_of_mass()
                                                  )
                        #Fix possible problems with translation
                        trans0=ref_atomsel.center_of_mass()- mobile_atomsel.center_of_mass()
                        mobile.atoms.translate(trans0)

                        #2) Obtain rotation and translatoin for mobile. I do this by aligning "mobil aligned to ref" to "original mobile". otherwise the fact that mob often have extra prot. segments and thus c.o.m. is at a different point of the protein made the rotation very complex
                        mobile_orig = mda.Universe(mobile_filepath)
                        mobile_ref=mobile
                        mobile0 = mobile_orig.select_atoms("name CA").positions - mobile_orig.atoms.center_of_mass()
                        ref0 = mobile_ref.select_atoms("name CA").positions - mobile_ref.atoms.center_of_mass()
                        R, rmsd = align.rotation_matrix(mobile0, ref0)

                        trans=mobile_ref.select_atoms("name CA").center_of_mass()- mobile_orig.select_atoms("name CA").center_of_mass()

                        if dyn_id==4:
                            r_angl=transforms3d.euler.mat2euler(R)
                        else:
                            r_angl=transforms3d.euler.mat2euler(R,"rxyz")

                        # Fix transl t match the center of map
                        centre_coord=np.array(cent_d[pdbid.lower()]) #PDB
                        mobile_orig.atoms.rotate(R,centre_coord)
                        mobile_orig.atoms.translate(trans)

                        eqref_selection= "segid %s and (%s)"%(pdbchain , equivalent_res["reference"])
                        if rep_res_sel:
                            mobile_orig_atomsel=mobile_orig.select_atoms(eqmobile_selection).select_atoms("name CA").select_atoms(no_rep_res_sel)
                            mobile_ref_atomsel=mobile_ref.select_atoms(eqref_selection).select_atoms("name CA").select_atoms(no_rep_res_sel)
                        else:
                            mobile_orig_atomsel=mobile_orig.select_atoms(eqmobile_selection).select_atoms("name CA")
                            mobile_ref_atomsel=mobile_ref.select_atoms(eqref_selection).select_atoms("name CA")
                        trans2=mobile_ref_atomsel.center_of_mass()- mobile_orig_atomsel.center_of_mass()
                        mobile_orig.atoms.translate(trans2)
                        # Obtain correct transl
                        final_trans=np.add(trans,trans2)
                        #self.stdout.write(self.style.SUCCESS("Angle: %s"%list(r_angl)))
                        #self.stdout.write(self.style.SUCCESS("Trans: %s"%list(final_trans)))
                        with open(matrix_datafile, 'wb') as filehandle:  
                            # store the data as binary data stream
                            pickle.dump([r_angl,final_trans], filehandle)

                        #to open:
        #                    with open(settings.MEDIA_ROOT + 'Precomputed/ED_map/dyn_4_transfmatrix.data', 'rb') as filehandle:  
        #                        (r_anglpre,transpre) = pickle.load(filehandle)

                        #remove tmp files
                            for filenm in os.listdir(tmp_path):
                                if filenm.startswith("dyn_%s"%dyn_id) or filenm==pdbid+".pdb":
                                    os.remove(os.path.join(tmp_path,filenm))

                        self.stdout.write(self.style.SUCCESS("Transformation matrix successfully generated at %s"%matrix_datafile))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(e))

                gc.collect()
