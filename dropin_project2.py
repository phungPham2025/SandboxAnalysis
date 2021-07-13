
'''
Created on Mar 6, 2021

@author: phung

learning:
https://www.analyticsvidhya.com/blog/2020/05/datetime-variables-python-pandas/
https://www.machinelearningplus.com/time-series/time-series-analysis-python/
https://pythontic.com/datetime/datetime/isoformat
https://docs.python.org/3/library/datetime.html#datetime.timedelta
https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#timeseries-offset-aliases
https://www.interviewqs.com/ddi-code-snippets/select-pandas-dataframe-rows-between-two-dates
https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html

prob:
- charman issue when expand result  -> invisible dash
UnicodeEncodeError: 'charmap' codec can't encode characters in position 5241-5242: character maps to <undefined>

- 5pm-6:30 or 9pmâ€”10pm

Dashboard
- choose a date range
- number of request
- number of accommodated request: closed + help during drop-in + awaiting for student?
- closed rate: should this = (closed + help during drop-in)/(total - cancelled by student - awaiting for student)?
- number of request by class
- request by tutor
- request by duration type
- Ranking with tutor and the class they helped
- who come most often?
- report week by week: flow of appointment week by week, time series,
- every week , download the file and upload into our application and show the report.
-
'''
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from datetime import datetime, time, date

def barGraph(lst, lst1, selection = "'Monthly'"):
    # #graph:
    fig = plt.figure()
    x = []
    y = []
    x1 = []
    y1 = []
    for val in lst:
        x.append(val[0])
        y.append(val[1])
    for val in lst1:
        x1.append(val[0])
        y1.append(val[1])
    plt.bar(x, y)
    plt.plot(x, y, marker="o", color = "pink", linewidth=2, label = "total requests")
    plt.plot(x1, y1, marker="o", color = "green", linewidth=2, label = "closed requests")
    plt.xticks(rotation = 45)
    plt.legend()


    if selection == "Weekly":
        labelWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        plt.xticks(np.arange(0,len(x)),labels = labelWeek)
        plt.xlabel("Week day")
        plt.title("Weekly Analysis")

    else:
        plt.xlabel("Month")
        plt.title("Monthly Analysis")

    locs, labels = plt.xticks()
    for val1, val2, val3 in zip(y,y1, locs):
        plt.annotate(str(val1),(val3, val1), ha = "center")
        plt.annotate(str(val2),(val3, val2), ha = "center")

    plt.ylabel("Number of requests")
    st.pyplot(fig)

def processMonth(allDict):
    '''
    :param allDict:
    :return: dictMonth - dictionary of month is key and number of requests for that month is value
    '''
    #create a list of month:
    listMonth = set([item.split("-")[1] for item in allDict.keys()])

    dictMonth = {}
    for i in listMonth:  #i =10   #create sum values for each month
        for item in allDict.keys():
            if item.split("-")[1] == i:
                if i not in dictMonth:
                    dictMonth[i] = allDict[item]
                else:
                    dictMonth[i] += allDict[item]
    return dictMonth

def processWeek(allDict):
    '''

    :param allDict:
    :return: weekDict - dictionary with
    week name is key and the total of request for that week name is value
    '''
    #fromisoformat turns a string to datetime.date and use weekday() to find the name of day correspoding to the date
    #below is a list of weekday
    weekday = [date.fromisoformat(item).weekday() for item in allDict.keys()]  ## Monday is 0 and Sunday is 6
    # print(weekday)
    weekDict = {} #total values for the weekday
    for weekd, val in zip(weekday, list(allDict.values())):
        if weekd not in weekDict:
            weekDict[weekd] =val
        else:
            weekDict[weekd] +=val
    return weekDict

def general(requestWithinDate, allDict, closeDict, year):
    '''
    which month is the busiest?
    which day in a week busiest?
    allDict, CloseDict: dictionary with all date range for all data and and closed data
    '''

    st.subheader(year)
    totalRecord = requestWithinDate.shape[0]

    st.write(f"The number of request for {year}: {totalRecord} requests.")

    #number of closed
    dataClosed = requestWithinDate[requestWithinDate["Status"] == "Closed"]
    numClosed = dataClosed.shape[0]

    #adding help during drop in and remove cancelled by student + awaiting for student
    numCancel = requestWithinDate[requestWithinDate["Status"] == "Cancelled by Student"].shape[0]
    numawait = requestWithinDate[requestWithinDate["Status"] == "Awaiting student reply"].shape[0]
    helpDropin = requestWithinDate[requestWithinDate["Status"] == "Helped during drop-in session"].shape[0]
    correctClosedRate = (numClosed + helpDropin)/(totalRecord - numCancel - numawait)
    st.write(f"Adjusted Closed Rate during the time range selected: {round(correctClosedRate,2)}%. \n")
    st.write(f"Formula: Adjusted Closed Rate = (Closed Requests + Help During Drop-in)/(Total Requests - Canceled Requests - Awaiting For Reply Request)")

    requestWithinDateNew =requestWithinDate[["ID", "Date Created", "Assigned Agent"]].sort_values(by= ["Assigned Agent"]).set_index(np.arange(requestWithinDate.shape[0]))
    st.write(f"Appointments requested within the date range of {year}: ", requestWithinDateNew)
    dataClosedNew = dataClosed[["ID", "Date Created", "Assigned Agent"]].sort_values(by= ["Assigned Agent"]).set_index(np.arange(dataClosed.shape[0]))
    st.write(f"Closed appointments within the date range of {year}: ", dataClosedNew)

    #ask user to select analysis type
    selection = st.sidebar.selectbox('Select the analysis type: ',
    ('Monthly','Weekly', 'daily'), key = year)



    # print(closeDict)
    if selection == 'Monthly':
        allDictMonth =processMonth(allDict)
        closedDictMonth = processMonth(closeDict)
        barGraph(sorted(allDictMonth.items()), sorted(closedDictMonth.items()))
    elif selection == "Weekly":
        allweekDict = processWeek(allDict)
        closedweekDict = processWeek(closeDict)
        barGraph(sorted(allweekDict.items()),sorted(closedweekDict.items()), selection)
    else:
        fig = plt.figure()
        # label = sorted(list(set([x.split("-")[1] for x in list(allDict.keys())])))
        # print(label)
        # plt.xticks(np.arange(0,len(list(allDict.keys())), 31), label, rotation=45)
        plt.xticks(rotation=45, fontsize=5, alpha=.7)
        plt.ylabel("number of requests")
        plt.plot(list(allDict.keys()), list(allDict.values()),alpha= 0.5)
        plt.title("Number of Request Daily")
        st.pyplot(fig)

def barSmall(lstX, lstY, type = "tutor"):
    fig = plt.figure()
    plt.bar(lstX, lstY, color = "red", linewidth=2, label = "total requests")

    locs, labels = plt.xticks()
    for val1, val2 in zip(lstY, locs):
        plt.annotate(str(val1),(val2, val1), ha = "center")
    plt.legend()
    if type == "tutor":
        plt.xticks(lstX, rotation = 45)
    else:
        label = [item.split("-")[0] for item in lstX]
        plt.xticks(np.arange(len(lstX)),label)
    st.pyplot(fig)
def requestByCourse(requestWithinDate):
    st.header("Number of request by course")
    dgByClass = requestWithinDate[["ID", "What Course are you in?"]].groupby(by = "What Course are you in?").count()
    dgByClass.rename(columns = {"ID": "number of request by class"}, inplace = True)
    st.write(dgByClass.sort_values(by = ["number of request by class"], ascending = False), "\n")

    st.sidebar.write("Choose the course you want to see detail analysis!!")
    dg = requestWithinDate.groupby(by = "What Course are you in?")

    lstCourse = []
    lstNumRequest = []
    for name, group in dg:
        courseName = st.sidebar.checkbox(name)
        if courseName:
            st.write(name)
            lstCourse.append(name)
            st.write(group.sort_values(by= ["Assigned Agent"]))
            lstNumRequest.append(group.shape[0])
            st.write("**********")

    barSmall(lstCourse, lstNumRequest, type = "Course")

def requestByTutor(requestWithinDate):
    st.header("Number of appointment by the tutor")
    dgByAgent = requestWithinDate[["ID", "Assigned Agent"]].groupby(by = "Assigned Agent").count()
    dgByAgent.rename(columns = {"ID": "number of request by tutor"}, inplace = True)
    st.write(dgByAgent.sort_values(by = ["number of request by tutor"], ascending = False), "\n")

    st.sidebar.write("Choose the Tutor you want to see detail analysis!!")
    dg2 = requestWithinDate.groupby(by = "Assigned Agent")
    lstTutor = []
    lstNumRequest = []

    for name, group in dg2:
        tutorName = st.sidebar.checkbox(name)
        if tutorName:
            st.write(name)
            lstTutor.append(name)
            st.write(group)
            lstNumRequest.append(group.shape[0])
            st.write("**********")
    barSmall(lstTutor, lstNumRequest)

def requestByDuration(requestWithinDate):
    st.header("Number of Request by Duration Type")
    dgByDuration = requestWithinDate[["ID", "How long?"]].groupby(by = "How long?").count()
    dgByDuration.rename(columns = {"ID": "number of request by duration type"}, inplace = True)
    st.write(dgByDuration.sort_values(by = ["number of request by duration type"], ascending = False), "\n")
    lstDuration = []
    lstNumRequest = []
    dg3 = requestWithinDate.groupby(by = "How long?")
    for name, group in dg3:
        st.write(name)
        lstDuration.append(name)
        st.write(group.sort_values(by= ["Assigned Agent"]))
        lstNumRequest.append(group.shape[0])
        st.write("**********")
    barSmall(lstDuration, lstNumRequest)

def requestByRating(requestWithinDate):
    st.header("Number of Request by Rating")
    dgByRating = requestWithinDate[["ID", "Rating"]].groupby(by = "Rating").count()
    dgByRating.rename(columns = {"ID": "number of rating"}, inplace = True)
    st.write(dgByRating.sort_values(by = ["number of rating"], ascending = False), "\n")
    lstRating = []
    lstNumRequest = []
    dg4 = requestWithinDate.groupby(by = "Rating")
    for name, group in dg4:
        st.write(name)
        lstRating.append(name)
        st.write(group.sort_values(by= ["Assigned Agent"]))
        lstNumRequest.append(group.shape[0])
        st.write("**********")
    barSmall(lstRating, lstNumRequest)

def studentMost(requestWithinDate):
    st.header("Who comes most often?")
    dgStudent = requestWithinDate[["ID", "Name"]].groupby(by = "Name").count()
    dgStudent.rename(columns = {"ID": "Number of appointment made"}, inplace = True)
    dgStudent = dgStudent.sort_values(by= ["Number of appointment made"], ascending = False)

    st.subheader("Number of appointment made by students:")
    st.write(dgStudent, "\n")
    st.write("who come most often within the time frame selected is: ", dgStudent.index[0])

    st.sidebar.write("Select the student for detail analysis:")
    dg5 = requestWithinDate.groupby(by = "Name")

    lstStudent = []
    lstNumRequest = []
    for name, group in dg5:
        studentName = st.sidebar.checkbox(name)
        if studentName:
            st.write(name)
            lstStudent.append(name)
            st.write(group)
            lstNumRequest.append(group.shape[0])
            st.write("**********")
    barSmall(lstStudent, lstNumRequest)



def dictAllDays(startDate, endDate, df):
    #create date range using end and start date chosen
    dayRange = pd.date_range(start=startDate, end = endDate, freq='D')

    #isoformat()  converts datetime.day to string and then create a list of dates (string format)
    newdays = [day.isoformat().split("T")[0] for day in dayRange]
    # print(newdays)

    #create a list of date from the filtered data:
    date = [str(item).split(" ")[0] for item in df["Date Created"]]   #.split(" ")[0]

    #total requests by day:
    dictDateRequest = {}
    for val in date:
        if val not in dictDateRequest:
            dictDateRequest[val] = 1
        else:
            dictDateRequest[val] += 1
    # print(dictDateRequest)

    #create a dictionary of all days and values
    newDict = {}
    for i in newdays:
        if i not in dictDateRequest:
            newDict[i] = 0
        else:
            newDict[i] = dictDateRequest[i]
    return newDict       #this is a dictionary including all days and values corresponding to that date

def main():
    #import image
    img = Image.open("sandbox.jpg")
    st.image(img, width=700, caption = "CIS Sandbox")

    #write the title
    st.title("Welcome to Sandbox Dropin Analysis")

    #import excel file
    # df = pd.read_csv("wpsc_export_ticket.csv")
    #ask user to upload files:
    uploaded_file = st.sidebar.file_uploader("Choose a CSV file", accept_multiple_files=False)
    if uploaded_file:
        df = pd.read_csv(uploaded_file)


        #filter only the column I want to use
        data = df[["ID", "Assigned Agent", "Name", "Date Closed", "Date Created", "Rating", "What Course are you in?", "How long?", "Status"]]

        #ask user for start date and end date:
        startDate = st.sidebar.date_input("Enter start date: ")   #min_value = datetime.date(2020, 2, 1)
        endDate = st.sidebar.date_input("Enter end date: ")

        #Make date column become datetime
        data["Date Created"] = pd.to_datetime(data['Date Created']) # format = '%Y%m%d')   #.strftime('%Y-%m-%d %H:%M:%S')
        # st.write(data["Date Created"])

        #Give warning to user when date range is not within the date have in the imported file
        lastDate = data["Date Created"][data["Date Created"].size-1]    #find last date in the dataset. This data["Date Created"].size-1 to find the last index number
        firstDate = data["Date Created"][0]                             #find first date in the dataset

        #show the data
        st.write(f"Full data from {str(firstDate).split()[0]} to {str(lastDate).split()[0]}:", df)

        if pd.to_datetime(startDate) == pd.to_datetime(endDate): #this happens when user has not selected the date range
            st.sidebar.warning(f"Warning: Please select the start date and end date within the range. \
            The first date in your data is {firstDate} and the last date in your data is {lastDate}.")
            st.stop()

        elif lastDate < pd.to_datetime(endDate):  #end date in the excel < end date selected
            st.sidebar.warning(f"Warning: The last date in your data is {lastDate}. Please select end date before or by {lastDate}.")
            st.stop()

        elif firstDate.replace(hour=0, minute = 0, , second = 0) > pd.to_datetime(startDate):  #start date enter is out of range. firstDate has hour at 11pm so we need to reduce firstDate by 1 day so startDate can be greater than firstDate
            st.sidebar.warning(f"Warning: The start date is out of range. Please select start date by or after {str(firstDate).split()[0]}. ")
            st.stop()
        else:
            st.sidebar.success("You have selected the date range correctly.\
             Please check \"Next\" to continue.")
        next = st.sidebar.checkbox("Next")
        if next:  #st.button does not work the same as this and won't work well
            #create dataframe that within the date range
            mask = (data['Date Created'] > pd.to_datetime(startDate)) & (data['Date Created'] <= (pd.to_datetime(endDate) + pd.to_timedelta(1,unit = "D")))  #date start from 0:00:00
            requestWithinDate = data.loc[mask]

            # Add a selectbox :
            analysisType = st.sidebar.selectbox(
            'Select the analysis you want to do: ',
            ('General', 'Request by Course', 'Request by Tutor','Request by Duration Type', "Request by Rating", "Student"))

            #closed data
            dataClosed = requestWithinDate[requestWithinDate["Status"] == "Closed"]

            #
            yearLst = sorted(list(set([str(item).split(" ")[0][:4] for item in requestWithinDate["Date Created"]]))) #list of year
            # print(yearLst)

            #data of selected day range
            st.write(f"Data from {startDate} to {endDate}: ", requestWithinDate)

            # call other function:
            if analysisType == "General":
                st.header("General Analysis")
                # if len(yearLst) >= 2:
                st.sidebar.write("Please check the year to view detail analysis for that year:")
                for year in yearLst:

                    if st.sidebar.checkbox(year):
                        yeardf = requestWithinDate[requestWithinDate["Date Created"].astype(str).str.split(" ").str.get(0).str.slice(0,4) == year]  #dataframe for the year selected
                        #create a dictionary with all date range:
                        allDict = dictAllDays(startDate, endDate, yeardf)
                        closeYeardf = dataClosed[dataClosed["Date Created"].astype(str).str.split(" ").str.get(0).str.slice(0,4) == year]
                        closeDict = dictAllDays(startDate, endDate, closeYeardf)

                        general(yeardf, allDict, closeDict, year)
            elif analysisType == "Request by Course":
                requestByCourse(requestWithinDate)
            elif analysisType == 'Request by Duration Type':
                requestByDuration(requestWithinDate)
            elif analysisType == "Request by Rating":
                requestByRating(requestWithinDate)
            elif analysisType == "Student":
                studentMost(requestWithinDate)
            else: #analysisType == "Request by Tutor":
                requestByTutor(requestWithinDate)

main()
