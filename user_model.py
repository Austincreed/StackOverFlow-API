import mysql.connector
import json
from flask import make_response
import requests
from datetime import datetime, timedelta
import jwt
class user_model():
    def __init__(self):
        # here is the connection code
        try:
            self.con=mysql.connector.connect(host="localhost", user="root",password="guddurkl01", database="stackoverflow_questions")
            self.con.autocommit=True
            self.cur=self.con.cursor(dictionary=True)
            print("Connection Established Successfully")
        except:
            print("Database Error")    
      
     
    # 1. CREATING TABLES 
    def create_tables(self):
        create_table_query = """CREATE TABLE IF NOT EXISTS stackoverflow_questions (
                                question_id INT PRIMARY KEY,
                                title VARCHAR(255) NOT NULL,
                                is_answered BOOLEAN,
                                view_count INT,
                                answer_count INT,
                                score INT,
                                last_activity_date INT,
                                creation_date INT,
                                content_license VARCHAR(20),
                                link VARCHAR(255) NOT NULL
                                )
                                """
        self.cur.execute(create_table_query)
        return make_response({"message":"Table Created Successfully"}, 201)
   
   
    
    # 2. LOAD Questions from API to Local-Database    
    def load_questions_from_api(self):
        try:
        # Make a request to Stack Overflow API
            api_url = "https://api.stackexchange.com/2.3/questions?order=desc&sort=activity&site=stackoverflow&pagesize=100"
            response = requests.get(api_url)
            questions_data = response.json()['items']

            # Store the data in MySQL
            for question in questions_data:
                insert_query = """
                    INSERT INTO stackoverflow_questions 
                    (question_id, title, is_answered, view_count, answer_count, score, last_activity_date, creation_date, content_license, link) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                values = (
                    question['question_id'],
                    question['title'],
                    question['is_answered'],
                    question['view_count'],
                    question['answer_count'],
                    question['score'],
                    question['last_activity_date'],
                    question['creation_date'],
                    question['content_license'],
                    question['link']
                )
                self.cur.execute(insert_query, values)

        except Exception as e:
            print(e)
                       
    
      
    # 3. GETTING DATA FROM THE DATABASE      
    def user_getquestion_model(self):
        self.cur.execute("SELECT * FROM stackoverflow_questions")
        result = self.cur.fetchall()
        if len(result)>0:
            res = make_response({"payload":result}, 200) # Define HTTP Headers
            res.headers["Access-Control-Allow-Origin"] = "*"
            return res
        else:
            res = make_response({"message":"No Data Found"}, 204)
            res.headers["Access-Control-Allow-Orign"] = "*"
            return res
    
    
    
    # 4. GETTING DATA FROM THE DATABASE USING FILTERS
    def user_filterquestion_model(self, filters, sort_by, limit, page):
        #self.cur.execute("SELECT * FROM stackoverflow_questions")
        try:
            qry = "SELECT * FROM stackoverflow_questions"
            values=[]
            
            if filters['is_answered']:
                qry += " AND is_answered = %s"
                values.append(filters['is_answered'])
                
            if filters['tags']:
                qry += " AND tags LIKE %s"
                values.append(f"%{filters['tags']}%")
                
            if filters['answer_count']:
                qry += " AND tags LIKE %s"
                values.append(filters['answer_count'])
                
            # APPLYING SORTING
            if sort_by == 'score':
                qry += " ORDER BY score DESC"
            elif sort_by == 'creation_date':
                qry += " ORDER BY creation_date DESC"
                    
            limit = int(limit)
            page = int(page)
            start = (page*limit)-limit
            qry += " LIMIT %s, %s"
            values.extend([start, limit])
            
            self.cur.execute(qry, tuple(values))
            result = self.cur.fetchall()
            
            if len(result)>0:
                res = make_response({"payload":result, "page_no":page, "limit":limit}, 200)
                res.headers["Access-Control-Allow-Origin"] = "*"
                return res
            else:
                res = make_response({"message":"No Data Found"}, 204)
                res.headers["Access-Control-Allow-Origin"] = "*"
                return res
        except Exception as e:
            res = make_response({"error":str(e)}, 500)
            res.headers['Access-Control-Allow-Origin'] = "*"
            return res

     
      
    # 5. GET QUESTION FROM TABLE BY id
    def user_getquestionbyid_model(self, question_id):
        try:
            qry = "SELECT * FROM stackoverflow_questions WHERE question_id=%s"
            self.cur.execute(qry, (question_id,))
            result = self.cur.fetchall()
            
            if len(result) > 0:
                res = make_response({"payload":result}, 200)
                res.headers['Access-Control-Allow-Orign'] = "*"
                return res
            else:
                res = make_response({"message":"Nothing to GET from the table"}, 404)
                res.headers['Allow-Control-Allow-Origin'] = "*"
                return res
        except Exception as e:
            res = make_response({"error":str(e)}, 500)
            res.headers['Allow-Control-Allow-Origin'] = "*"
            return res
            
        
          
        
    # 6. POST DATA IN TABLE    
    def user_postquestion_model(self, data):
        try:
            self.cur.execute("""INSERT INTO stackoverflow_questions(
                            question_id, title, is_answered,
                            view_count, answer_count, score,
                            last_activity_date, creation_date,
                            content_license, link)
                            VALUES(%s, %s, %s, %s,%s, %s, %s, %s, %s, %s)""",
                            (data['question_id'], data['title'], data['is_answered'],
                            data['view_count'], data['answer_count'], data['score'],
                            data['last_activity_date'], data['creation_date'],
                            data['content_license'], data['link']
                            ))
            
            
            if self.cur.rowcount > 0:
                res = make_response({"message":"User Created Successfully"}, 201)
                res.headers["Access-Control-Allow-Origin"] = "*"
                return res
            else:
                res = make_response({"message":"NOTHING TO POST"}, 202)
                res.headers["Access-Control-Allow-Origin"] = "*"
                return res
        except Exception as e:
            res = make_response({"error":str(e)}, 500)
            res.headers['Access-Control-Allow-Origin'] = "*"   
            return res  
        # return data
        
        
  
    # 7. PUT / UPDATE DATA IN THE TABLE
    def user_putquestion_model(self, data):
        try:
            self.cur.execute("""
                             UPDATE stackoverflow_questions SET 
                             question_id=%s, title=%s,
                             is_answered=%s, view_count=%s,
                             answer_count=%s, score=%s, last_activity_date=%s,
                             creation_date=%s, content_license=%s, link=%s
                             WHERE question_id=%s
                             """,
                             (
                              data['question_id'], data['title'],
                              data['is_answered'], data['view_count'],
                              data['answer_count'], data['score'],
                              data['last_activity_date'], data['creation_date'],
                              data['content_license'], data['link'],
                              data['question_id']
                              ))
            if self.cur.rowcount>0:
                res = make_response({"message":"Updated updated Successfully"}, 201)
                res.headers["Access-Control-Allow-Origin"] = "*"
                return res
            else:
                res = make_response({"message":"Nothing to Update"}, 202)
                res.headers["Access-Control-Allow-Origin"] = "*"
                return res
        except Exception as e:
            res = make_response({"error":str(e)}, 500)
            res.headers['Allow-Control-Allow-Origin'] = "*"
            return res
    
    
    # 8. PATCH DATA IN TABLE USING question_d        
    def user_patchquestion_model(self, data, question_id):
        try:
            qry = "UPDATE stackoverflow_questions SET "
            values = []
            for key in data:
                qry = qry + f"{key}=%s, "
                values.append(data[key])
                
            qry = qry[:-2] + " WHERE question_id=%s"
            values.append(data[key])
            # Now got the query.
            
            self.cur.execute(qry, tuple(values)) # query get executed
            if self.cur.rowcount > 0:
                res = make_response({"message":"User Updated patch successfully"}, 201)
                res.headers['Access-Control-Allow-Origin'] = "*"
                return res
            else:
                res = make_response({"message":"No Data to Patched"}, 202)
                res.headers['Access-Control-Allow-Origin'] = "*"
                return res
        except Exception as e:
            res = make_response({"error":str(e)}, 500)
            res.headers['Access-Control-Allow-Origin'] = "*"
            return res
  
  
  
    # 9. DELETE RECORDS FROM DATABASE
    def user_deletequestion_model(self, question_id):
        try:
            self.cur.execute(f"DELETE FROM stackoverflow_questions WHERE question_id=%s", (question_id,))
            if self.cur.rowcount>0:
                res = make_response({"message":"User Record Deleted Successfully"}, 200)
                res.headers["Allow-Control-Allow-Origin"] = "*"
                return res
            else:
                res = make_response({"message":"Nothing To Delete"}, 202)
                res.headers["Access-Control-Allow-Origin"] = "*"
                return res
        except Exception as e:
            res = make_response({"error":str(e)}, 500)
            res.headers['Acess-Control-Allow-Origin'] = "*"
            return res
        

        
        
    def user_upload_avatar_model(self, uid, filepath):
        self.cur.execute(f"UPDATE users SET avatar='{filepath}' WHERE id={uid}")
        if self.cur.rowcount > 0:
            res = make_response({"message":"FILE_UPLOADED_SUCCESSFULLY"}, 201)
            res.headers['Access-Control-Allow-Origin'] = "*"
            return res
        else:
            res = make_response({"message":"No data to update"}, 202)
            res.headers['Access-Control-allow-Origin'] = "*"
            return res    
        
        
    def user_login_model(self, data):
        self.cur.execute(f"SELECT id, name, email, phone, avatar, role_id FROM users WHERE email='{data['email']}' and password='{data['password']}'")
        result = self.cur.fetchall()
        userdata = result[0]
        exp_time = datetime.now() + timedelta(minutes=15)
        exp_epoch_time = int(exp_time.timestamp())
        payload = {
            "payload":userdata,
            "exp":exp_epoch_time
        }
        jwt_token = jwt.encode(payload, "sagar", algorithm="HS256")
        return make_response({"token":jwt_token}, 200)
       
        
        
        
        