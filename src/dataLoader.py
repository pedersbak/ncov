#! pip install BeautifulSoup4 requests
import tabula
import pandas as pd
from bs4 import BeautifulSoup
import re
import requests
import os
import numpy as np


def delete():
    dir_name = "../data"
    test = os.listdir(dir_name)
    for item in test:
        if item.endswith(".pdf"):
            os.remove(os.path.join(dir_name, item))


def download():
    linkList = []
    html_page = requests.get(
        'https://www.who.int/emergencies/diseases/novel-coronavirus-2019/situation-reports').content
    soup = BeautifulSoup(html_page, features="lxml")
    for link in soup.findAll('a'):
        l = str(link)
        m = re.search('/docs/(.+?).pdf', l)
        if m:
            foundLink = m.group(1)  # if 'sitrep' in link.get('href'):
            # print(found)
            linkList.append('https://who.int/docs/' + foundLink + '.pdf')

    for link in linkList:
        # url = 'https://www.who.int/docs/default-source/coronaviruse/situation-reports/20200121-sitrep-'+str(i)+'-2019-ncov.pdf'
        #print('Downloading '+url)
        myfile = requests.get(link)
        #print()
        targetFileName = os.path.basename(link)
        print('Writing ' + targetFileName)
        with open('../data/' + targetFileName, 'wb') as f:
            f.write(myfile.content)


def findNumber(df):
    t = False
    for i, row in df.iterrows():
        r = False
        for y in range(0, len(row)):
            #Is this the right table ?
            if 'japan' in str(row[y]).lower().strip():
                t = True
                # Is this the right row ?
            if 'total' in str(row[y]).lower() or 'confirmed' in str(row[y]).lower():
                r = True
            if r == True & t == True:
                if str(row[y]).split('.')[0].replace(',', '').isdigit():
                    return row['Date'].date(), int(str(row[y]).split('.')[0].replace(',', '')), row['Filename']

def createDataframe(pages):
    dates, confirmedCases, file=[],[],[]
    for page in pages:
        if len(page)>0:
            for i, df in enumerate(page):
                try:
                    dt, number, filename = findNumber(df)
                    dates.append(dt)
                    confirmedCases.append(number)
                    file.append(filename)
                    #print(dt,number, filename)
                except Exception as e:
                    pass
    dataTable=pd.DataFrame({'Date':dates, 'confirmedcases':confirmedCases, 'File':file})
    dataTable=dataTable.sort_values('Date')
    dataTable=dataTable[['Date','File','confirmedcases']].drop_duplicates() # Somehow, the same table could be returned twice
    dataTable['C'] = np.arange(len(dataTable))+1
    dataTable=dataTable.sort_values('C')

    dataTable.drop_duplicates(subset=['Date','File','confirmedcases','C'], inplace=True)
    print("Writing csv-file")
    dataTable.to_csv('../data/dataTable.csv')


if __name__=='__main__':
    delete()
    download()
    print("Extracting data from pdfs")
    pages=[]
    for filename in os.listdir('../data/'):
        if filename.endswith('.pdf'):
            dt=(filename[:8])
            dflist = tabula.read_pdf('../data/'+filename, pages='all', silent=True)
            for df in dflist:
                df['Date']=pd.Series([pd.to_datetime(dt) for i in range(0, len(df))])
                df['Filename']=pd.Series([filename for i in range(0, len(df))])
        pages.append(dflist)
    print(pages)
    createDataframe(pages)
    print("Done, all is well")