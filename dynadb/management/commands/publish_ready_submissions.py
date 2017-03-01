from django.core.management.base import BaseCommand, CommandError
from dynadb.models import DyndbSubmission, DyndbProtein, DyndbCompound, DyndbDynamics, DyndbMolecule,  DyndbComplexExp, DyndbComplexMolecule, DyndbModel
from dynadb.models import DyndbSubmissionProtein, DyndbSubmissionMolecule, DyndbSubmissionModel
from django.db.models import Count, F



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
                subobj = subobj.filter(is_ready_for_publication=True)
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
            
        self.stdout.write(self.style.SUCCESS('%s%s' % (msg,','.join(str(x) for x in submission_ids))))        
            
        if options['submission_id']:
            ignored_submission_ids = sorted(set(options['submission_id']).difference(set(submission_ids)))
            if options['set-ready-only']:
                msg= 'Following submission IDs were ignored for setting "ready for publication" flag'
            else:
                msg= 'Following submission IDs were ignored for publication'
            self.stdout.write(self.style.NOTICE('%s:\n%s' % (msg,','.join(str(x) for x in ignored_submission_ids))))

