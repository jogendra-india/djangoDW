from collections import defaultdict
from django.shortcuts import render
from rest_framework.decorators import api_view
from django.http import request
from rest_framework.response import Response
import mysql.connector
from . import data_file


# Create your views here.


@api_view(['GET'])
def getTagDetails(request):
    tagDetails={}
    try:
        tagDetails={}
        mydb=mysql.connector.connect(
            host=data_file.host,user=data_file.user,password=data_file.password,database='digitaltwin'
        )
        mycursor=mydb.cursor()
        query_to_fetch="Select tagID,tagDetail from tagdetails"
        mycursor.execute(query_to_fetch)
        myresult=mycursor.fetchall()
        for each_one in myresult:
            tagDetails[each_one[1]]=each_one[0]
            
    except:
        tagDetails={"error":"nothing found"}

    return Response(tagDetails)

context={}
time_data=[]
raw_data=[]
raw_data_charting=defaultdict(list)
column_list=[]

def fetchData():
    global context
    global time_data
    global raw_data
    global column_list
    global raw_data_charting

    # try:
    mydb=mysql.connector.connect(
        host=data_file.host,user=data_file.user,password=data_file.password,database='digitaltwin'
    )
    mycursor=mydb.cursor()
    query_to_fetch="Select column_name from information_schema.columns where table_schema=Database() and table_name='rawdata' ORDER BY ordinal_position"
    mycursor.execute(query_to_fetch)
    
    column_names=mycursor.fetchall()
    
    column_list=[column_names[i][0] for i in range(2,len(column_names))]
    del column_names

    query_to_fetch= "select * from rawdata"
    mycursor.execute(query_to_fetch)        

    myresult=mycursor.fetchall()
    for each_one in myresult:
        time_data.append(each_one[1])
        raw_data.append(list(each_one[2:]))
    
    for i in raw_data:
        for j in range(len(i)):
            raw_data_charting[column_list[j]].append(i[j])

    del myresult

fetchData()

@api_view(['GET','POST'])
def rawDataApi(request):
    # print(request.method)

    

    if request.method=='POST':
        captured_data=request.data
        xaxis=raw_data_charting[captured_data['para1']][0:captured_data["datarange"]]
        yaxis=raw_data_charting[captured_data['para2']][0:captured_data["datarange"]]

        data_to_push=[]

        for i in range(captured_data["datarange"]):
            data_to_push.append({"x":xaxis[i],"y":yaxis[i]})

        # zipped_axis=[list(a) for a in zip(xaxis,yaxis)]
        
        return Response({'chartData':data_to_push})

    return Response(column_list)
