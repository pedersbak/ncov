from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__, static_folder='static')


def readData():
    data=pd.read_csv('../data/dataTable.csv', parse_dates=['Date'])[['Date','confirmedcases','C']].sort_values('C')
    data['dateStr']=data['Date'].dt.date.astype(str)
    return data.to_json(orient='records')


# Index page
@app.route('/')
def index():
    data=readData()
    return render_template('index.html', plot=data)
    print('Ready to serve...')


app.run(port=5001, debug=True, use_reloader=False, host='0.0.0.0')

