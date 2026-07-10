import time
from fastapi import FastAPI,Path,HTTPException,Query
from fastapi.responses import HTMLResponse,JSONResponse
from pydantic import BaseModel, Field , EmailStr, field_validator,computed_field
from typing import Literal, Optional, List, Dict,Annotated
import json

#@MuskanBhabhi
app = FastAPI()

class Patient(BaseModel):
    id:Annotated[int,Field(description='id of the patient', examples=[1])]
    name:Annotated[str, Field(max_length=20,title='name of the patient',examples=["rohan yadav"],strict=True)]
    city:Annotated[str,Field(max_length=10,title='name of the city',examples=["goa"],strict=True)]
    age:Annotated[int,Field(ge=15 ,title='age of patient',examples=[15])]
    gender: Annotated[Literal['male', 'female', 'others'],Field(title="Gender of patient",examples=["female"])]
    height:Annotated[float, Field(title='height of the patient in feet',examples=[5.2])]
    weight:Annotated[float, Field(title='weight of the patient in Kg',examples=[72.0])]
    email:Annotated[EmailStr,Field(title='email of the patient (optional)',examples=["xyz@gmail.com"])] =None

    @computed_field
    @property
    def bmi(self)-> float:
        return round(self.weight / (self.height ** 2), 2)
    

    @computed_field
    @property
    def verdict(self)-> str:
        if self.bmi<18.5:
            return 'underweight'
        elif self.bmi<25:
            return 'normal'
        else:
            return 'Obeese'
        

class PatientUpdate(BaseModel):
    name:Annotated[Optional[str], Field(max_length=20,default=None)]
    city:Annotated[Optional[str],Field(max_length=10,default=None)]
    age:Annotated[Optional[int],Field(ge=15,default=None)]
    gender: Annotated[Optional[Literal['male', 'female', 'others']],Field(default=None)]
    height:Annotated[Optional[float], Field(default=None)]
    weight:Annotated[Optional[float], Field(default=None)]
    email:Annotated[Optional[EmailStr],Field(default=None)]

        
#load data from the file 
def load_data():
    with open("patient.json", "r") as f:
        data = json.load(f)
    return data
#save the data into the file
def save_data(data):
    with open("patient.json", "w") as f:
        json.dump(data, f, indent=4)

@app.get("/look", response_class=HTMLResponse)
def hello():
    return "<h1>Hey there</h1>"

@app.get("/")
def hello():
    return {'hello ':'there'}


@app.get("/about")
def about():
    return {'message':'welcome to first api dev'}


@app.get("/view")
def view():
    data=load_data()
    return data

@app.get('/patient/{patient_id}') # path parameter
def view_patient(patient_id:str=Path(...,description='patient id in DB',example=1)):
    #loading all the patient
    data=load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404,detail='no patient found')

@app.get('/sort')  #query parameter
def sort_patient(sort_by:str=Query(...,description='sort on the basis of height,weight,bmi') , order:str=Query('asc',description='sort in asc or dsc order')):
    
    valid_field=['height','weight','bmi']

    if sort_by not in valid_field:
        raise HTTPException(status_code=400,detail=f'select from {valid_field}')

    if order not in ['asc','dsc']:
        raise HTTPException(status_code=400,detail='kindly select from asc,dsc')   
    
    order=True if order =='dsc' else False


    data=load_data()
    
    sorted_patients = sorted(
    data.values(),
    key=lambda x: x.get(sort_by, 0) ,reverse=order)
    return sorted_patients


@app.post('/create')
def create_patient(patient: Patient):

    start = time.perf_counter()

    # Load existing data
    data = load_data()

    # Check if patient already exists
    if str(patient.id) in data:
        raise HTTPException(status_code=400, detail='patient already exist')

    # Add new patient
    data[patient.id] = patient.model_dump(exclude=['id'])

    # Save into JSON file
    save_data(data)

    end = time.perf_counter()
    print(f"POST /create executed in {end - start:.4f} seconds")

    return JSONResponse(
        status_code=201,
        content={'message': 'patient added successfully bhai!'} 
    )

@app.put('/edit/{patient_id}')
def update_patient(patient_id:str ,patientupdate:PatientUpdate):
    #check whether updating data exist in database or not
    data=load_data()
    if patient_id not in data:
        raise HTTPException(status_code=400, detail='patient does not exist')
    target_patient=data[patient_id]
    updated_info=patientupdate.model_dump(exclude_unset=True)
    for key,value in updated_info.items():
        target_patient[key]=value
        
    target_patient['id']=patient_id
    #converting our object to dictionary
    obj=Patient(**target_patient)
    changed_data=obj.model_dump(exclude='id')
    data[patient_id]=changed_data
    save_data(data)
    return JSONResponse(status_code=200,content='patient data updated succesfully')

@app.delete('/delete/{paitent_id}')
def delete_patient(patient_id:str=Query(...,description='enter the patient id')):
    data=load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404,detail='patient not found')
    
    del data[patient_id]
    save_data(data)
    return JSONResponse(status_code=200,content={'message':'patient data deleted succesfully'})


