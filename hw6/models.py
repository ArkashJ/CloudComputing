import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import csv
import re
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

def pre_process_data():
    requests = pd.read_csv('requests.csv')
    failures = pd.read_csv('failure.csv')
    requests.dropna()
    failures.dropna()
    requests.drop(['Row'], axis=1, inplace=True)
    files = failures['File']
    requests['File'] = files
    requests.drop_duplicates(inplace=True)
    return requests
 
def country_vs_ip():
    requests = pre_process_data()    
    countries = requests['Country']
    client_ip = requests['Client_Ip']

    def ip_to_number(ip):
        parts = ip.split('.')
        return int(parts[0]) * (256 * 256 * 256) + int(parts[1]) * (256 * 256) + int(parts[2]) * 256 + int(parts[3])

    client_ip = client_ip.apply(lambda x: int(''.join([i for i in x if i.isdigit()])))

    X_train, X_test, y_train, y_test = train_test_split(client_ip, countries, test_size=0.2)

    # reshape to 2D array
    X_train = X_train.values.reshape(-1, 1)
    X_test = X_test.values.reshape(-1, 1)

    # Use a decision tree classifier
    clf = DecisionTreeClassifier()
    clf.fit(X_train, y_train)
    print(f"Accuracy: {clf.score(X_test, y_test)}")

    #import random forest classifier
    country_model = RandomForestClassifier(n_estimators=100, random_state=0)
    country_model.fit(X_train, y_train)
    print(f"Accuracy: {country_model.score(X_test, y_test)}")
    
def income_model():
    requests = pre_process_data()
    features = requests.drop(['Date', 'Income', 'File', 'Client_Ip'], axis=1)
    income = requests['Income']

    # use LabelEncoder to convert categorical data to numeric
    for col in features.columns:
        if features[col].dtype == type(object):
            le = LabelEncoder()
            features[col] = le.fit_transform(features[col])
    for col in features.columns:
        features[col] = features[col].astype('category')
    income = LabelEncoder().fit_transform(income)

    X_train, X_test, y_train, y_test = train_test_split(features, income, test_size=0.2)

    #Use a decision tree classifier
    clf = DecisionTreeClassifier()
    clf.fit(X_train, y_train)
    print(f"Accuracy: {clf.score(X_test, y_test)}")
   
    
def main():
    country_vs_ip()
    income_model()

main()