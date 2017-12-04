from django.shortcuts import render
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
import pymysql
import math
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, tostring
from lxml import etree
import datetime
import calendar
from django.http import HttpResponse
import matplotlib.pyplot as plt
from matplotlib import pylab
from pylab import *
import PIL, PIL.Image
import io
from SystemOwner import WeatherPrediction as wp
import pdb
import _tkinter
import pygal as pg
# Create your views here.
app_name = "SystemOwner"


def JulianDate_to_date(y, jd):
    month = 1
    while (jd - calendar.monthrange(y, month)[1] > 0 and month <= 12):
        jd = jd - calendar.monthrange(y, month)[1]
        month += 1
    date = datetime.date(y, month, jd)
    return date


def calculate(gmeas, t, ws, exponent):
    gtrc = 1000  # constant value of 1 kW/m2
    ttrc = 20  # Degree C
    ppredtarg = 106.25  # W/m2
    dTcond = 3  # constant value
    a = -3.47  # constant value
    b = -0.0594  # constant value

    tm = (gmeas * (exponent)) + t  # Calculating Module back temperature
    tc = tm + ((gmeas / 1000) * dTcond)  # Calculating cell temperature
    ppower = ppredtarg * (gmeas / gtrc) * (1 + (-0.005 * (
    tc - ttrc)))  # delta value is  -0.5% / degree Celsius.Crystalline Silicon Photovoltaic Modules ASE-300-DGF/50

    return ppower


def OwnerView(request):
    print("index")
    con = pymysql.connect(host='ift540.cyhc1qzz7e7u.us-west-2.rds.amazonaws.com',
                          port=3306,
                          user='IFT540PSP',
                          password='IFT540PSP',
                          db='pvsystem')

    print(request.session.get('userid'))

    user_id = request.session.get('userid')  # getting userid from session
    cur = con.cursor()
    cur.execute("select distinct PvSystem_id,User_id from PvSystem where user_id = %s", [user_id])
    result = cur.fetchall()
    list1 = []
    for row in result:
        # date_dict = { i:row }
        list1.append(row)

    date_dict = {"key": list1}

    return render(request, 'SystemOwnerHome.html', date_dict)


def Details(request, system_id):
    print("details")
    systemid = system_id
    con = pymysql.connect(host='ift540.cyhc1qzz7e7u.us-west-2.rds.amazonaws.com',
                          port=3306,
                          user='IFT540PSP',
                          password='IFT540PSP',
                          db='pvsystem')

    cur = con.cursor()
    cur.execute("select * from PvSystem where Pvsystem_id = %s", [system_id])
    result = cur.fetchone()
    print(result)
    return render(request, 'PVsystem.html', {'key': result})

def Update(request):
    con = pymysql.connect(host='ift540.cyhc1qzz7e7u.us-west-2.rds.amazonaws.com',
                          port=3306,
                          user='IFT540PSP',
                          password='IFT540PSP',
                          db='pvsystem')

    user_id = request.session.get('userid')  # getting userid from session
    cur = con.cursor()
    cur.execute("select pvsystem_id,power_rating,module_type,array_type,system_loss,tilt,system_type "
                "from PvSystem where user_id = %s", [user_id])
    result = cur.fetchall()
    list1 = []
    for row in result:
        # date_dict = { i:row }
        list1.append(row)

    res = {"key": list1}

    return render(request, 'Update.html', res)

def UpdateAttempt(request,system_id):
    result1 = {'key': system_id}
    if request.method == "GET":
        return render(request, 'UpdateSystem.html', result1)

def UpdateSystem(request):
    result1 = {}
    if request.method == "POST":
        system_id = request.POST.get('system_id')
        power = request.POST.get('powerrating')
        module = request.POST.get('moduletype')
        array = request.POST.get('arraytype')
        sloss = request.POST.get('systemloss')
        tilt = request.POST.get('tilt')
        stype = request.POST.get('systemtype')
        #l = request.POST.get('location')
        userid = request.session.get('userid')
        #loc = l.split(",")
        pk_list = (userid, power, module, array, sloss, tilt, stype)
        print(pk_list)
        update_pvsystem = ("Update PvSystem set user_id = %s, power_rating = %s, module_type = %s, array_type = %s, system_loss = %s,"
                        " tilt = %s, system_type = %s where pvsystem_id = %s")
        pk_list = list(pk_list)
        pk_list.append(system_id)

        con = pymysql.connect(host='ift540.cyhc1qzz7e7u.us-west-2.rds.amazonaws.com' ,
                              port=3306,
                              user='IFT540PSP',
                              password='IFT540PSP',
                              db='pvsystem')

        cur = con.cursor()
        cur.execute(update_pvsystem, pk_list)
        con.commit()
        result1 = {}

    return render(request, 'SystemOwnerWelcome.html', result1)




def Delete(request):
    con = pymysql.connect(host='ift540.cyhc1qzz7e7u.us-west-2.rds.amazonaws.com',
                          port=3306,
                          user='IFT540PSP',
                          password='IFT540PSP',
                          db='pvsystem')

    print(request.session.get('userid'))

    user_id = request.session.get('userid')  # getting userid from session
    cur = con.cursor()
    cur.execute("select distinct Pvsystem_id,User_id from PvSystem where user_id = %s", [user_id])
    result = cur.fetchall()
    list1 = []
    for row in result:
        # date_dict = { i:row }
        list1.append(row)

    date_dict = {"key": list1}

    return render(request, 'Delete.html', date_dict)


def DeleteAttempt(request, system_id):
    con = pymysql.connect(host='ift540.cyhc1qzz7e7u.us-west-2.rds.amazonaws.com',
                          port=3306,
                          user='IFT540PSP',
                          password='IFT540PSP',
                          db='pvsystem')

    cur = con.cursor()
    cur.execute("Delete from PvSystem where pvsystem_id = %s", [system_id])
    con.commit()

    result = {}
    #return render(request, 'SystemOwnerWelcome.html', result)
    return OwnerView(request)


def EE(request, system_id):
    request.session['systemid'] = system_id

    result = {}

    if request.method == "GET":
        return render(request, 'UploadCSV.html', result)


def CalculateEE(request):
    result = {}
    monthlyvalue = [0 for i in range(12)]


    if request.method == "POST":

        julianDay = 1
        numberInput = 0
        ambientAvg = 0
        windSpeedAvg = 0
        irradianceAvg = 0
        expectedEnergy = 0
        expectedEnergyArr = []
        expectedEnergyArrMonthlySum = []
        expectedEnergyArrMonthlycount = []
        daysCount = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        csv_file = request.FILES["csv_file"]
        file_data = csv_file.read()
        lines = file_data.splitlines()  # ("\n")
        k = 0

        for line in lines:

            if (k == 0):
                k += 1
                continue

            fields = line.decode().split(",")

            if (int(fields[1]) == julianDay):
                ambientAvg = ambientAvg + float(fields[2])
                windSpeedAvg = windSpeedAvg + float(fields[3])
                irradianceAvg = irradianceAvg + float(fields[5])
                expectedEnergy = expectedEnergy + calculate(float(fields[5]), float(fields[2]), float(fields[3]),
                                                        float(fields[4])) * 0.25
                numberInput += 1
            else:
                julianDay += 1
                expectedEnergyArr.append(expectedEnergy)
                irradianceAvg = float(fields[5])
                ambientAvg = float(fields[2])
                windSpeedAvg = float(fields[3])
                expectedEnergy = calculate(float(fields[5]), float(fields[2]), float(fields[3]), float(fields[4])) * 0.25
                numberInput = 1

    # monthly average calculaton

        i = 0
        expectedEnergyArrMonthlySum = []
        expectedEnergyArrMonthlycount = []

        for row in expectedEnergyArr:
            date = JulianDate_to_date(2007, i + 1)

            if (len(expectedEnergyArrMonthlySum) < date.month):
                expectedEnergyArrMonthlySum.insert(date.month - 1, row)
                expectedEnergyArrMonthlycount.insert(date.month - 1, 1)
            else:
                monthlysum = expectedEnergyArrMonthlySum[date.month - 1]
                monthlysum += row
                expectedEnergyArrMonthlySum[date.month - 1] = monthlysum
                monthlycount = expectedEnergyArrMonthlycount[date.month - 1]
                monthlycount += 1
                expectedEnergyArrMonthlycount[date.month - 1] = monthlycount
            i += 1

        j = len(expectedEnergyArrMonthlySum)
        print(monthlyvalue[0])
        for i in range(0, j):
            print(i)
            monthlyvalue[i] = round(expectedEnergyArrMonthlySum[i] / 1000, 3)
        con = pymysql.connect(host='ift540.cyhc1qzz7e7u.us-west-2.rds.amazonaws.com',
                              port=3306,
                              user='IFT540PSP',
                              password='IFT540PSP',
                              db='pvsystem')
        cur = con.cursor()
        systemid = request.session.get('systemid')
        # systemid_i = int(systemid)
        # e_list = (systemid,jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec,"EE")
        e_list = (systemid, monthlyvalue[0], monthlyvalue[1], monthlyvalue[2], monthlyvalue[3], monthlyvalue[4],
              monthlyvalue[5], monthlyvalue[6], monthlyvalue[7], monthlyvalue[8], monthlyvalue[9], monthlyvalue[10],
              monthlyvalue[11], 'EE')
        if (cur.execute("select * from Results1 where system_id = %s and etype = %s", [systemid, 'EE']) > 0):
            add_energy = ("Update Results1 set system_id = %s, jan = %s, feb = %s, mar = %s, apr = %s,"
                          " may = %s, jun = %s, jul = %s, aug = %s, sep = %s, oct = %s, nov = %s, dece = %s, etype = %s "
                          "where system_id = %s and etype = %s")
            e_list = list(e_list)
            e_list.append(systemid)
            e_list.append('EE')
            e_list = tuple(e_list)
        else:
            add_energy = ("INSERT INTO Results1 (system_id, jan, feb, mar, apr,"
                  " may, jun, jul, aug, sep, oct, nov, dece, etype)"
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

        cur.execute(add_energy, e_list)
        con.commit()

        result = {'key':monthlyvalue}
        #return render(request, 'SystemOwnerWelcome.html', result)
        return render(request, 'expectedview.html', result)

def CompareResults(request, system_id):
    con = pymysql.connect(host='ift540.cyhc1qzz7e7u.us-west-2.rds.amazonaws.com',
                          port=3306,
                          user='IFT540PSP',
                          password='IFT540PSP',
                          db='pvsystem')

    cur1 = con.cursor()
    cur2 = con.cursor()
    x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    cur1.execute("select jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dece from Results1 where system_id = %s and etype = %s", [system_id, 'PE'])
    res1 = cur1.fetchone()

    cur2.execute("select jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dece from Results1 where system_id = %s and etype = %s", [system_id, 'EE'])
    res2 = cur2.fetchone()

    monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    if not cur1.rowcount:
        return render(request, 'SystemOwnerWelcome.html', {'key': 1})
    elif not cur2.rowcount:
        return render(request, 'SystemOwnerWelcome.html', {'key': 2})
    else:
        y1 = list(map(float, list(res1)))
        y2 = list(map(float, list(res2)))
        comparison_graph = pg.Line()
        comparison_graph.title = 'Comparison of Expected and Predicted Energy'
        comparison_graph.x_labels = monthNames
        comparison_graph.add('Predicted Energy', y1)
        comparison_graph.add('Expected Energy', y2)
        comparison_graph.render_to_file('static/images/comparisonrender.svg')
        res1 = res1 + res2
        res1 = list(res1)
        res1.append(system_id)
        return render(request, 'CompareResults.html', {'key': res1})

def getLocation(request):
    print("Hello")
    if request.method == "POST":
        state = request.POST.get("state")
        city = request.POST.get("city")
        print(state, city)


def PE(request, system_id):
    print(system_id)
    # Set the constant values used in calculations
    Ttrc = 20
    Gtrc = 1000
    a = -3.47
    b = -0.0594
    dTcond = 3
    Ppredvals = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    daysCount = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    con = pymysql.connect(host='ift540.cyhc1qzz7e7u.us-west-2.rds.amazonaws.com',
                          port=3306,
                          user='IFT540PSP',
                          password='IFT540PSP',
                          db='pvsystem')

    cur = con.cursor()
    cur.execute("select power_rating from PvSystem where pvsystem_id = %s", [system_id])
    result = cur.fetchone()
    cur.execute("select location_id from SystemLocation where pvsystem_id = %s", [system_id])
    loc_id = cur.fetchone()
    d = wp.get_predicted_values(loc_id[0])
    Gvals = d['GHI']
    Tempvals = d['Temperature']
    WSvals = d['Wind Speed']
    for i in range(0, 12):
        # Calculate the module back surface temperature Tm
        Tm = Gvals[i] * (math.exp(a + b * WSvals[i])) + Tempvals[i]
        # Calculate the cell temperature Tc
        Tc = Tm + (Gvals[i] / 1000) * dTcond
        # Calculate the Cell Correction Factor CFtcell
        CFtcell = 1 - 0.005 * (Tc - Ttrc)
        # Calculate the Predicted Power values using the predicted power at target conditions
        Ppredvals[i] = float(result[0]) * (Gvals[i] / Gtrc) * CFtcell
        # Convert the predicted power to energy in MWh
        Ppredvals[i] = (Ppredvals[i] * daysCount[i] * 8) / 1000
        Ppredvals[i] = round(Ppredvals[i], 3)
    p_list = (system_id, Ppredvals[0], Ppredvals[1], Ppredvals[2], Ppredvals[3], Ppredvals[4], Ppredvals[5],
              Ppredvals[6], Ppredvals[7], Ppredvals[8], Ppredvals[9], Ppredvals[10], Ppredvals[11], 'PE')

    if(cur.execute("select * from Results1 where system_id = %s and etype = %s", [system_id, 'PE']) > 0):
        add_energy = ("Update Results1 set system_id = %s, jan = %s, feb = %s, mar = %s, apr = %s,"
                      " may = %s, jun = %s, jul = %s, aug = %s, sep = %s, oct = %s, nov = %s, dece = %s, etype = %s "
                      "where system_id = %s and etype = %s")
        p_list = list(p_list)
        p_list.append(system_id)
        p_list.append('PE')
        p_list = tuple(p_list)
    else:
        add_energy = ("INSERT INTO Results1 (system_id, jan, feb, mar, apr,"
                  " may, jun, jul, aug, sep, oct, nov, dece, etype)"
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    #pdb.set_trace()
    cur.execute(add_energy, p_list)
    con.commit()

    Ppredvals.append(system_id)

    return render(request, 'predicted.html', {'key': Ppredvals})


def EditView(request):

    result1 = {}

    if request.method == "GET":
        return render(request, 'editprofile.html', result1)

def EditProfile(request):

    result1 = {}

    if request.method == "POST":
        fname = request.POST.get('firstname')
        lname = request.POST.get('lastname')
        email = request.POST.get('emailid')
        phone = int(request.POST.get('phone'))
        address1 = request.POST.get('address1')
        address2 = request.POST.get('address2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip = int(request.POST.get('zip'))
        psw = request.POST.get('password')
        userid = int(request.session.get('userid'))
        edit_user = ("Update User set first_name = %s, last_name = %s, email_id = %s, contact_no = %s, addr_line1 = %s,"
                      " addr_line2 = %s, city = %s, state = %s, zip = %s, password = %s where user_id = %s")
        edit_list = [fname, lname, email, phone, address1, address2, city, state, zip, psw]
        edit_list = list(edit_list)
        result1 = {'key': edit_list}
        edit_list.append(userid)
        edit_list = tuple(edit_list)
        con = pymysql.connect(host='ift540.cyhc1qzz7e7u.us-west-2.rds.amazonaws.com',
                              port=3306,
                              user='IFT540PSP',
                              password='IFT540PSP',
                              db='pvsystem')

        cur = con.cursor()
        cur.execute(edit_user, edit_list)
        con.commit()
    return render(request, 'editprofile.html', result1)


def InsertView(request):

    result1 = {}

    if request.method == "GET":
        return render(request, 'AddNewPVSystem.html', result1)


def InsertPVView(request):

    result1 = {}

    if request.method == "POST":
        power = request.POST.get('powerrating')
        module = request.POST.get('moduletype')
        array = request.POST.get('arraytype')
        sloss = request.POST.get('systemloss')
        tilt = request.POST.get('tilt')
        stype = request.POST.get('systemtype')
        l = request.POST.get('location')
        userid = request.session.get('userid')
        #loc = l.split(",")
        pk_list = (userid, power, module, array, sloss, tilt, stype, 1, 1)
        print(pk_list)
        add_pvsystem = ("INSERT INTO PvSystem (user_id, power_rating, module_type, array_type, system_loss,"
                        " tilt, system_type, certification_status, system_access)"
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")

        con = pymysql.connect(host='ift540.cyhc1qzz7e7u.us-west-2.rds.amazonaws.com',
                              port=3306,
                              user='IFT540PSP',
                              password='IFT540PSP',
                              db='pvsystem')

        cur = con.cursor()
        cur.execute(add_pvsystem, pk_list)
        pvsystemid = cur.lastrowid  # to fetch the last autogenerated Pvsystem_id
        add_location = ("INSERT INTO SystemLocation (location_id, pvsystem_id, zip) VALUES (%s, %s, %s)")
        loc_list = (l, pvsystemid, '88888')
        cur.execute(add_location, loc_list)
        con.commit()
        result1 = {'key': 1}

    return render(request, 'AddNewPVSystem.html', result1)


def UploadXML(request):
    return render(request, 'UploadXMLtoDB.html')

def ProvideAccess(request):
    if request.method == "GET":
        return render(request, 'ProvideAccess.html')

def UploadXMLtoDB(request):
    if request.method == "POST":
        fileName = request.FILES['Selectfile']
        tree = ET.parse(fileName)
        root = tree.getroot()
        insertList = []
        con = pymysql.connect(host='ift540.cyhc1qzz7e7u.us-west-2.rds.amazonaws.com',
                              port=3306,
                              user='IFT540PSP',
                              password='IFT540PSP',
                              db='pvsystem')

        cur = con.cursor()
        for child in root:
            insertList.append(child.text)
        userid = request.session.get('userid')
        #l = insertList[6].split(",")
        pk_list = (userid, insertList[1], insertList[0], insertList[2], insertList[3], insertList[4], insertList[5], 1, 1)
        add_pvsystem = ("INSERT INTO PvSystem (user_id, power_rating, module_type, array_type, system_loss,"
                        " tilt, system_type, certification_status, system_access)"
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")

        cur.execute(add_pvsystem, pk_list)
        pvsystemid = cur.lastrowid  # to fetch the last autogenerated Pvsystem_id
        add_location = ("INSERT INTO SystemLocation (location_id, pvsystem_id, zip) VALUES (%s, %s, %s)")
        loc_list = (insertList[6], pvsystemid, '88888')
        cur.execute(add_location, loc_list)
        con.commit()

    return render(request, 'SystemOwnerHome.html')


def DownloadResults(request, system_id):
    con = pymysql.connect(host='ift540.cyhc1qzz7e7u.us-west-2.rds.amazonaws.com',
                          port=3306,
                          user='IFT540PSP',
                          password='IFT540PSP',
                          db='pvsystem')

    monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                  'November', 'December']

    cur = con.cursor()
    cur.execute("select system_id, jan, feb, mar, apr, may, jun, jul, "
                "aug, sep, oct, nov, dece, etype from Results1 where system_id = %s and etype = %s", [system_id, 'PE'])
    res1 = cur.fetchone()
    cur.execute("select system_id, jan, feb, mar, apr, may, jun, jul, "
                "aug, sep, oct, nov, dece, etype from Results1 where system_id = %s and etype = %s", [system_id, 'EE'])
    res2 = cur.fetchone()
    cur.execute("select city,state from Location where location_id in(select location_id from SystemLocation where pvsystem_id = %s )",[system_id])
    l = str(cur.fetchone())
    l1 = l.split('(')[1].split(')')
    loc = str(l1[0])
    vals1 = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    vals2 = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    for i in range(1, 13):
        vals1[i - 1] = res1[i]
        vals2[i - 1] = res2[i]
    # Create the root element of the XML i.e.Results
    root = etree.Element('Results')
    system = etree.Element('System')
    system.set('Location', loc)
    year = etree.Element('Year')
    year.set('Value', '2003')
    predicted = etree.Element('PredictedEnergy')
    for i in range(0, 12):
        month = etree.Element('Month')
        month.set('Name', monthNames[i])
        energy = etree.Element('Energy')
        energy.text = vals1[i]
        month.append(energy)
        predicted.append(month)
    expected = etree.Element('ExpectedEnergy')
    for i in range(0, 12):
        month = etree.Element('Month')
        month.set('Name', monthNames[i])
        energy = etree.Element('Energy')
        energy.text = vals2[i]
        month.append(energy)
        expected.append(month)
    year.append(expected)
    year.append(predicted)
    system.append(year)
    root.append(system)
    filename = "results.xml"
    file_ = open(filename, 'w')
    file_.write(tostring(root).decode())
    file_.close()
    file_ = open(filename, 'r')
    response = HttpResponse(file_.read(), content_type="application/xml")
    response['Content-Disposition'] = 'attachment; filename=results.xml'
    file_.close()
    return response
    #return render(request, 'SystemOwnerHome.html')


def Logout(request):
    del request.session['userid']
    print(request.session.get('userid'))
    result = {}
    return render(request, 'main.html', result)
