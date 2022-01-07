import pandas as pd


def clean_data():
    data = pd.read_csv('./globalterrorismdb_0718dist.csv',low_memory=False)
    data_cleaned = data[['iyear', 'imonth', 'iday', 'country','country_txt','city','latitude','longitude',
                         'success','suicide','attacktype1','attacktype1_txt','targtype1','targtype1_txt',
                         'weaptype1','weaptype1_txt','nkill','nwound','propextent','propextent_txt']]
    # print(data_cleaned)
    # print(data_cleaned.isnull().sum())

    data_cleaned = data_cleaned.dropna(subset=['longitude'])                               # 删除经纬度为空的记录
    data_cleaned = data_cleaned.dropna(subset=['nkill', 'nwound', 'propextent'], how='all') # 删除伤亡人数和财产损失都为空的记录
    data_cleaned['nkill'] = data_cleaned['nkill'].fillna(-1)                     # 将nkill列和nwound列的空值填充为-1
    data_cleaned['nwound'] = data_cleaned['nwound'].fillna(-1)
    data_cleaned['propextent'] = data_cleaned['propextent'].fillna(4)            # 将propextent和propextent_txt的空值填充为4:Unknown
    data_cleaned['propextent_txt'] = data_cleaned['propextent_txt'].fillna('Unknown')
    # print(data_cleaned)
    # print(data_cleaned.isnull().sum())
    return data_cleaned

