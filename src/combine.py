import pandas as pd


def df_parse(df, col_map=None):
    df = df.rename(columns={'Date': 'DATE'})
    if col_map is not None:
        df = df.rename(columns=col_map)
    df['DATE'] = pd.to_datetime(df['DATE'])
    return df[df['DATE'] >= '2000-01-01']


def quarter2month(df):
    df['DATE'] = pd.to_datetime(df['DATE'])
    df.set_index('DATE', inplace=True)
    df = df.resample('MS').ffill()
    df.reset_index(inplace=True)
    df = df[df['DATE'] >= '2000-01-01']
    return df


def merge_df(df1, df2, j='inner'):
    merged_df = pd.merge(df1, df2, on='DATE', how=j)
    merged_df['DATE'] = pd.to_datetime(merged_df['DATE'])
    merged_df = merged_df[merged_df['DATE'] >= '2000-01-01']
    return merged_df


def day2week(df):
    df = df.rename(columns={'Date': 'DATE'})
    df['DATE'] = pd.to_datetime(df['DATE'])
    df.set_index('DATE', inplace=True)
    aggs = ['mean', 'sum']
    agg_dict = {}
    for col_name in df.columns:
        agg_dict[col_name] = aggs

    monthly_df = df.resample('W').agg(agg_dict)
    monthly_df.columns = [f'{col[0]}_{col[1]}' for col in monthly_df.columns]
    monthly_df.reset_index(inplace=True)

    monthly_df['DATE'] = pd.to_datetime(monthly_df['DATE'])
    monthly_df['DATE'] = monthly_df['DATE'].dt.to_period('W')
    monthly_df['DATE'] = monthly_df['DATE'].dt.start_time
    monthly_df = monthly_df[monthly_df['DATE'] >= '2000-01-01']
    return monthly_df


def fil_day(df):
    df['DATE'] = pd.to_datetime(df['DATE'])
    df = df.set_index('DATE')
    date_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')
    df = df.reindex(date_range)
    df = df.bfill()
    df.reset_index(inplace=True)
    df = df.rename(columns={'index': 'DATE'})
    return df


def week2month(df, col):
    df['DATE'] = pd.to_datetime(df['DATE'])
    df.set_index('DATE', inplace=True)
    monthly_df = df.resample('M').agg({col: ['mean']})
    monthly_df.columns = [f'{col[0]}_{col[1]}' for col in monthly_df.columns]
    monthly_df.reset_index(inplace=True)

    monthly_df['DATE'] = pd.to_datetime(monthly_df['DATE'])
    monthly_df['DATE'] = monthly_df['DATE'].dt.to_period('M')
    monthly_df['DATE'] = monthly_df['DATE'].dt.start_time
    monthly_df = monthly_df[monthly_df['DATE'] >= '2000-01-01']
    return monthly_df


def joint_df(df1, df2):
    df1['DATE'] = pd.to_datetime(df1['DATE'])
    df2['DATE'] = pd.to_datetime(df2['DATE'])
    df = pd.merge(df1, df2, on='DATE', how='left')
    return df


if __name__ == '__main__':
    M2NS = pd.read_csv('../data/M2NS.csv')
    M2SL = pd.read_csv('../data/M2SL.csv')
    CPA = pd.read_csv('../data/CPALTT01USM657N.csv')
    CPI = pd.read_csv('../data/CPIAUCSL.csv')
    SP500M = pd.read_csv('../data/SP500_monthly.csv')
    unemploy = pd.read_csv('../data/unemployment.csv')
    GDP = pd.read_csv('../data/GDP.csv')
    borrowing = pd.read_csv('../data/Commercial_Bank_Borrow.csv')
    asset = pd.read_csv('../data/bank_assets.csv')
    # interest1month = pd.read_csv('../data/interest_rate_month.csv')
    # interest1month = df_parse(interest1month, {'REAINTRATREARAT1YE': 'interest_rate_1mo'})

    asset = week2month(asset, 'RESPPANWW')
    unemploy = df_parse(unemploy)
    borrowing = df_parse(borrowing)
    GDP = quarter2month(GDP)
    CPI_A = merge_df(CPA, CPI)
    M2_month = merge_df(M2NS, M2SL)
    SP500M = df_parse(SP500M)

    month_merged = merge_df(SP500M, M2_month)
    month_merged = merge_df(month_merged, CPI_A)
    month_merged = merge_df(month_merged, unemploy)
    month_merged = merge_df(month_merged, GDP)
    month_merged = merge_df(month_merged, borrowing)
    month_merged = merge_df(month_merged, asset, 'left')

    col_map = {'CPIAUCSL':'CPI_adj',
               'CPALTT01USM657N': 'CPI',
               'UNRATE':'unemployment',
               'H8B3094NCBCMG': 'bank_borrow',
               'M2SL': 'M2_adj',
               'M2NS': 'M2',
               'RESPPANWW_mean': 'asset_mean'
               }
    month_merged.rename(columns=col_map, inplace=True)

    print(month_merged)
    cols_with_na = month_merged.columns[month_merged.isna().any()].tolist()
    print("Columns with missing values:")
    print(cols_with_na)
    month_merged.to_csv('../data_gen/Month.csv', header=True, index=False)

    exit()
    WM2NS = pd.read_csv('../data/WM2NS.csv')
    WM2NS = WM2NS[WM2NS['DATE'] >= '2000-01-01']
    SP500D = pd.read_csv('../data/SP500_daily.csv', sep=';')
    SP500D.rename(columns={'Date': "DATE"}, inplace=True)
    SP500D = fil_day(SP500D)

    week_merged = joint_df(WM2NS,SP500D)
    week_merged.rename(columns={'WM2NS': "M2"}, inplace=True)

    print(len(week_merged), len(WM2NS))
    week_merged.to_csv('../data_gen/Week.csv', header=True, index=False)
