
# coding: utf-8

# In[5]:


import json
import requests
import pandas as pd
import datetime
import numpy as np

import pandas.io.sql as psql
import mysql.connector
import pandas as pd

sql = mysql.connector.connect(host='192.168.104.50',
                              database='servicedesk',
                              user='servicedesk',
                              password='servicedesk'
                              )

print ("\nConnected SQL Servicedesk database successfully")

cursor = sql.cursor()


#Reg =['Polaris','AAD','AAN','ACC','ACR','APA','APTA','AUA','AUGS','CAP','HNS','ABFM','IC','LPH','NS','AAO']
Reg =['AAO']
for Registry in Reg:
    
    print (Registry)
    mySql_select_Table_Query = """select distinct provider_npi as npi_list from allpgres_ActiveProvider
    where is_provider_active='YES' and registry = '"""+Registry+"""' """
    print("Reading SQl")
    data = pd.read_sql(sql=mySql_select_Table_Query, con=sql)

    print("Creating Data List")
    data_list =data['npi_list'].tolist()
    #data_list=data_list[:5]
    print(data_list)
    data = pd.DataFrame(columns=['Name','NPI','Org','NonPatientFacing','HSPA','Rural','SmallGroup','mips_eligible_individual', 'individual_isOptInEligible', 'mips_eligible_group', 'group_isOptInEligible', 'mips_eligible_mipsApm', 'mips_eligible_virtualGroup', 'Error'])
    unwanted_data = pd.DataFrame(columns=['NPI'])

    # For loop of npi's
    print("Starting For Loop")
    for npi in data_list:
        if (len(str(npi)) == 10):
            try:
                print(npi)
                r = requests.get('https://qpp.cms.gov/api/eligibility/npi/' + npi)
                response = r.json()
                first_name = response['data']['firstName']
                middle_name = response['data']['middleName']
                last_name = response['data']['lastName']
            #     npi = response['data']['npi']
        #         years_in_medicare=response['data']['yearsInMedicare']
        #         approved_date = datetime.datetime.strptime(response['data']['firstApprovedDate'], "%Y-%m-%d")
                billing_tins=len(response['data']['organizations'])
                #name = first_name + ' ' +  middle_name + ' ' + last_name
                mips_eligible = 'Not Eligible'

                for org in range(0, billing_tins):
                    try:
                        organization = response['data']['organizations'][org]['prvdrOrgName']
                        try:
                            non_patient_facing = str(response['data']['organizations'][org]['individualScenario']['nonPatientFacing'])
                        except KeyError as e:
                            non_patient_facing = 'NA'
                        try:
                            hpsa_clinician = str(response['data']['organizations'][org]['individualScenario']['hpsaClinician'])
                        except KeyError as e:
                            hpsa_clinician = 'NA'
                        try:
                            rural_clinician = str(response['data']['organizations'][org]['individualScenario']['ruralClinician'])
                        except KeyError as e:
                            rural_clinician = 'NA'
                        try:
                            small_group_practitioner = str(response['data']['organizations'][org]['individualScenario']['smallGroupPractitioner'])
                        except KeyError as e:
                            small_group_practitioner = 'NA'
                        try:
                            if response['data']['organizations'][org]['individualScenario']['isEligible']['individual'] == True:
                                mips_eligible_individual = 'Eligible'
                            else:
                                mips_eligible_individual = 'Not Eligible'
                        except KeyError as e:
                                mips_eligible_individual = 'Data Not Available'
                        try:
                            if response['data']['organizations'][org]['individualScenario']["isOptInEligible"] == True:
                                individual_isOptInEligible = 'Eligible'
                            else:
                                individual_isOptInEligible = 'Not Eligible'
                        except KeyError as e:
                                individual_isOptInEligible = 'Data Not Available'
                        try:
                            if response['data']['organizations'][org]['individualScenario']['isEligible']['group'] == True:
                                mips_eligible_group = 'Eligible'
                            else:
                                mips_eligible_group = 'Not Eligible'
                        except KeyError as e:
                                mips_eligible_group = 'Data Not Available'
                        try:
                            if response['data']['organizations'][org]['groupScenario']["isOptInEligible"] == True:
                                group_isOptInEligible = 'Eligible'
                            else:
                                group_isOptInEligible = 'Not Eligible'
                        except KeyError as e:
                                group_isOptInEligible = 'Data Not Available'
                        try:
                            if response['data']['organizations'][org]['individualScenario']['isEligible']['mipsApm'] == True:
                                mips_eligible_mipsApm = 'Eligible'
                            else:
                                mips_eligible_mipsApm = 'Not Eligible'
                        except KeyError as e:
                                mips_eligible_mipsApm = 'Data Not Available'
                        try:
                            if response['data']['organizations'][org]['individualScenario']['isEligible']['virtualGroup'] == True:
                                mips_eligible_virtualGroup = 'Eligible'
                            else:
                                mips_eligible_virtualGroup = 'Not Eligible'
                        except KeyError as e:
                                mips_eligible_virtualGroup = 'Data Not Available'
                        error = ''
                        data_list = [[name, npi, organization, non_patient_facing, hpsa_clinician, rural_clinician, small_group_practitioner, mips_eligible_individual, individual_isOptInEligible, mips_eligible_group, group_isOptInEligible, mips_eligible_mipsApm, mips_eligible_virtualGroup, error]]
                        df2 = pd.DataFrame(data_list, columns=['First_Name','Last_Name','NPI','Org','NonPatientFacing','HSPA','Rural','SmallGroup','mips_eligible_individual', 'individual_isOptInEligible', 'mips_eligible_group', 'group_isOptInEligible', 'mips_eligible_mipsApm', 'mips_eligible_virtualGroup', 'Error'])
                        data = data.append(df2, ignore_index=True, sort=False)
                    except KeyError as e:
                        pass
            except:
                try:
                    error = response['error']['message']
                    if error == 'No individual clinician information exists for this NPI':
                        data_list = [[npi]]
                        df3 = pd.DataFrame(data_list, columns=['NPI'])
                        unwanted_data = unwanted_data.append(df3, ignore_index=True, sort=False)
                    first_name = ''
                    last_name = ''
                    organization = ''
                    non_patient_facing = ''
                    hpsa_clinician = ''
                    rural_clinician = ''
                    small_group_practitioner = ''
                    mips_eligible_individual = ''
                    individual_isOptInEligible = ''
                    mips_eligible_group = ''
                    group_isOptInEligible = ''
                    mips_eligible_mipsApm = ''
                    mips_eligible_virtualGroup = ''
                    tin = ''
                    data_list = [[name, npi, organization, non_patient_facing, hpsa_clinician, rural_clinician, small_group_practitioner, mips_eligible_individual, individual_isOptInEligible, mips_eligible_group, group_isOptInEligible, mips_eligible_mipsApm, mips_eligible_virtualGroup, error]]
                    df2 = pd.DataFrame(data_list, columns=['First_Name','Last_Name','NPI','Org','NonPatientFacing','HSPA','Rural','SmallGroup','mips_eligible_individual', 'individual_isOptInEligible', 'mips_eligible_group', 'group_isOptInEligible', 'mips_eligible_mipsApm', 'mips_eligible_virtualGroup', 'Error'])
                    data = data.append(df2, ignore_index=True, sort=False)
                except:
                    pass
        else:
            data_list = [[npi]]
            df3 = pd.DataFrame(data_list, columns=['NPI'])
            unwanted_data = unwanted_data.append(df3, ignore_index=True, sort=False)

    data['TIN'] = data['NPI'].map(data['NPI'].value_counts())
    data = data[[
     'NPI',
     'First_Name',
     'Last_Name',
     'TIN',
     'Org',
     'mips_eligible_individual',
     'individual_isOptInEligible',
     'mips_eligible_group',
     'group_isOptInEligible',
     'mips_eligible_mipsApm',
     'mips_eligible_virtualGroup',
     'NonPatientFacing',
     'SmallGroup',
     'Rural',
     'HSPA',
     'Error',
     ]]
    data.columns = ['NPI', 'First_Name','Last_Name', 'No. of TINs', 'Practice Name', 'MIPS Eligibility Individual', 'Opt In Eligibility Individual', 'MIPS Eligibility Group', 'Opt In Eligibility Group', 'MIPS Eligibility APM', 'MIPS Eligibility Virtual Group', 'Is Non Patient facing ?', 'Is small Practice?', 'Is Rural Practice?', 'Is HSPA ?', 'API Error']
    data['No. of TINs'] = np.where(data['API Error'].str.len() > 0, '', data['No. of TINs'])
    data.drop(data[data['API Error'] == 'bad NPI'].index, inplace = True) 
    data.to_excel("C:/Users/shabbir.anaswala/Downloads/NPI_CSV/"+Registry+"npi.xlsx", index=False)
    unwanted_data.to_excel("C:/Users/shabbir.anaswala/Downloads/NPI_CSV/Defaulter/"+Registry+"npi_defaulter.xlsx", index=False)
    print(''+Registry+'_NPI Script completed')


# In[ ]:




