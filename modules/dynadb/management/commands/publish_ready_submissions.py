from django.core.management.base import BaseCommand, CommandError
from modules.dynadb.models import DyndbSubmission, DyndbProtein, DyndbCompound, DyndbDynamics, DyndbMolecule,  DyndbComplexExp, DyndbComplexMolecule, DyndbModel
from modules.dynadb.models import DyndbSubmissionProtein, DyndbSubmissionMolecule, DyndbSubmissionModel, DyndbFilesMolecule, DyndbFilesModel , DyndbFilesDynamics, DyndbFiles
from modules.dynadb.views import get_file_name, get_file_name_dict, get_file_paths
from django.db.models import Count, F, Value as V, SmallIntegerField
import re
from os import path, rename as os_rename
import shutil

class Command(BaseCommand):
    help = 'Publishes main objects whose submission is set to "ready for publication". BACKUP DB before use.'
    __object_type_dict = {
        'protein'          : {'dbobject': DyndbProtein,         'ref_obj_id_field': 'id_protein',  'path_to_ref': 'dyndbreferencesprotein',  'path_to_submission': 'dyndbsubmissionprotein',                                 'sub_dbobject': DyndbSubmissionProtein,  'submission_id_field': 'submission_id', 'path_from_submission': 'protein_id'},
        'compound'         : {'dbobject': DyndbCompound,        'ref_obj_id_field': 'id_compound', 'path_to_ref': 'dyndbreferencescompound', 'path_to_submission': 'dyndbmolecule__dyndbsubmissionmolecule',                 'sub_dbobject': DyndbSubmissionMolecule, 'submission_id_field': 'submission_id', 'path_from_submission': 'molecule_id__id_compound'},
        'molecule'         : {'dbobject': DyndbMolecule,        'ref_obj_id_field': 'id_molecule', 'path_to_ref': 'dyndbreferencesmolecule', 'path_to_submission': 'dyndbsubmissionmolecule',                                'sub_dbobject': DyndbSubmissionMolecule, 'submission_id_field': 'submission_id', 'path_from_submission': 'molecule_id'},
        'complex'          : {'dbobject': DyndbComplexExp,      'ref_obj_id_field': None,          'path_to_ref': None,                      'path_to_submission': 'dyndbcomplexmolecule__dyndbmodel__dyndbsubmissionmodel', 'sub_dbobject': DyndbSubmissionModel,    'submission_id_field': 'submission_id', 'path_from_submission': 'model_id__id_complex_molecule__id_complex_exp'},
        'complex_molecule' : {'dbobject': DyndbComplexMolecule, 'ref_obj_id_field': None,          'path_to_ref': None,                      'path_to_submission': 'dyndbmodel__dyndbsubmissionmodel',                       'sub_dbobject': DyndbSubmissionModel,    'submission_id_field': 'submission_id', 'path_from_submission': 'model_id__id_complex_molecule'},
        'model'            : {'dbobject': DyndbModel,           'ref_obj_id_field': 'id_model',    'path_to_ref': 'dyndbreferencesmodel',    'path_to_submission': 'dyndbsubmissionmodel',                                   'sub_dbobject': DyndbSubmissionModel,    'submission_id_field': 'submission_id', 'path_from_submission': 'model_id'},
        'dynamics'         : {'dbobject': DyndbDynamics,        'ref_obj_id_field': 'id_dynamics', 'path_to_ref': 'dyndbreferencesdynamics', 'path_to_submission': None,                                                     'sub_dbobject': DyndbDynamics,           'submission_id_field': 'submission_id', 'path_from_submission': None},
    }
    
    __filenamedict=get_file_name_dict()
    
    __numberre = re.compile(r'(\d+)')
    __molre = re.compile(r'mol',flags=re.IGNORECASE)
    __imgre = re.compile(r'ima?g',flags=re.IGNORECASE)
            
    __coorre = re.compile(r'coor',flags=re.IGNORECASE)
    __strre = re.compile(r'str',flags=re.IGNORECASE)
    __topre = re.compile(r'top',flags=re.IGNORECASE)
    __trjre = re.compile(r'tra?j',flags=re.IGNORECASE)
    __prmre = re.compile(r'(pa?ra?m)|(par)',flags=re.IGNORECASE)
    __otherre = re.compile(r'other',flags=re.IGNORECASE)
    
    def add_arguments(self, parser):
        parser.add_argument(
           'submission_id',
            nargs='*',
            action='store',
            default=False,
            help='Submission id(s) to publish. All submissions with "ready for publication" flag will be published if no id(s) are provided.',
        )
        parser.add_argument(
            '--set-ready-only',
            action='store_true',
            dest='set-ready-only',
            default=False,
            help='Sets submission flags from "closed" to "ready for publication".',
        )
        parser.add_argument(
            '--repair',
            action='store_true',
            dest='repair',
            default=False,
            help='Repairs coherence between submission flags. Preference order is "published" > "ready for publication" > "closed".',
        )
        parser.add_argument(
            '--ignore-references-check',
            action='store_false',
            dest='references-check',
            default=True,
            help='Publish entries even if they have no references.',
        )
        parser.add_argument(
            '--full',
            action='store_true',
            dest='full',
            default=False,
            help='Updates publication flags in main objects whose submission flag was already in "published. Preference order is "published" > "ready for publication" > "closed".',
        )
        parser.add_argument(
            '--publish-on-missing-submission',
            action='store_true',
            dest='publish-on-missing-submission',
            default=False,
            help='Publishes main objects whose submission is missing or never had one. It does not perform any checks.',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            default=False,
            help='Forces publishing (or sets "ready for publication" flag) without doing any check. DANGEROUS, especially with non "closed" submissions or if no id(s) are provided.'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            dest='verbose',
            default=False,
            help='Gives details about the files published.'
        )
    
            
    
    def handle(self, *args, **options):
        
        def references_check(submission_ids=None,set_ready_only=False):
            '''Checks if objects have at least one reference.'''
            if set_ready_only:
                field = 'is_closed'
            else:
                field = 'is_ready_for_publication'
            
            #Do only for objects that have references
            object_types = filter(lambda object_type: self.__object_type_dict[object_type]['path_to_ref'] is not None,self.__object_type_dict)
            object_ref_count = dict()
            sub_ids_to_exclude = set()
            header_printed = False
            for object_type in object_types:
                #Create dictionary for .filter() parameters
                filter_dict = dict()
                #Check only if submission is closed or ready for publication 
                filter_dict[self.__object_type_dict[object_type]['submission_id_field']+'__'+field] = True

                subobj2 = self.__object_type_dict[object_type]['sub_dbobject'].objects.filter(**filter_dict)
                
                if submission_ids is not None:
                    subobj2 = subobj2.filter(submission_id__in = submission_ids)
                #Build query from submission_[object]__submission_id from to [object]__[object]_id
                submission_id_field = self.__object_type_dict[object_type]['submission_id_field']
                object_id_path_list = [self.__object_type_dict[object_type]['path_from_submission'],'pk']
                object_id_path_list = filter(lambda x: not(x is None or x == ''), object_id_path_list)
                object_id_path = '__'.join(object_id_path_list)
                subobj2 = subobj2.annotate(object_id=F(object_id_path))
                #Build query from submission_[object]__submission_id from to reference_[object]__[object]_id
                object_id_ref_path_list = [self.__object_type_dict[object_type]['path_from_submission'],self.__object_type_dict[object_type]['path_to_ref'],\
                self.__object_type_dict[object_type]['ref_obj_id_field']]
                object_id_ref_path_list = filter(lambda x: not(x is None or x == ''), object_id_ref_path_list)
                object_id_ref_path = '__'.join(object_id_ref_path_list)
                #Count object_id. ref_id and object_id must have not null and unique together.
                subobj2 = subobj2.annotate(ref_count=Count(object_id_ref_path)).order_by(submission_id_field)
                object_ref_count[object_type] = tuple(subobj2.values('object_id','ref_count',submission_id_field))
                
                #Get submission IDs that did not past the check.
                rows = filter(lambda row: row['ref_count'] == 0,object_ref_count[object_type])
                if rows and not header_printed:
                    self.stdout.write(self.style.NOTICE('Following submission IDs were ignored due to missing references:'))
                    header_printed = True
                for row in rows:
                    sub_id = row[submission_id_field]
                    sub_ids_to_exclude.add(sub_id)
                    self.stdout.write(self.style.NOTICE('"Submission ID": %d, "object_type": "%s", "ID": %s') % (sub_id,object_type,str(row['object_id'])))
            return sub_ids_to_exclude
            
        def publish_on_missing_submission():
            '''Publishes main objects that are not link to any submission.'''
            object_ids = dict()
            header_printed = False
            for object_type in self.__object_type_dict:
                
                mainobj = self.__object_type_dict[object_type]['dbobject'].objects.all()
                path_to_submission_id_list = [self.__object_type_dict[object_type]['path_to_submission'],\
                self.__object_type_dict[object_type]['submission_id_field']]
                path_to_submission_id_list = filter(lambda x: not(x is None or x == ''), path_to_submission_id_list)
                path_to_submission_id = '__'.join(path_to_submission_id_list)
                
                mainobj = mainobj.filter(**{path_to_submission_id:None})
                mainobj = mainobj.exclude(is_published=True)
                object_ids[object_type] = set(mainobj.values_list("pk",flat=True))
                mainobj_to_update = self.__object_type_dict[object_type]['dbobject'].objects.filter(pk__in=object_ids[object_type])
                mainobj_to_update.update(is_published=True)
            
                if object_ids[object_type]:
                    if not header_printed:
                        self.stdout.write(self.style.SUCCESS('Following objects were publish due to missing submissions:'))
                        header_printed = True
                    self.stdout.write(self.style.SUCCESS('"object_type": "%s", "IDs":\n%s') % (object_type,','.join(str(x) for x in object_ids[object_type])))   
                    
        def get_file_subtypes_dict():
            file_subtypes_dict = dict()
            
            mol_types=dict(DyndbFilesMolecule.filemolec_types)
            file_subtypes_dict["molecule"] = {}
            for typenum in mol_types:
                type_text = mol_types[typenum]
                if self.__imgre.search(type_text):
                    subtype = "image"
                    m = self.__numberre.search(type_text)
                    if m:
                        imgsize=int(m.group(0))
                    else:
                        imgsize=300
                elif self.__molre.search(type_text):
                    subtype = "molecule"
                    imgsize = None
                else:
                    raise ValueError('Non-defined type: "'+type_text+'".')
                file_subtypes_dict["molecule"][typenum] = {'subtype':subtype,'imgsize':imgsize}
                
            file_subtypes_dict["dynamics"] = {}
            dyn_types=dict(DyndbFilesDynamics.file_types)
            for typenum in dyn_types:
                type_text = dyn_types[typenum]
                if self.__coorre.search(type_text) or self.__coorre.search(type_text):
                    subtype = "pdb"
                elif self.__topre.search(type_text):
                    subtype = "topology"
                elif self.__trjre.search(type_text):
                    subtype = "trajectory"
                elif self.__prmre.search(type_text):
                    subtype = "parameters"
                elif self.__otherre.search(type_text):
                    subtype = "other"
                else:
                    raise ValueError('Non-defined type: "'+type_text+'".')    
                file_subtypes_dict["dynamics"][typenum] = {'subtype':subtype,'imgsize':None}
            file_subtypes_dict["model"] = {}
            file_subtypes_dict["model"][0] = {'subtype':"pdb",'imgsize':None} 
            
            return file_subtypes_dict
        
        def publish_files(submission_ids=None,object_id_dict=None,verbose=False):
            objects = ["molecule","model","dynamics"]
            path_to_files_dict = {"molecule":{"file_obj":"dyndbfilesmolecule","file_type_field":"type"},
            "model":{"file_obj":"dyndbfilesmodel","file_type_field":None},
            "dynamics":{"file_obj":"dyndbfilesdynamics","file_type_field":"type"}}
            file_subtypes_dict = get_file_subtypes_dict()
            work_dict = dict()
            if submission_ids is not None and object_id_dict is not None:
                raise ValueError("Only one keyword, 'submission_ids' or 'object_id_dict', can be defined.")
            
            elif submission_ids is not None:
                for obj in objects:
                    path_to_submission_id_list = [self.__object_type_dict[obj]['path_to_submission'],\
                    self.__object_type_dict[obj]['submission_id_field']]
                    path_to_submission_id_list = filter(lambda x: not(x is None or x == ''), path_to_submission_id_list)
                    path_to_submission_id = '__'.join(path_to_submission_id_list)
                    
                    work_dict[obj] = {}
                    work_dict[obj]['dbobject'] = self.__object_type_dict[obj]['dbobject'].objects.filter(**{path_to_submission_id+'__in':submission_ids})
                    
                
            elif object_id_dict is not None:
                if object_id_dict.keys() != set(objects):
                    raise ValueError("'object_id_dict' keyword must be a dictionary with keys: "+','.join(objects)+'.')
                for obj in objects:
                    work_dict[obj]['dbobject'] = self.__object_type_dict[obj]['dbobject'].objects.filter(pk__in=object_id_dict[obj])
            else:
                raise ValueError("One keyword, 'submission_ids' or 'object_id_dict', must be defined.")
            for obj in objects:
                dbobj = work_dict[obj]['dbobject']
                path_to_file_obj = path_to_files_dict[obj]["file_obj"]
                path_to_id_files = path_to_file_obj+'__id_files'
                path_to_filepath = path_to_id_files+'__filepath'
                path_to_ext = path_to_id_files+'__id_file_types__extension'
                dbobj = dbobj.annotate(object_id=F('pk'),id_files=F(path_to_id_files),filepath=F(path_to_filepath),ext=F(path_to_ext))
                if len(file_subtypes_dict[obj]) == 1:
                    file_type = list(file_subtypes_dict[obj])[0]
                    if isinstance(file_type, int):
                        output_field=SmallIntegerField()
                    else:
                        output_field=TextField()
                    dbobj = dbobj.annotate(file_type=V(file_type,output_field=output_field))
                else:
                    path_to_file_type = path_to_file_obj +'__'+path_to_files_dict[obj]["file_type_field"]
                    dbobj = dbobj.annotate(file_type=F(path_to_file_type))
                dbobj = dbobj.values('object_id','id_files','file_type','filepath','ext')
                newdir = get_file_paths(obj,url=False,submission_id=None)
                newurlroot = get_file_paths(obj,url=True,submission_id=None)
                for fileobj in  dbobj:
                    subtype = file_subtypes_dict[obj][fileobj['file_type']]['subtype']
                    imgsize = file_subtypes_dict[obj][fileobj['file_type']]['imgsize']

                    newfilename = get_file_name(objecttype=obj,fileid=fileobj['id_files'],objectid=fileobj['object_id'],ext=fileobj['ext'],forceext=False,subtype=subtype,imgsize=imgsize)
                    newpath = path.join(newdir,newfilename)
                    newurl = path.join(newurlroot,newfilename)
                    if newpath != fileobj['filepath']:
                        if path.isfile(fileobj['filepath']):
                            self.stdout.write(''.join(('Moving "',fileobj['filepath'],'" to "',newpath,'".')))
                            try:
                                os_rename(fileobj['filepath'],newpath)
                            except PermissionError:
                                shutil.copy2(fileobj['filepath'],newpath)
                                self.stdout.write(self.style.NOTICE("Copied instead of moved due to permission error: %s" % fileobj['filepath']))
                    try:
                        DyndbFiles.objects.filter(pk=fileobj['id_files']).update(filename=newfilename,url=newurl,filepath=newpath)
                    except:
                        if newpath != fileobj['filepath']:
                            try:
                                os_rename(newpath,fileobj['filepath'])
                            except PermissionError:
                                shutil.copy2(newpath,fileobj['filepath'])
                                self.stdout.write(self.style.NOTICE("Copied instead of moved due to permission error: %s" % newpath))
                                
                        raise
                    
        if options['set-ready-only'] and options['full']:
            raise CommandError('Incompatible options "--set-ready-only" and "--full".')
        subobj = DyndbSubmission.objects.all()
        
        if options['publish-on-missing-submission']:
            self.stdout.write('You are going to apply changes to ALL objects that are not currently linked to a submission. ' \
            'We recommend backing up your database before you proceed. Would you like to continue?[y/n]')
            while 1:
                answer = input().lower()
                if answer in {'y','yes'}:
                    publish_on_missing_submission()
                    break
                elif answer in {'n','no'}:
                    break
            
        
        
        
        if options['submission_id']:
            subobj = subobj.filter(pk__in=options['submission_id'])
            
        else:
            if options['force']:
                self.stdout.write('You are going to apply changes to ALL submissions and their dependences. ' \
                'We recommend backing up your database before you proceed. You probably do not want to do that. Would you like to continue?[y/n]')
            else:
                if options['set-ready-only']:
                    word = 'CLOSED'
                else:
                    word = 'READY FOR PUBLICATION'
                self.stdout.write('You are going to apply changes to ALL %s submissions and their dependences. ' \
                'We recommend backing up your database before you proceed. Would you like to continue?[y/n]' % word)
            while 1:
                answer = input().lower()
                if answer in {'y','yes'}:
                    break
                elif answer in {'n','no'}:
                    return
        if options['repair']:
           
           if options['set-ready-only']:
               repair_subobj = subobj.filter(is_closed=False,is_ready_for_publication=True)
           else:
               repair_subobj = subobj.filter(is_published=True).exclude(is_closed=True,is_ready_for_publication=True)
           repair_subobj.update(is_closed=True,is_ready_for_publication=True)
        
        # --force disables references-check
        if options['references-check'] and not options['force']:
            kargs_dict = {'set_ready_only':options['set-ready-only'],'submission_ids':None}
            if options['submission_id']:
                kargs_dict['submission_ids'] = options['submission_id']
            sub_ids_to_exclude = references_check(**kargs_dict)
        else:
            sub_ids_to_exclude = ()
           
        if options['set-ready-only']:
            # --force disables checking if submission is closed on --set-ready-only
            if not options['force']:
                subobj = subobj.filter(is_closed=True)
                subobj = subobj.exclude(pk__in=sub_ids_to_exclude)
            subobj = subobj.exclude(is_ready_for_publication=True)
            submission_ids = sorted(subobj.values_list('pk',flat=True))
            
            if len(submission_ids) > 0:
                subobj.update(is_closed=True,is_ready_for_publication=True)
                msg = 'Successfully set "ready for publication" flag on submission IDs:\n'
            else:
                msg = 'No pending closed submissions found.'
            
            
        else:
            # --force disables checking if submission is ready for publication
            if not options['force']:
                subobj = subobj.exclude(pk__in=sub_ids_to_exclude)
            subobj = subobj.exclude(is_published=True)
            submission_ids = sorted(subobj.values_list('pk',flat=True))
            if len(submission_ids) > 0:
                subobj.update(is_closed=True,is_ready_for_publication=True,is_published=True)
                msg = 'Successfully published submission IDs:\n'

            else:
                msg = 'No submissions pending for publication found.'
            
            if len(submission_ids) > 0 or options['full']:
                if options['full']:
                    submission_ids_full = options['submission_id']
                else:
                    submission_ids_full = submission_ids
                for object_type in self.__object_type_dict:
                    mainobj = self.__object_type_dict[object_type]['dbobject'].objects.all()
                    path_to_submission_id_list = [self.__object_type_dict[object_type]['path_to_submission'],\
                    self.__object_type_dict[object_type]['submission_id_field']]
                    path_to_submission_id_list = filter(lambda x: not(x is None or x == ''), path_to_submission_id_list)
                    path_to_submission_id = '__'.join(path_to_submission_id_list)
                    if options['submission_id']:
                        mainobj = mainobj.filter(**{path_to_submission_id+'__in':submission_ids_full})
                    if options['full']:
                        mainobj = mainobj.filter(**{path_to_submission_id+'__is_published':True})
                    mainobj.update(is_published=True)
                publish_files(submission_ids=submission_ids_full)
            
        self.stdout.write(self.style.SUCCESS('%s%s' % (msg,','.join(str(x) for x in submission_ids))))        
            
        if options['submission_id']:
            submission_ids_set = { str(a) for a in submission_ids}
            ignored_submission_ids = sorted(set(options['submission_id']).difference(submission_ids_set))
            if options['set-ready-only']:
                msg= 'Following submission IDs were ignored for setting "ready for publication" flag'
            else:
                msg= 'Following submission IDs were ignored for publication'
            self.stdout.write(self.style.NOTICE('%s:\n%s' % (msg,','.join(str(x) for x in ignored_submission_ids))))

