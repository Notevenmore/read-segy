from readsegy import read_bheader, read_ebcdic, num_traces
import tempfile
import textwrap
import hashlib
from datetime import datetime
import io
import os, re
import json

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def convertsegy(file):
  try:
      # membaca file
      file_content = file.read()
      file_io = io.BytesIO(file_content)
      with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file_io.read())
      binhead = read_bheader(temp_file.name)
      ns = binhead[0][7]

      # membaca file format ebcdic dalam segy file
      ebcdic = read_ebcdic(temp_file.name)
      ebcdic = textwrap.fill(str(ebcdic, 'utf-8'), 80)  # utf-8 remove b' character
      ebcdic_split_newline = ebcdic.split('\n')
      ebcdic_dict = {}
      for row in ebcdic_split_newline:
          row_split = row.split(' :')
          if len(row_split) > 1:
              key = row_split[0].split(maxsplit=1)[1].strip()
              value = row_split[1].strip()
              ebcdic_dict[key] = value
      
      # melakukan decrypt nama file
      m = hashlib.md5()
      m.update(temp_file.name.encode())
      x = m.hexdigest()
      ebcdic_dict['DECRYPT_KEY'] = x.upper()
      ebcdic_dict['DECRYPTION_TYPE'] = 'MD5'
 
      # melihat ukuran tracing file
      ntraces = int(num_traces(temp_file.name, ns))

      # Your dictionary with new values
      data = {
          'BA_LONG_NAME': ebcdic_dict.get('CLIENT', '') 
          if ebcdic_dict.get('CLIENT', '') 
          else (re.search(r'SURVEY\s([A-Za-z]+\s[A-Za-z]+\s?[A-Za-z]*)', ebcdic).group(1) 
                if re.search(r'SURVEY\s([A-Za-z]+\s[A-Za-z]+\s?[A-Za-z]*)', ebcdic) is not None 
                else ''),
          'BA_TYPE': 'BADAN USAHA',
          'AREA_ID': ebcdic_dict.get('AREA', "")
          if ebcdic_dict.get('CLIENT', '')
          else (re.search(r'SURVEY\s([A-Za-z]+\s[A-Za-z]+)', ebcdic).group(1) 
                if re.search(r'SURVEY\s([A-Za-z]+\s[A-Za-z]+)', ebcdic) is not None
                else ''),
          'AREA_TYPE': 'WILAYAH KERJA', 
          'ACQTN_SURVEY_NAME': ebcdic_dict.get('AREA/Prospect', ""), 
          'SHOT_BY': ebcdic_dict.get('RECORD BY', ""),
          'PROCESSING_COMPANY': ebcdic_dict.get('RECORD BY', ""),
          'START_DATE': datetime.strptime(ebcdic_dict.get('RECORD DATE', ''), '%d-%m-%Y').strftime('%d/%m/%Y') if ebcdic_dict.get('RECORD DATE', '') else '',
          'RCRD_REC_LENGTH': ebcdic_dict.get('RL', '').split(' ')[0] if 'RL' in ebcdic_dict and len(ebcdic_dict.get('RL', '').split(' ')) > 0 else ebcdic_dict.get('SI/RL', '').split('/')[1].strip().split(' ')[0] if '/' in ebcdic_dict.get('SI/RL', '') else '',
          'RCRD_REC_LENGTH_OUOM': (ebcdic_dict.get('RL', '').split(' ')[1] if len(ebcdic_dict.get('RL', '').split(' ')) > 1 else ''.join([i for i in ebcdic_dict.get('SI/RL', '').split('/')[1] if not i.isdigit()]).strip()  if len(ebcdic_dict.get('SI/RL', '').split('/')) > 1 else ''),
          'RCRD_SAMPLE_RATE': ''.join([i for i in ebcdic_dict.get('SI', '').split(' ')[0] if i.isdigit()]) if 'SI' in ebcdic_dict else ''.join([i for i in ebcdic_dict.get('SI/RL', '').split('/')[0] if i.isdigit()]),
          'RCRD_SAMPLE_RATE_OUOM': ebcdic_dict.get('SI', '').split(' ')[1] if 'SI' in ebcdic_dict and len(ebcdic_dict.get('SI', '').split(' ')) > 1 else ''.join([i for i in ebcdic_dict.get('SI/RL', '').split('/')[0] if not i.isdigit()]).strip(),
          'LINE_NAME': ebcdic_dict.get('LINE', '') 
              if ebcdic_dict.get('LINE', '') 
              else (re.search(r'LINE\s([A-Za-z0-9-]{3,})', ebcdic).group(1)
                  if re.search(r'LINE\s([A-Za-z0-9-]{3,})', ebcdic) is not None
                  else ''),
          'DIGITAL_FORMAT': os.path.basename(file.filename).split('.')[1],
          'STEP_TYPE': 'RAW FIELD',
          'ITEM_CATEGORY': '1. ACQUISITION',
          'ITEM_SUB_CATEGORY': '1.1. F - FIELD DATA', 
          'MEDIA_TYPE': 'EXTERNAL HARDISK',
          'FIELD_FILE_NUMBER': ebcdic_dict.get('FFID RANGE', ''),
          'FIRST_SEIS_POINT_ID': ebcdic_dict.get('SP RANGE', '').split('-')[0], #First SP
          'LAST_SEIS_POINT_ID': ebcdic_dict.get('SP RANGE', '').split('-')[1] if len(ebcdic_dict.get('SP RANGE', '').split(' ')) > 1 else '', #Last SP
          'SEIS_POINT_LABEL': 'SP',
          'POLARITY': 'NORMAL', # Need to be checked if not null data
          'BA_LONG_NAME_1': ebcdic_dict.get('CLIENT', ''),
          'BA_TYPE_1': 'BADAN USAHA',
          'DATA_STORE_NAME': '',
          'ORIGINAL_FILE_NAME': os.path.basename(file.filename),
          'DECRYPT_KEY': ebcdic_dict.get('DECRYPT_KEY', ''),
          'DECRYPTION_TYPE': 'MD5',
          'SW_APPLICATION_ID': '', 
          'APPLICATION_VERSION': '',
          'DIGITAL_SIZE': os.path.getsize(temp_file.name), 
          'DIGITAL_SIZE_UOM': 'BYTE',
          'REMARK': '',
          'SOURCE': '', 
          'QC_STATUS': 'TERVERIFIKASI OLEH SKK MIGAS',
          'CHECKED_BY_BA_ID': '3578144811980003',
      }

      data_ebcdic = {
          'BA_LONG_NAME': ebcdic_dict.get("CLIENT", ""),
          'AREA_ID': ebcdic_dict.get('AREA', ""),
          'ACQTN_SURVEY_NAME': ebcdic_dict.get('AREA/Prospect', ""), 
          'SHOT_BY': ebcdic_dict.get('RECORD BY', ""),
          'PROCESSING_COMPANY': ebcdic_dict.get('RECORD BY', ""),
          'START_DATE': datetime.strptime(ebcdic_dict.get('RECORD DATE', ''), '%d-%m-%Y').strftime('%d/%m/%Y') if ebcdic_dict.get('RECORD DATE', '') else '',
          'RCRD_REC_LENGTH': ebcdic_dict.get('RL', '').split(' ')[0] if 'RL' in ebcdic_dict and len(ebcdic_dict.get('RL', '').split(' ')) > 0 else ebcdic_dict.get('SI/RL', '').split('/')[1].strip().split(' ')[0] if '/' in ebcdic_dict.get('SI/RL', '') else '',
          'RCRD_REC_LENGTH_OUOM': (ebcdic_dict.get('RL', '').split(' ')[1] if len(ebcdic_dict.get('RL', '').split(' ')) > 1 else ''.join([i for i in ebcdic_dict.get('SI/RL', '').split('/')[1] if not i.isdigit()]).strip()  if len(ebcdic_dict.get('SI/RL', '').split('/')) > 1 else ''),
          'RCRD_SAMPLE_RATE': ''.join([i for i in ebcdic_dict.get('SI', '').split(' ')[0] if i.isdigit()]) if 'SI' in ebcdic_dict else ''.join([i for i in ebcdic_dict.get('SI/RL', '').split('/')[0] if i.isdigit()]),
          'RCRD_SAMPLE_RATE_OUOM': ebcdic_dict.get('SI', '').split(' ')[1] if 'SI' in ebcdic_dict and len(ebcdic_dict.get('SI', '').split(' ')) > 1 else ''.join([i for i in ebcdic_dict.get('SI/RL', '').split('/')[0] if not i.isdigit()]).strip(),
          'LINE_NAME': ebcdic_dict.get('LINE', ''),
          'FIELD_FILE_NUMBER': ebcdic_dict.get('FFID RANGE', ''),
          'FIRST_SEIS_POINT_ID': ebcdic_dict.get('SP RANGE', '').split('-')[0], #First SP
          'LAST_SEIS_POINT_ID': ebcdic_dict.get('SP RANGE', '').split('-')[1] if len(ebcdic_dict.get('SP RANGE', '').split(' ')) > 1 else '',
          'BA_LONG_NAME_1': ebcdic_dict.get('CLIENT', ''),
          'DECRYPT_KEY': ebcdic_dict.get('DECRYPT_KEY', ''),
      }
      return json.dumps(data), json.dumps(data_ebcdic)
  except Exception as e:
    logger.error(f"Error processing file with SegyFile: {e}")
    raise