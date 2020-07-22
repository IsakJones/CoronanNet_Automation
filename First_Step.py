#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 12:29:33 2020

@author: isakjones
"""

import pandas as pd

Table = pd.read_excel("Table.xlsx", header = None)

def get_policy_ids(df):
    """ 
    Input a DataFrame with one column constituting "WHO_NOTES". Outputs a list with policy ids.
    """

    def ciao_first_lines(val):
        """
        Input a formatted cell and outputs only WHO id#
    
        """
        if type(val) == float or val == "N/A":
            return val
        else:
            L = str(val).split("\n")
            if "WARNING" in L[0]:
                L = L[2:]
            if "ent" in L[0].split(" ")[1]:
                if "WHO" in L[1]:
                    L = L[2:]
                else:
                    L = L[1:]
            S = []
            for item in L:
                S.append(item.split(" ")[0])
            return "\n".join(S)
    
    dirty_number_list = (df.applymap(ciao_first_lines).to_string(header = False, index=False)).split("\n")
    
    clean_number_list = []
    for element in dirty_number_list:
        clean_number_list += element.split("\\n")
    
    for index in range(len(clean_number_list)):
        try:
            if " " in clean_number_list[index]:
                    clean_number_list[index] = clean_number_list[index].replace(" ", "")
            if clean_number_list[index] == "NaN":
                del clean_number_list[index]
        except IndexError:
            break
                
    return clean_number_list

def create_new_dataframe(clean):
    """ 
    creates a dataframe with corresponding entries.
    """
    def is_number(x):
        try:
            int(x)
            return True
        except ValueError:
            return False
    
    def formatmeasure(measure):
        if is_number(measure[1]):
            measure = measure[4:-3]
        return measure
    
    def formatscope(scope, number):
        if scope != "national" and str(WHO.loc[number, "AREA_COVERED"]) != "":
            scope = str(WHO.loc[number, "AREA_COVERED"])
        return scope
    
    def formatlink(link):
        try:
            if "\n\n" in link:
                link = link.replace("\n\n", "  OR  ")
            elif "\n" in link:
                link = link.replace("\n", "  OR  ")
            return link
        except TypeError:
            return "missing"
    
    WHO = pd.read_csv("WHO.csv", index_col = "NUMBER")
    columns = ('WHO_ID# COUNTRY START_DATE SCOPE POLICY LINK').split(" ")
    df = pd.DataFrame({ columns[0] : clean})
    
    df[columns[1]] = df[columns[0]].apply(lambda number: WHO.loc[int(number), "COUNTRY_TERRITORY_AREA"])
    df[columns[2]] = df[columns[0]].apply(lambda number: WHO.loc[int(number), "DATE_START"])
    df[columns[3]] = df[columns[0]].apply(lambda number: formatscope(WHO.loc[int(number), "ADMIN_LEVEL"], int(number)))
    df[columns[4]] = df[columns[0]].apply(lambda number: formatmeasure(WHO.loc[int(number), "PROV_MEASURE"]))
    df[columns[5]] = df[columns[0]].apply(lambda number: formatlink(WHO.loc[int(number), "LINK"]))
    
    df = df.drop( index = df[ df["LINK"] == "missing"].index)
    
    return df
            
create_new_dataframe(get_policy_ids(Table)).to_excel("Central_America_Missing_Entries.xlsx")

