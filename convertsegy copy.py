from segy.file import SegyFile
import tempfile
import json
from fuzzywuzzy import fuzz
import re
import hashlib

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def convertsegy(file):
  try:
    KEYS = ["line", "client", 'area_prospect', "survey_type", "record_date", "record_by", "record_instrument", "initial_format", "channel", "source_type"]
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
      temp_file.write(file.read())
      results = SegyFile(temp_file.name)
      results = results.text_header.strip()
      results = results.split('\n')
      data = {}
      
      # mengolah data key dan value yang akan ditampilkan pada halaman konfirmasi
      for result in results:
        pattern = r'(\D*\s*:)(\s*\D*[^ ]+)'
        matches = re.findall(pattern, result)
        for match in matches:
          keywords = ["min", "max", "delta"]
          if any(keyword in matches[0][0].strip() for keyword in keywords):
            variabel = matches[0][0].strip().split(" ")[0].lower()
            key = match[0].strip().replace(":", "").replace(" ", "").replace("x", "ks").lower()
            if variabel not in key:
              key = variabel+key
            key = key.replace("ks", 'x')
          else:
            key = match[0].strip().replace(":", "").replace(" ", "").lower()
            if(key == ""):
              continue
          value = match[1].strip()
          data[key] = value
      
      # data yang akan tampil pada preview
      result = {}
      for KEY in KEYS:
        biggest_ratio = 0
        biggest_key = ""
        for key in data:  
          ratio = fuzz.ratio(KEY.replace(" ", ""), key)
          if ratio > biggest_ratio: 
            biggest_ratio = ratio
            biggest_key = key
        result[KEY] = data[biggest_key]
      return json.dumps(result), json.dumps(data)
  except Exception as e:
    logger.error(f"Error processing file with SegyFile: {e}")
    raise