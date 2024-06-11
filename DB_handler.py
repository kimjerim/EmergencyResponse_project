import firebase_admin
from firebase_admin import credentials, storage,db
import pyrebase
import json
from datetime import datetime, timedelta
import os
import shutil
import pandas as pd

class DBModule : 
    def __init__(self):
        with open("./auth/firebaseAuth.json") as f :
            config = json.load(f)     
        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()

#----------------------------- 로그인 ------------------------------

    def signin(self,name,_id_,pwd,phoneNumber):
        informations = {
            "uname" : name,
            "pwd" : pwd,
            "phoneNumber" : phoneNumber
        } 
        if self.signin_verification(_id_):
            self.db.child("users").child(_id_).set(informations)
            return True
        else :
            return False
        
    def signin_verification(self,uid):
        users = self.db.child("users").get().val()
        for i in users:
            if uid == i :
                return False
        return True

    def login(self,uid,pwd):
            users = self.db.child("users").get().val()
            try : 
                userinfo = users[uid]
                if userinfo["pwd"] == pwd :
                    return True
                else :
                    return False 
            except :
                return False
#-----------------------------------------------------------------------
            

#----------------------- emergency 데이터 관리 --------------------------

    # 생성한  emergency 데이터들 firebase에 저장
    def put_emergencyData(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate("./auth/serviceAccountKey.json")
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://emergencyresponse-b8c54-default-rtdb.firebaseio.com/'  # Firebase Realtime Database URL
                })
            
        # CSV 파일을 읽어 데이터프레임으로 변환
        csv_file_path = "EmergencyData/emergency_data.csv"
        data = pd.read_csv(csv_file_path)

        # 데이터를 딕셔너리로 변환
        data_dict = data.to_dict(orient="records")  # 각 행이 하나의 딕셔너리가 되도록 변환

        # emergency_data 참조 후 저장 
        ref = db.reference("/emergency_data")
        ref.set(data_dict)

        print("Firebase 업로드 완료")
        return 0


############################################################################################################
###########################################################################################################
    # 드롭다운에서 전달 받은 값들 호출    
    def emergencyData(self,city,district):
        emergency_data = self.db.child("emergency_data").get().val()
        print(emergency_data)
        address = []
        hospital = []
        
        # for reg in regions:
        #     if reg["city"] == city and reg["town"] == district : 
        #         address.append(reg["address"])
        #         hospital.append(reg["hospital"])
        # return address,hospital
############################################################################################################
############################################################################################################
#-----------------------------------------------------------------------
#                 

class Storage :
    def __init__(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate("./auth/serviceAccountKey.json")
            firebase_admin.initialize_app(cred, {
              'storageBucket': 'emergencyresponse-b8c54.appspot.com',
              'databaseURL': 'https://emergencyresponse-b8c54-default-rtdb.firebaseio.com/'  # Firebase Realtime Database URL
            })
        
        with open("./auth/firebaseAuth.json") as f:
            config = json.load(f)
        self.firebase = pyrebase.initialize_app(config)
        self.storage = self.firebase.storage()

    def video_save(self,user,filename) :
        self.storage.child(f"Video/recode/{user}/{filename}.mp4").put(f"videoRecode_tmp/{filename}.mp4",f"{user}")
        print(f"{filename} {user}님 DB 저장")
        return 0

    # 로컬 녹화본 삭제    
    def delete_all_files_in_directory(self,directory="./videoRecode_tmp"):
        if os.path.exists(directory) and os.path.isdir(directory):
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"{file_path} 파일이 삭제되었습니다.")
                except Exception:
                    pass
        return 0


    def video_getUrl(self,uid):
        bucket = storage.bucket()
        blobs = bucket.list_blobs(prefix=f"Video/recode/{uid}/")         
        urls = []
        filenames = []
        for blob in blobs:
            filename = os.path.basename(blob.name)
            if filename and '.' in filename:  # 파일 이름이 의미 있는 경우에만 처리
                url = blob.generate_signed_url(timedelta(seconds=300))  # URL 생성
                urls.append(url)
                filenames.append(filename)
        return urls,filenames

db = DBModule()
db.emergencyData("제주","제주시")