import tempfile
import lasio
import os
import json

def convertlas(file):
    try:
        # Membaca file sebagai bytes
        file_content = file.read()
        
        # Membuka file sebagai file text sementara untuk debugging
        with tempfile.NamedTemporaryFile(delete=False, mode='w+', encoding="utf-8") as temp_file:
            temp_file.write(file_content.decode('utf-8', errors='ignore'))  # Memastikan encoding aman
            temp_file.seek(0)
            las = lasio.read(temp_file.name)

        # Menampilkan nilai WRAP dan VERS secara terpisah
        vers = las.version['VERS'].value
        wrap = las.version['WRAP'].value
        print(f"\nVERS: {vers}")
        print(f"WRAP: {wrap}")
        # Menampilkan header well information
        result = {}
        print("Well Information:")
        for item in las.well:
            print(item)
            result[str(item.mnemonic)] = str(item.value) + ' ' + item.unit
        # Menampilkan header curve information
        print("\nCurve Information:")
        for curve in las.curves:
            print(f"{curve.mnemonic}: {curve.unit} ({curve.descr})")
        data = {
          'BA_LONG_NAME': '',
          'BA_TYPE': 'BADAN USAHA',
          'AREA_ID': '',
          'AREA_TYPE': '',
          'FIELD_NAME': '',
          'WELL_NAME': las.well.get('WELL', '')['value'],
          'UWI': las.well.get('UWI', '')['value'],
          'LOGGING_COMPANY': las.well.get('SRVC', '')['value'],
          'MEDIA_TYPE': '',
          'WELL_LOG_CLASS_ID': '',
          'DIGITAL_FORMAT': os.path.basename(file.filename).split('.')[1],
          'REPORT_LOG_RUN': '',
          'TRIP_DATE': las.well.get('SPUD', '')['value'], 
          'TOP_DEPTH': las.well.get('STRT', '')['value'],
          'TOP_DEPTH_OUOM': las.well.get('STRT', '')['unit'],
          'BASE_DEPTH': las.well.get('STOP', '')['value'],
          'BASE_DEPTH_OUOM': las.well.get('STOP', '')['unit'],
          'ORIGINAL_FILE_NAME': os.path.basename(file.filename),
          'PASSWORD': '',
          'DIGITAL_SIZE': os.path.getsize(temp_file.name), 
          'DIGITAL_SIZE_UOM': 'BYTE',
          'BA_LONG_NAME_1': '',
          'BA_TYPE_1': 'BADAN USAHA',
          'DATA_STORE_NAME': '',
          'REMARK': '',
          'SOURCE': '', 
          'QC_STATUS': 'TERVERIFIKASI OLEH SKK MIGAS',
          'CHECKED_BY_BA_ID': '3578144811980003',
      }
        data_well = {
            'WELL_NAME': las.well.get('WELL', '')['value'],
            'TOP_DEPTH': las.well.get('STRT', '')['value'],
            'TOP_DEPTH_OUOM': las.well.get('STRT', '')['unit'],
            'BASE_DEPTH': las.well.get('STOP', '')['value'],
            'BASE_DEPTH_OUOM': las.well.get('STOP', '')['unit'],
            'TRIP_DATE': las.well.get('SPUD', '')['value'], 
            'UWI': las.well.get('UWI', '')['value'],
            'LOGGING_COMPANY': las.well.get('SRVC', '')['value'],
        }
        return json.dumps(data), json.dumps(data_well)

    except Exception as e:
        raise
