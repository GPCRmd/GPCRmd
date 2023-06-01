import requests
import re
import sys
import time
import urllib
import certifi
from .customized_errors import StreamSizeLimitError, StreamTimeoutError, ParsingError, InvalidPNGFileError
from requests.exceptions import HTTPError,ConnectionError,Timeout,TooManyRedirects
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse, JsonResponse, StreamingHttpResponse, HttpResponseForbidden
from defusedxml.ElementTree import DefusedXMLParser as xmlparser
from io import BytesIO
from .molecule_properties_tools import open_molecule_file
from html.parser import HTMLParser

from PIL import Image
import warnings
warnings.simplefilter('error', Image.DecompressionBombWarning)
import numpy as np
from tempfile import TemporaryFile

CIDS_TYPES = {'all', 'active', 'inactive', 'standardized', \

'component','original', 'parent', 'component', 'similar_2d', 'similar_3d', \

'same_stereo', 'same_isotopes', \

'same_connectivity', 'same_tautomer', \

'same_parent', 'same_parent_stereo', 'same_parent_isotopes', \

'same_parent_connectivity', 'same_parent_tautomer'}


def pubchem_errdata_2_response(errdata,data=None):
    if 'Error' in errdata.keys():
          if data is not None:
              if 'Fault'not in data.keys():
                  data = None
              else:
                  if 'Code' not in data['Fault'].keys():
                      data['Fault']['Code'] = 'unknown'
                  if 'Message' not in data['Fault'].keys():
                      data['Message']['Code'] = 'None'
                  if 'Details' not in data['Fault'].keys():
                      data['Fault']['Details'] = ['None']
          if errdata['ErrorType'] == 'HTTPError':
            if errdata['status_code'] == 404 or errdata['status_code'] == 410:
                msg = 'No data found for this molecule in PubChem.\n'
                if data is not None:
                    msg += 'Code: '+data['Fault']['Code']+'\nMessage: '+data['Fault']['Message']+'\nDetails: '+'\n'.join(data['Fault']['Details'])
                response = HttpResponseNotFound(msg,content_type='text/plain')
            else:
              msg = 'Problem downloading from PubChem:\nStatus: '+str(errdata['status_code']) \
                +'\n'+errdata['reason']+'\n'
              if data is not None:
                msg += 'Code: '+data['Fault']['Code']+'\nMessage: '+data['Fault']['Message']+'\nDetails: '+'\n'.join(data['Fault']['Details'])
              response = HttpResponse(msg,status=502,content_type='text/plain')
          elif errdata['ErrorType'] == 'StreamSizeLimitError' or errdata['ErrorType'] == 'StreamTimeoutError' \
            or errdata['ErrorType'] == 'ParsingError':
            response = HttpResponse('Problem downloading from PubChem:'\
                +'\n'+errdata['reason'],status=502,content_type='text/plain')
          elif errdata['ErrorType'] == 'InvalidPNGFileError':
            response = HttpResponse('Problem downloading from PubChem:'\
                +'\n'+errdata['reason'],status=502,content_type='text/plain') 
          elif errdata['ErrorType'] == 'Internal':
            response = HttpResponse('Unknown internal error.',status=500,content_type='text/plain')
          else:
            response = HttpResponse('Cannot connect to PubChem PUG server:\n'+errdata['reason'],status=504,content_type='text/plain')
    else:
        response = None
    return response


def chembl_errdata_2_response(errdata,data=None):
    if 'Error' in errdata.keys():
          if errdata['ErrorType'] == 'HTTPError':
            if errdata['status_code'] == 404 or errdata['status_code'] == 410:
                msg = 'No data found for this molecule in ChEMBL.\n'
                response = HttpResponseNotFound(msg,content_type='text/plain')
            else:
              msg = 'Problem downloading from ChEMBL:\nStatus: '+str(errdata['status_code']) \
                +'\n'+errdata['reason']+'\n'
              response = HttpResponse(msg,status=502,content_type='text/plain')
          elif errdata['ErrorType'] == 'StreamSizeLimitError' or errdata['ErrorType'] == 'StreamTimeoutError' \
            or errdata['ErrorType'] == 'ParsingError':
            response = HttpResponse('Problem downloading from ChEMBL:'\
                +'\n'+errdata['reason'],status=502,content_type='text/plain')
          elif errdata['ErrorType'] == 'Internal':
            response = HttpResponse('Unknown internal error.',status=500,content_type='text/plain')
          else:
            response = HttpResponse('Cannot connect to ChEMBL web server:\n'+errdata['reason'],status=504,content_type='text/plain')
    else:
        response = None
    return response


def retreive_compound_data_pubchem_post_json(searchproperty,searchvalue,outputproperty=None,operation='property',preoperation=None,extras=None):
    errdata = dict()
    data = dict()
    do_not_skip_on_debug = False
    try:
        
        URL = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/'
        args = []
        extrasstr = ''
        if preoperation is not None:
            args.append(str(preoperation))
        args.append(str(searchproperty))
        if operation is not None:
            args.append(str(operation))
        if outputproperty is not None:
            args.append(str(outputproperty))
        
        if extras:
            extraargs = []
            keys = extras.keys()
            for key in keys:
                if isinstance(extras[key],(list,tuple)):
                    extrastr = ','.join([str (i) for i in extras[key]])
                else:
                    extrastr = str(extras[key])
                extraargs.append(str(key) + '=' + urllib.parse.quote(extrastr,safe=''))
            extrasstr = '?' + '&'.join(extraargs)
        postdata = {str(searchproperty) : str(searchvalue)} 
        response = requests.post(URL+'/'.join(args)+'/JSON'+extrasstr,data=postdata,timeout=30,stream=False,verify=True)
        data = response.json()
        response.raise_for_status()
        
        
        response.close()
        return data
    
    except HTTPError:
      errdata['Error'] = True
      errdata['ErrorType'] = 'HTTPError'
      errdata['status_code'] = response.status_code
      errdata['reason'] = response.reason
    except ConnectionError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'ConnectionError'
      errdata['reason'] = 'Cannot connect.'
    except Timeout as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'Timeout'
      errdata['reason'] = 'Timeout exceeded.'
    except TooManyRedirects as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'TooManyRedirects'
      errdata['reason'] = 'Too many redirects.'
    except StreamSizeLimitError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'StreamSizeLimitError'
      errdata['reason'] = str(e)
    except StreamTimeoutError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'StreamTimeoutError'
      errdata['reason'] = str(e)

    except:
      errdata['Error'] = True
      errdata['ErrorType'] = 'Internal'
      errdata['reason'] = ''
      do_not_skip_on_debug = True
      raise
    finally:
      try:
        response.close()
      except:
        pass
      if not (settings.DEBUG and do_not_skip_on_debug):
        return (data,errdata)
    
    
def retreive_compound_data_pubchem_json(searchproperty,searchvalue,outputproperty=None,operation='property',extras=None):
    URL = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/'
    args = []
    args.append(str(searchproperty))
    args.append(urllib.parse.quote(str(searchvalue),safe=''))
    args.append(str(operation))
    if outputproperty is not None:
        args.append(str(outputproperty))
    extrasstr = ''
    if extras:
        extraargs = []
        keys = extras.keys()
        for key in keys:
            extraargs.append(str(key) + '=' + urllib.parse.quote(str(extras[key]),safe=''))
        extrasstr = '?' + ','.join(extraargs)
    response = requests.get(URL+'/'.join(args)+'/JSON'+extrasstr,timeout=30,stream=False,verify=True)
    if response.status_code != 404:
        response.raise_for_status()
    
    jsondata = response.json()

    response.close()
    return jsondata
    
def retreive_compound_data_pubchem_txt(searchproperty,searchvalue,outputproperty=None,operation='property',limit=0):
    URL = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/'
    args = []
    args.append(str(searchproperty))
    args.append(urllib.parse.quote(str(searchvalue),safe=''))
    args.append(str(operation))
    if outputproperty is not None:
        args.append(str(outputproperty))
    if limit is None:
        limit = 0
    response = requests.get(URL+'/'.join(args)+'/TXT',timeout=30,stream=True,verify=True)
    if response.status_code != 404:
        response.raise_for_status()
    encoding = response.encoding
    lines = response.iter_lines()
    
    if limit > 0:
        data = []
        counter = 1
        for line in lines:
            if counter > limit:
                break
            uline = line.decode(encoding)
            data.append(uline.strip())
            counter += 1
    else:
        data = [line.strip() for line in response.text.split('\n')]
    
    if data[-1] == '':
        data.pop()

    response.close()
    return data

def replace_png_background_color(input_png,input_type='file',replaced_background_color=(245,245,245),replacing_background_color=(255,255,255),outputfile=None):
    """This function replaces grey background (default) RGB(245,245,245) of a PNG image. 
    input_file                      an str that can be  "file" or "bytes". Default='file'.
    input_png                       In the "input_file='file'" case, input can be an str with the path
                                    to the PNG file or a file-like object.
                                    In the "input_file='bytes'", input must be a bytes object with PNG file data.
    outputfile                      String with the path for the output file or a file-like object. If set to
                                    None, an a bytes object with PNG file data is returned. Default=None.
    replaced_background_color       iterable with three 0 to 255 RGB values. Default=(245,245,245) (pubchem PNG gray).
    replacing_background_color      iterable with three 0 to 255 RGB values. Default=(255,255,255) (white). 
    """       
    input_type_values = {'file','bytes'}
    input_type = input_type.lower()    

    if input_type not in input_type_values:
         raise ValueError('Invalid input_type "".' % (input_type))
    
    if input_type == 'bytes':
         input_png2 = BytesIO(input_png)
    else:
         input_png2 = input_png
    del input_png

    try:
    	im = Image.open(input_png2)
    except Exception as e:
        raise InvalidPNGFileError("Cannot read PNG file.")
    finally:
        if input_type == 'bytes':
            input_png2.close()
    
    del input_png2
    im = im.convert('RGB')
    data = np.array(im)
    del im
    red, green, blue = data.T
    background = (red == replaced_background_color[0]) & (green == replaced_background_color[1]) & (blue == replaced_background_color[2])
    del red
    del green
    del blue 
    data[background.T] = replacing_background_color
    
    im2 = Image.fromarray(data)
    del data
    if outputfile is None:
        output = BytesIO()
        im2.save(output,format='PNG')
        del im2
        output.flush()
        output.seek(0)
        outputdata = output.read()
        output.close()
        del output
        return outputdata
    
    im2.save(outputfile,format='PNG') 


def retreive_compound_png_pubchem(searchproperty,searchvalue,outputfile=None,width=300,height=300,replace_background_color=(255,255,255)):
    URL = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/'
    errdata = dict()
    data = None
    do_not_skip_on_debug = False
    SIZE_LIMIT = 52428800
    RECIEVE_TIMEOUT = 120
    try:
        args = []
        args.append(str(searchproperty))
        args.append(urllib.parse.quote(str(searchvalue),safe=''))
        response = requests.get(URL+'/'.join(args)+'/PNG?'+str(width)+'x'+str(height),timeout=30,stream=True,verify=True)
        response.raise_for_status()
        if outputfile:
            if replace_background_color is None:
              fileh = open(outputfile,'wb')
            else:
              fileh = TemporaryFile(dir=settings.FILE_UPLOAD_TEMP_DIR)
        else:
            data = b''
        size = 0
        start = time.time()
        chunks = response.iter_content(chunk_size=524288)
        for chunk in chunks:
            size += len(chunk)
            if size > SIZE_LIMIT:
                raise StreamSizeLimitError('response too large')
            if time.time() - start > RECIEVE_TIMEOUT:
                raise StreamTimeoutError('timeout reached')
            if outputfile:
                fileh.write(chunk)
            else:
                data += chunk
        response.close()
        if outputfile:
            if replace_background_color is not None:
                fileh.seek(0)
                replace_png_background_color(fileh,input_type='file',outputfile=outputfile)
            fileh.close()
        else:
            if replace_background_color is not None:
                data = replace_png_background_color(data,input_type='bytes')
            return data
    except HTTPError:
      errdata['Error'] = True
      errdata['ErrorType'] = 'HTTPError'
      errdata['status_code'] = response.status_code
      errdata['reason'] = response.reason
    except ConnectionError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'ConnectionError'
      errdata['reason'] = 'Cannot connect.'
    except Timeout as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'Timeout'
      errdata['reason'] = 'Timeout exceeded.'
    except TooManyRedirects as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'TooManyRedirects'
      errdata['reason'] = 'Too many redirects.'
    except StreamSizeLimitError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'StreamSizeLimitError'
      errdata['reason'] = str(e)
    except StreamTimeoutError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'StreamTimeoutError'
      errdata['reason'] = str(e)
    except InvalidPNGFileError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'InvalidPNGFileError'
      errdata['reason'] = "Cannot read PubChem downloaded PNG file."
    except:
      errdata['Error'] = True
      errdata['ErrorType'] = 'Internal'
      errdata['reason'] = ''
      do_not_skip_on_debug = True
      raise
    finally:
      try:
        response.close()
      except:
        pass
      try:
        fileh.close()
      except:
        pass
      if not (settings.DEBUG and do_not_skip_on_debug):
        return (data,errdata)
        
def retreive_compound_sdf_pubchem(searchproperty,searchvalue,outputfile=None,in3D=False):
    URL = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/'
    errdata = dict()
    data = None
    do_not_skip_on_debug = False
    SIZE_LIMIT = 52428800
    RECIEVE_TIMEOUT = 120
    args = []
    try:
        args.append(str(searchproperty))
        args.append(urllib.parse.quote(str(searchvalue),safe=''))
        if in3D:
            recordtype='3d'
        else:
            recordtype='2d'
        
        response = requests.get(URL+'/'.join(args)+'/SDF?record_type='+recordtype,timeout=30,stream=True,verify=True)
        response.raise_for_status()
        if outputfile:
            fileh = open(outputfile,'w+b')
        else:
            fileh = BytesIO(b'')
        size = 0
        start = time.time()
        chunks = response.iter_content(chunk_size=524288)
        for chunk in chunks:
            size += len(chunk)
            if size > SIZE_LIMIT:
                raise StreamSizeLimitError('response too large')
            if time.time() - start > RECIEVE_TIMEOUT:
                raise StreamTimeoutError('timeout reached')
            fileh.write(chunk)

        response.close()
        if not outputfile:
            data = fileh.read()
            fileh.close()
        fileh.seek(0)
        mol = open_molecule_file(fileh,filetype='sdf')
        del mol

        return(data,errdata)
           
          
    except HTTPError:
      errdata['Error'] = True
      errdata['ErrorType'] = 'HTTPError'
      errdata['status_code'] = response.status_code
      errdata['reason'] = response.reason
    except ConnectionError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'ConnectionError'
      errdata['reason'] = 'Cannot connect.'
    except Timeout as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'Timeout'
      errdata['reason'] = 'Timeout exceeded.'
    except TooManyRedirects as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'TooManyRedirects'
      errdata['reason'] = 'Too many redirects.'
    except StreamSizeLimitError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'StreamSizeLimitError'
      errdata['reason'] = str(e)
    except StreamTimeoutError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'StreamTimeoutError'
      errdata['reason'] = str(e)
    except ParsingError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'ParsingError'
      errdata['reason'] = str(e)
    except:
      errdata['Error'] = True
      errdata['ErrorType'] = 'Internal'
      errdata['reason'] = ''
      do_not_skip_on_debug = True
      raise
    finally:
      try:
        response.close()
      except:
        pass
      try:
        fileh.close()
      except:
        pass
      if not (settings.DEBUG and do_not_skip_on_debug):
        return(data,errdata)    


def check_chembl_up():
    URL = 'https://www.ebi.ac.uk/chembl/api/data/status.json'
    response = requests.get(URL,timeout=30,stream=False,verify=True)
    response.raise_for_status()
    data = response.json()
    response.close()
    if data["status"] == "UP":
        return True
    else:
        print("ChEMBL REST service not avaliable. Status: "+data["status"],sys.__stderr__)
        return False
        

def retreive_molecule_chembl_id_json(chemblid):
    URL = 'https://www.ebi.ac.uk/chembl/api/data/molecule/'
    data = None
    do_not_skip_on_debug = False 
    errdata = dict()
    try:
        if check_chembl_up():

            chemblstr = urllib.parse.quote(str(chemblid),safe='')
            
            response = requests.get(URL+chemblstr+'.json',timeout=30,stream=False,verify=True)
            response.raise_for_status()

            
            data = response.json()
            
            response.close()
            return (data,errdata)
    except HTTPError:
      errdata['Error'] = True
      errdata['ErrorType'] = 'HTTPError'
      errdata['status_code'] = response.status_code
      errdata['reason'] = response.reason
    except ConnectionError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'ConnectionError'
      errdata['reason'] = 'Cannot connect.'
    except Timeout as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'Timeout'
      errdata['reason'] = 'Timeout exceeded.'
    except TooManyRedirects as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'TooManyRedirects'
      errdata['reason'] = 'Too many redirects.'
    except StreamSizeLimitError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'StreamSizeLimitError'
      errdata['reason'] = str(e)
    except StreamTimeoutError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'StreamTimeoutError'
      errdata['reason'] = str(e)

    except:
      errdata['Error'] = True
      errdata['ErrorType'] = 'Internal'
      errdata['reason'] = ''
      do_not_skip_on_debug = True
      raise
    finally:
      try:
        response.close()
      except:
        pass
      if not (settings.DEBUG and do_not_skip_on_debug):
        return(data,errdata) 
        
   
def retreive_molecule_chembl_similarity_json(search_value,similarity=100,filterdict=dict()):
    URL = 'https://www.ebi.ac.uk/chembl/api/data/similarity/'
    data = None
    do_not_skip_on_debug = False 
    errdata = dict()
    try:
        if check_chembl_up():
            keys = filterdict.keys()
            
            args = []
            for key in keys:
                args.append(key+'='+urllib.parse.quote(str(filterdict[key]),safe=''))
                
            args.append('limit=300')
            args.append('format=json')

            response = requests.get(URL+urllib.parse.quote(str(search_value),safe='')+'/'+urllib.parse.quote(str(similarity),safe='')+'?'+'&'.join(args),timeout=30,stream=False,verify=True)
            response.raise_for_status()
            data = response.json()

            response.close()
            return(data,errdata)
            
    except HTTPError:
      errdata['Error'] = True
      errdata['ErrorType'] = 'HTTPError'
      errdata['status_code'] = response.status_code
      errdata['reason'] = response.reason
    except ConnectionError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'ConnectionError'
      errdata['reason'] = 'Cannot connect.'
    except Timeout as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'Timeout'
      errdata['reason'] = 'Timeout exceeded.'
    except TooManyRedirects as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'TooManyRedirects'
      errdata['reason'] = 'Too many redirects.'
    except StreamSizeLimitError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'StreamSizeLimitError'
      errdata['reason'] = str(e)
    except StreamTimeoutError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'StreamTimeoutError'
      errdata['reason'] = str(e)

    except:
      errdata['Error'] = True
      errdata['ErrorType'] = 'Internal'
      errdata['reason'] = ''
      do_not_skip_on_debug = True
      raise
    finally:
      try:
        response.close()
      except:
        pass
      if not (settings.DEBUG and do_not_skip_on_debug):
        return(data,errdata) 
    
def retreive_molecule_chembl_json(filterdict):
    URL = 'https://www.ebi.ac.uk/chembl/api/data/molecule/?'
    if check_chembl_up():
        keys = filterdict.keys()
        
        args = []
        for key in keys:
            args.append(key+'='+urllib.parse.quote(str(filterdict[key]),safe=''))
            
        args.append('limit=1000')
        args.append('format=json')

        response = requests.get(URL+'&'.join(args),timeout=30,stream=False,verify=True)
        if response.status_code != 404:
            response.raise_for_status()
        else:
            response.close()
            return None
        
        jsondata = response.json()

        response.close()
        return jsondata
    

def retreive_compound_png_chembl(chemblid,dimensions=300,outputfile=None):
    URL = 'https://www.ebi.ac.uk/chembl/api/data/image/'
    errdata = dict()
    data = None
    do_not_skip_on_debug = False
    SIZE_LIMIT = 52428800
    RECIEVE_TIMEOUT = 120
    try:
        if check_chembl_up():   
            response = requests.get(URL+str(chemblid)+'?dimensions='+str(dimensions)+'&format=png'+'&ignoreCoords=0'+'&engine=indigo',timeout=30,stream=True,verify=True)
            response.raise_for_status()
            if outputfile:
                fileh = open(outputfile,'wb')
            else:
                data = b''
            size = 0
            start = time.time()
            chunks = response.iter_content(chunk_size=524288)
            for chunk in chunks:
                size += len(chunk)
                if size > SIZE_LIMIT:
                    raise StreamSizeLimitError('response too large')
                if time.time() - start > RECIEVE_TIMEOUT:
                    raise StreamTimeoutError('timeout reached')
                if outputfile:
                    fileh.write(chunk)
                else:
                    data += chunk
            response.close()
            if outputfile:
                fileh.close()
            else:
                return data 
    except HTTPError:
      errdata['Error'] = True
      errdata['ErrorType'] = 'HTTPError'
      errdata['status_code'] = response.status_code
      errdata['reason'] = response.reason
    except ConnectionError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'ConnectionError'
      errdata['reason'] = 'Cannot connect.'
    except Timeout as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'Timeout'
      errdata['reason'] = 'Timeout exceeded.'
    except TooManyRedirects as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'TooManyRedirects'
      errdata['reason'] = 'Too many redirects.'
    except StreamSizeLimitError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'StreamSizeLimitError'
      errdata['reason'] = str(e)
    except StreamTimeoutError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'StreamTimeoutError'
      errdata['reason'] = str(e)

    except:
      errdata['Error'] = True
      errdata['ErrorType'] = 'Internal'
      errdata['reason'] = ''
      do_not_skip_on_debug = True
      raise
    finally:
      try:
        response.close()
      except:
        pass
      try:
        fileh.close()
      except:
        pass
      if not (settings.DEBUG and do_not_skip_on_debug):
        return(data,errdata) 

def list_unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def get_chembl_molecule_ids(datachembl,parents=False):
    ids = []
    try:
        for molecule in datachembl["molecules"]:
            if parents and "molecule_hierarchy" in molecule.keys() and molecule["molecule_hierarchy"]:
                if "parent_chembl_id" in molecule["molecule_hierarchy"].keys():
                    chembl_id = molecule["molecule_hierarchy"]["parent_chembl_id"]
            else:
                chembl_id =  molecule["molecule_chembl_id"]
            ids.append(int(chembl_id.replace('CHEMBL','')))
        ids = list_unique(ids)
    except:
        raise ParsingError("Cannot parse ChEMBL molecule information.")
    return ids

def get_chembl_prefname_synonyms(moljson):
    aliases = []
    aliases_lc = set()

    if "pref_name" in moljson:
        prefname = moljson["pref_name"]
        if prefname is not None:
            aliases_lc.add(prefname.lower())
    else:
        prefname = None

    if "molecule_synonyms" in moljson:
        syn_list = moljson["molecule_synonyms"]
        for syn in syn_list:
            if syn is not None:
                ssyn = syn["synonyms"].strip()
                lcsyn = ssyn.lower()
                if lcsyn not in aliases_lc:
                    aliases.append(ssyn)
                    aliases_lc.add(lcsyn)
    return prefname,aliases


class ChemblResultsUrl:
    #We are assuming 'results' and 'url' tags only appear once
    results_started = False
    url_started = False
    keep_parsing = True
    def start(self, tag, attrib):   # Called for each opening tag.
        if self.keep_parsing:
            if tag == 'results':
                self.results_started = True
            elif tag == 'url' and self.results_started:
                self.url_started = True
    def end(self, tag):            # Called for each closing tag.
        if self.keep_parsing:
            if tag == 'url' and self.results_started:
                self.results_started = True
                self.keep_parsing = False
            elif tag == 'results':
                self.results_started = True
                self.keep_parsing = False
    def data(self, data):
        if self.keep_parsing and self.url_started:
            self.results_url = data         # We do not need to do anything with data.
    def close(self):    # Called when all data has been parsed.

        return self.results_url

def chembl_get_compound_id_query_result_url(postdata,chembl_submission_url='https://www.ebi.ac.uk/chembl/compound/ids'):
    results_url = None
    do_not_skip_on_debug = False
    SIZE_LIMIT = 512000
    RECIEVE_TIMEOUT = 120
    errdata = dict()
    try:
        response = requests.post(chembl_submission_url,data=postdata,timeout=30,stream=False,verify=True)
        response.raise_for_status()
        encoding = response.encoding
        chunks = response.iter_content(chunk_size=524288)
        target = ChemblResultsUrl()
        parser = xmlparser(target=target)
        
        size = 0
        start = time.time()
        for chunk in chunks:
            size += len(chunk)
            if size > SIZE_LIMIT:
                raise StreamSizeLimitError('response too large')
            if time.time() - start > RECIEVE_TIMEOUT:
                raise StreamTimeoutError('timeout reached')
            chunk = chunk.decode(encoding)
            parser.feed(chunk)
            if not target.keep_parsing:
                break
        
        results_url = parser.close()
        
        if results_url is None:
            raise ParsingError("No query result url found.")
        results_url = results_url.replace(':','/')
        return(results_url,errdata)
    
    except HTTPError:
      errdata['Error'] = True
      errdata['ErrorType'] = 'HTTPError'
      errdata['status_code'] = response.status_code
      errdata['reason'] = response.reason
    except ConnectionError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'ConnectionError'
      errdata['reason'] = 'Cannot connect.'
    except Timeout as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'Timeout'
      errdata['reason'] = 'Timeout exceeded.'
    except TooManyRedirects as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'TooManyRedirects'
      errdata['reason'] = 'Too many redirects.'
    except StreamSizeLimitError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'StreamSizeLimitError'
      errdata['reason'] = str(e)
    except StreamTimeoutError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'StreamTimeoutError'
      errdata['reason'] = str(e)
    except ParsingError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'ParsingError'
      errdata['reason'] = str(e)
    except:
      errdata['Error'] = True
      errdata['ErrorType'] = 'Internal'
      errdata['reason'] = ''
      do_not_skip_on_debug = True
      raise
    finally:
      try:
        parser.close()
      except:
        pass
      try:
        response.close()
      except:
        pass
      if not (settings.DEBUG and do_not_skip_on_debug):
        return(results_url,errdata)
        
def chembl_get_compound_id_query_result_url(postdata,chembl_submission_url='https://www.ebi.ac.uk/chembl/compound/ids'):
    results_url = None
    do_not_skip_on_debug = False
    SIZE_LIMIT = 512000
    RECIEVE_TIMEOUT = 120
    errdata = dict()
    try:
        response = requests.post(chembl_submission_url,data=postdata,timeout=30,stream=False,verify=True)
        response.raise_for_status()
        encoding = response.encoding
        chunks = response.iter_content(chunk_size=524288)
        target = ChemblResultsUrl()
        parser = xmlparser(target=target)
        
        size = 0
        start = time.time()
        for chunk in chunks:
            size += len(chunk)
            if size > SIZE_LIMIT:
                raise StreamSizeLimitError('response too large')
            if time.time() - start > RECIEVE_TIMEOUT:
                raise StreamTimeoutError('timeout reached')
            chunk = chunk.decode(encoding)
            parser.feed(chunk)
            if not target.keep_parsing:
                break
        
        results_url = parser.close()
        
        if results_url is None:
            raise ParsingError("No query result url found.")
        results_url = results_url.replace(':','/')
        return(results_url,errdata)
    
    except HTTPError:
      errdata['Error'] = True
      errdata['ErrorType'] = 'HTTPError'
      errdata['status_code'] = response.status_code
      errdata['reason'] = response.reason
    except ConnectionError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'ConnectionError'
      errdata['reason'] = 'Cannot connect.'
    except Timeout as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'Timeout'
      errdata['reason'] = 'Timeout exceeded.'
    except TooManyRedirects as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'TooManyRedirects'
      errdata['reason'] = 'Too many redirects.'
    except StreamSizeLimitError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'StreamSizeLimitError'
      errdata['reason'] = str(e)
    except StreamTimeoutError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'StreamTimeoutError'
      errdata['reason'] = str(e)
    except ParsingError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'ParsingError'
      errdata['reason'] = str(e)
    except:
      errdata['Error'] = True
      errdata['ErrorType'] = 'Internal'
      errdata['reason'] = ''
      do_not_skip_on_debug = True
      raise
    finally:
      try:
        parser.close()
      except:
        pass
      try:
        response.close()
      except:
        pass
      if not (settings.DEBUG and do_not_skip_on_debug):
        return(results_url,errdata)


class ChemblUrlInspectCompoundDownloadMolHTMLParser(HTMLParser):
    def __init__(self,*args,getmol_url='/chembl/download_helper/getmol/',**kwargs):
        self.getmol_url = getmol_url
        self.url = None
        self.keep_parsing = True
        super(ChemblUrlInspectCompoundDownloadMolHTMLParser, self).__init__(*args, **kwargs)
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                
                if (attr[0] == 'href') and (attr[1].find(self.getmol_url) > -1):
                   self.url = attr[1]
                   self.keep_parsing = False

def chembl_get_molregno_from_html(chemblid,getmol_url='/chembl/download_helper/getmol/'):
    URL = "https://www.ebi.ac.uk/chembl/compound/inspect/"
    molregno = None
    do_not_skip_on_debug = False
    SIZE_LIMIT = 512000
    RECIEVE_TIMEOUT = 120
    errdata = dict()
    try:
        response = requests.get(URL+chemblid,timeout=30,stream=False,verify=True)
        response.raise_for_status()
        encoding = response.encoding
        chunks = response.iter_content(chunk_size=524288)
        parser = ChemblUrlInspectCompoundDownloadMolHTMLParser(getmol_url=getmol_url)
        
        size = 0
        start = time.time()
        for chunk in chunks:
            size += len(chunk)
            if size > SIZE_LIMIT:
                raise StreamSizeLimitError('response too large')
            if time.time() - start > RECIEVE_TIMEOUT:
                raise StreamTimeoutError('timeout reached')
            chunk = chunk.decode(encoding)
            parser.feed(chunk)
            if not parser.keep_parsing:
                break
        parser.close()
        href_url = parser.url
        m = re.search(re.escape(getmol_url)+r'(\d+)',href_url)
        if m:
            molregno = int(m.group(1))
        if molregno is None:
            raise ParsingError("Molecule structure molregno not found.")
        return(molregno,errdata)
    
    except HTTPError:
      errdata['Error'] = True
      errdata['ErrorType'] = 'HTTPError'
      errdata['status_code'] = response.status_code
      errdata['reason'] = response.reason
    except ConnectionError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'ConnectionError'
      errdata['reason'] = 'Cannot connect.'
    except Timeout as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'Timeout'
      errdata['reason'] = 'Timeout exceeded.'
    except TooManyRedirects as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'TooManyRedirects'
      errdata['reason'] = 'Too many redirects.'
    except StreamSizeLimitError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'StreamSizeLimitError'
      errdata['reason'] = str(e)
    except StreamTimeoutError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'StreamTimeoutError'
      errdata['reason'] = str(e)
    except ParsingError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'ParsingError'
      errdata['reason'] = str(e)
    except:
      errdata['Error'] = True
      errdata['ErrorType'] = 'Internal'
      errdata['reason'] = ''
      do_not_skip_on_debug = True
      raise
    finally:
      try:
        parser.close()
      except:
        pass
      try:
        response.close()
      except:
        pass
      if not (settings.DEBUG and do_not_skip_on_debug):
        return(molregno,errdata)
        
def retreive_compound_sdf_chembl(molregno,getmol_url='/chembl/download_helper/getmol/',outputfile=None):
    DOMAIN_URL = 'https://www.ebi.ac.uk'
    errdata = dict()
    data = None
    do_not_skip_on_debug = False
    SIZE_LIMIT = 52428800
    RECIEVE_TIMEOUT = 120
    args = []
    try:
        
        response = requests.get(DOMAIN_URL+getmol_url+str(molregno),timeout=30,stream=True,verify=True)
        response.raise_for_status()
        if outputfile:
            fileh = open(outputfile,'w+b')
        else:
            fileh = BytesIO(b'')
        size = 0
        start = time.time()
        chunks = response.iter_content(chunk_size=524288)
        for chunk in chunks:
            size += len(chunk)
            if size > SIZE_LIMIT:
                raise StreamSizeLimitError('response too large')
            if time.time() - start > RECIEVE_TIMEOUT:
                raise StreamTimeoutError('timeout reached')
            fileh.write(chunk)

        response.close()
        if not outputfile:
            data = fileh.read()
            fileh.close()
        fileh.seek(0)
        mol = open_molecule_file(fileh,filetype='sdf')
        del mol

        return(data,errdata)
           
          
    except HTTPError:
      errdata['Error'] = True
      errdata['ErrorType'] = 'HTTPError'
      errdata['status_code'] = response.status_code
      errdata['reason'] = response.reason
    except ConnectionError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'ConnectionError'
      errdata['reason'] = 'Cannot connect.'
    except Timeout as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'Timeout'
      errdata['reason'] = 'Timeout exceeded.'
    except TooManyRedirects as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'TooManyRedirects'
      errdata['reason'] = 'Too many redirects.'
    except StreamSizeLimitError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'StreamSizeLimitError'
      errdata['reason'] = str(e)
    except StreamTimeoutError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'StreamTimeoutError'
      errdata['reason'] = str(e)
    except ParsingError as e:
      errdata['Error'] = True
      errdata['ErrorType'] = 'ParsingError'
      errdata['reason'] = str(e)
    except:
      errdata['Error'] = True
      errdata['ErrorType'] = 'Internal'
      errdata['reason'] = ''
      do_not_skip_on_debug = True
      raise
    finally:
      try:
        response.close()
      except:
        pass
      try:
        fileh.close()
      except:
        pass
      if not (settings.DEBUG and do_not_skip_on_debug):
        return(data,errdata)
