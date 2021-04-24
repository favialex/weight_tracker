import streamlit as st

from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime
from streamlit.script_runner import RerunException
import plotly.graph_objects as go

TABELLE = "Tabelle"
GEWICHT_HINZUFUEGEN = "Gewicht hinzufügen"
DATAFILE = "datafile.csv"
GEWICHT = "Gewicht"
ZEITPUNKT = "Zeitpunkt"
TIME_COLUMNS = ["Jahr", "Monat", "Tag", "Stunden", "Minuten", "Sekunden"]


def create_df():
    df = {c:[] for c in [GEWICHT, *TIME_COLUMNS]}
    return pd.DataFrame(df)

def load_data(fn=DATAFILE):
    files = [f for f in Path().iterdir() if not f.is_dir()]
    if fn not in [f.name for f in files]: df = create_df()
    else: df = pd.read_csv(fn)
    return df

def save_data(data, fn=DATAFILE): 
    data.to_csv(fn, index=False)

def now():
    t = datetime.now()
    return {
        TIME_COLUMNS[0]: t.year,
        TIME_COLUMNS[1]: t.month,
        TIME_COLUMNS[2]: t.day,
        TIME_COLUMNS[3]: t.hour,
        TIME_COLUMNS[4]: t.minute,
        TIME_COLUMNS[5]: t.second
    }

def clean_inp(inp):
    return inp.replace(",", ".") 

def is_valid_weight(inp):
    try: float(inp)
    except: return False
    return True

def row2datetime(row):
    dt = datetime(
        year   = int(row[TIME_COLUMNS[0]]),
        month  = int(row[TIME_COLUMNS[1]]),
        day    = int(row[TIME_COLUMNS[2]]),
        hour   = int(row[TIME_COLUMNS[3]]),
        minute = int(row[TIME_COLUMNS[4]]),
        second = int(row[TIME_COLUMNS[5]]),
    )
    return dt

def create_time_df(data):
    weights = data[[GEWICHT]].values
    weights = np.einsum("ab -> a", weights)
    times_data = data[TIME_COLUMNS]
    times = []
    for r_idx in range(times_data.shape[0]):
        time_str = row2datetime(times_data.iloc[r_idx,:])
        times.append(time_str)
    return pd.DataFrame({
        GEWICHT: weights,
        ZEITPUNKT: times
    })

def create_display_df(data):
    weights = data[[GEWICHT]].values
    weights = np.einsum("ab -> a", weights)
    times_data = data[TIME_COLUMNS]
    times = []
    for r_idx in range(times_data.shape[0]):
        time_str = row2datetime(times_data.iloc[r_idx,:])
        time_str = time_str.strftime("%d. %b %Y")
        times.append(time_str)
    return pd.DataFrame({
        GEWICHT: weights,
        ZEITPUNKT: times
    })

def remove_last_row(data):
    if data.shape[0] < 2: return create_df()
    return data.iloc[:-1, :]



###################################################
############### SCRIPT BEGINS HERE ################
###################################################



data = load_data()
display_df = create_display_df(data)

user_input = st.number_input("Gewicht hinzufügen:")
if st.button("Hinzufügen"):
    if is_valid_weight(user_input): 
        t = now()
        new_row = {GEWICHT: [float(user_input)]}
        for tc in TIME_COLUMNS: new_row[tc] = [t[tc]]

        data = pd.concat([data, pd.DataFrame(new_row)])
        save_data(data)
        display_df = create_display_df(data)
        user_input = None
        
st.write("Aufzeichnungen")
st.write(display_df)

if st.button("Letzten Eintrag löschen"):
    data = remove_last_row(data)
    save_data(data)
    display_df = create_display_df(data)

time_df = create_time_df(data)
fig = go.Figure([go.Scatter(x=time_df[ZEITPUNKT], y=time_df[GEWICHT])])
st.write(fig)
