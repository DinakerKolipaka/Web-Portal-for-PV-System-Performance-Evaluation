import pandas as pd
import statsmodels.api as sm
import itertools
import warnings
import os
from ast import literal_eval
import pymysql as pm
import pdb

def get_params_pdq(SomeSeries):
    """
    Generates optimal p,d,q values for the input series.
    :param SomeSeries:
    :return: p,d,q parameters for ARIMA model
    """
    p = d = q = range(0, 2)
    pdq = list(itertools.product(p, d, q))
    seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]
    print('Examples of parameter combinations for Seasonal ARIMA...')
    print('SARIMAX: {} x {}'.format(pdq[1], seasonal_pdq[1]))
    print('SARIMAX: {} x {}'.format(pdq[1], seasonal_pdq[2]))
    print('SARIMAX: {} x {}'.format(pdq[2], seasonal_pdq[3]))
    print('SARIMAX: {} x {}'.format(pdq[2], seasonal_pdq[4]))

    warnings.filterwarnings("ignore")
    aic = 10000000

    for param in pdq:
        for param_seasonal in seasonal_pdq:
            try:
                mod = sm.tsa.statespace.SARIMAX(SomeSeries,
                                                order=param,
                                                seasonal_order=param_seasonal,
                                                enforce_stationarity=False,
                                                enforce_invertibility=False)

                results = mod.fit()
                if(aic > results.aic):
                    aic = results.aic
                    params = (param,param_seasonal)
                print('ARIMA{}x{}12 - AIC:{}'.format(param, param_seasonal, results.aic))

            except:
                continue
    return params


def predict_values(params, SomeSeries, location):
    """
    Currently unable to save the generated model to file. (https://github.com/statsmodels/statsmodels/issues/3401).
    Alternate plan: Save the optimal params to DB. Fetch the params when required and predict the values. Also, this
    method will generate a predicted time series. This can also be persisted in a file.

    return: panda.series of predicted values.
    """
    mod = sm.tsa.statespace.SARIMAX(SomeSeries,
                                    order=params[0],
                                    seasonal_order=params[1],
                                    enforce_stationarity=False,
                                    enforce_invertibility=False)

    results = mod.fit()

    pred_uc = results.get_forecast(steps=365)

    preds = pred_uc.predicted_mean
    pred_df = pd.DataFrame({'date': preds.index, SomeSeries.name: preds.values})
    pred_df.index = pred_df['date']
    pred_df = pred_df.resample('M').mean()
    if os.path.isdir(location+'/PredictedValues') is False:
        os.makedirs(location+'/PredictedValues')
    pred_df.to_csv(location+'/PredictedValues/'+pred_df.columns[0] + '.csv', index=True, header=True)

    return pred_df


def save_params(params):
    df = pd.DataFrame(params)
    df.to_csv('params.csv', index=False, header=False)


def get_params(SomeSeries):
    df = pd.read_csv('test.csv', header=None)
    param_string = df.loc[df[0] == SomeSeries.name].iloc[0][1]
    param_tuple = literal_eval(param_string)
    return param_tuple


def removeOutliers(SomeDF):
    """
    Cleans the input dataframe by calculating mean and standard deviations and removes rows which lie outside 1 std.
    :param SomeDF:
    :return:Pandas series with frequency of one day
    """
    paramColumnName = SomeDF.columns[5]
    SomeDF_mean = pd.DataFrame({'mean_t': SomeDF.groupby(['Year', 'Month'])[paramColumnName].mean()}).reset_index()
    SomeDF_std = pd.DataFrame({'std_t': SomeDF.groupby(['Year', 'Month'])[paramColumnName].std()}).reset_index()
    SomeDF_mean_std = pd.merge(SomeDF_mean, SomeDF_std, how='inner', left_on=['Year', 'Month'], right_on=['Year', 'Month'])
    SomeDF_final = pd.merge(SomeDF, SomeDF_mean_std, how='left', left_on=['Year', 'Month'], right_on=['Year', 'Month'])

    def funk(row):
        # pdb.set_trace()
        if (float(row.iloc[5]) > (row.mean_t - row.std_t)) & (float(row.iloc[5]) < (row.mean_t + row.std_t)):
            return 1
        else:
            return 0

    SomeDF_final['bool'] = SomeDF_final.apply(lambda row: funk(row), axis=1)
    SomeDF_final = SomeDF_final[SomeDF_final["bool"] == 1]

    SomeDF_final['Date'] = SomeDF_final['Year'].astype(str) + '-' + SomeDF_final['Month'].astype(str) + '-' + SomeDF_final['Day'].astype(str)
    SomeDF_final['Date'] = pd.to_datetime(SomeDF_final['Date'])
    del SomeDF_final['Year']
    del SomeDF_final['Month']
    del SomeDF_final['Day']
    del SomeDF_final['Hour']
    del SomeDF_final['Minute']
    del SomeDF_final['mean_t']
    del SomeDF_final['std_t']
    del SomeDF_final['bool']
    SomeDF_final = SomeDF_final.set_index('Date')
    SomeSeries = SomeDF_final.groupby(['Date'])[paramColumnName].mean()
    SomeSeries.index = add_freq(SomeSeries, freq='D')

    return SomeSeries


def getSeries(SomeDF):
    """Create a time series from the input DataFrame"""
    paramColumnName = SomeDF.columns[5]

    SomeDF['Date'] = SomeDF['Year'].astype(str) + '-' + SomeDF['Month'].astype(str) + '-' + SomeDF['Day'].astype(str)
    SomeDF['Date'] = pd.to_datetime(SomeDF['Date'])
    del SomeDF['Year']
    del SomeDF['Month']
    del SomeDF['Day']
    del SomeDF['Hour']
    del SomeDF['Minute']
    SomeDF = SomeDF.set_index('Date')
    SomeSeries = SomeDF.groupby(['Date'])[paramColumnName].mean()
    SomeSeries.index = add_freq(SomeSeries, freq='D')

    return SomeSeries


def add_freq(idx, freq=None):
    """Add a frequency attribute to idx, through inference or directly.

    Returns a copy.  If `freq` is None, it is inferred.
    """

    idx = idx.copy()
    if freq is None:
        if idx.index.freq is None:
            freq = pd.infer_freq(idx.index)
        else:
            return idx
    idx.index.freq = pd.tseries.frequencies.to_offset(freq)
    if idx.index.freq is None:
        raise AttributeError('no discernible frequency found to `idx`.  Specify'
                             ' a frequency string with `freq`.')
    return idx.index


def files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            if file.endswith(".csv"):
                yield file


def cleanData(location):
    """
    Fetch the downloaded data from file storage and clean by calling removeOutliers().
    :return:
    List[ghiSeries, temperatureSeries, windSpeedSeries]
    """

    df = pd.DataFrame()
    for file in files(location+"/Datasets"):
        try:
            tempDF = pd.read_csv(location+"/Datasets/" + file, skiprows=2)
            # print(tempDF)
            df = df.append(tempDF)
        except pd.errors:
            continue

    # Splitting into 3 dataframes ghiDF, temperatureDF, windSpeedDF

    ghiDF = df.iloc[:, 0:6]
    ghiDF = ghiDF[ghiDF.GHI!=0]
    ghiSeries = removeOutliers(ghiDF)

    temperatureDF = df.iloc[:, 0:9]
    del temperatureDF['GHI']
    del temperatureDF['Wind Speed']
    temperatureSeries = getSeries(temperatureDF)

    windSpeedDF = df.iloc[:, 0:8]
    del windSpeedDF['GHI']
    del windSpeedDF['Temperature']
    windSpeedSeries = getSeries(windSpeedDF)

    return [ghiSeries, temperatureSeries, windSpeedSeries]


def build_model(location):
    cleanedData = cleanData(location)

    ghiParams = get_params_pdq(cleanedData[0])
    temperatureParams = get_params_pdq(cleanedData[1])
    windspeedParams = get_params_pdq(cleanedData[2])

    predict_values(ghiParams, cleanedData[0], location)
    predict_values(temperatureParams, cleanedData[1], location)
    predict_values(windspeedParams, cleanedData[2], location)


def get_city_and_state(location_id):

    conn = pm.connect(host='ift540.cyhc1qzz7e7u.us-west-2.rds.amazonaws.com', port=3306, user='IFT540PSP', passwd='IFT540PSP', db='pvsystem')
    cur = conn.cursor()

    cur.execute("SELECT * from Location where location_id = "+str(location_id))
    result = cur.fetchone()

    city = ""
    state = ""

    if location_id == result[0]:
        city = result[1]
        state = result[2]
    cur.close()
    conn.close()

    if city != "" and state != "":
        return (city, state)
    else:
        return -1


def fetch_predicted_values(location):
    dfDict = {}
    fileList = []
    if os.path.isdir('SystemOwner/'+location+'/PredictedValues/') is True:
        for file in files('SystemOwner/'+location+'/PredictedValues'):
            try:
                tempDF = pd.read_csv('SystemOwner/'+location+"/PredictedValues/" + file)
                param = file.split('.')[0]
                fileList.append(param)
                dfDict[param] = list(tempDF[param])
            except:
                continue
        return dfDict
    else:
        return {}
