# coding=utf-8
import pandas as pd
import numpy as np


def fil_na(df, columns, order=1):
    fixed = 0
    for col in columns:
        missing_data = df[df[col].isna()]
        complete_data = df[~df[col].isna()].drop('DATE', axis=1)
        poly_coeffs = np.polyfit(complete_data.index, complete_data[col], order)
        poly_interp = np.poly1d(poly_coeffs)
        missing_data[col] = np.abs(poly_interp(missing_data.index))+fixed
        df.update(missing_data)
    return df


def pre_parse():
    month = pd.read_csv('../data_gen/Month.csv',)

    month.drop('Open',axis=1, inplace=True)
    month.drop('High',axis=1, inplace=True)
    month.drop('Low',axis=1, inplace=True)
    month.drop('Close',axis=1, inplace=True)
    month.drop('Volume_in_mln',axis=1, inplace=True)

    month['DATE'] = pd.to_datetime(month['DATE'])
    reference_date = pd.to_datetime('2000-01-01')
    month['Days_From_2000'] = (month['DATE'] - reference_date).dt.days
    return month


def lagging(df, columns): #有点效果
    lags = [1, 2, 3]  # 滞后期数
    df_lagged = pd.DataFrame()
    for col in columns:
        for lag in lags:
            # 使用shift方法将列向下滞后lag期
            lagged_col = df[col].shift(lag)
            new_col_name = col + '_lag' + str(lag)
            df_lagged[new_col_name] = lagged_col
    df = pd.concat([df, df_lagged], axis=1)
    df = df.bfill()
    return df


def avg_moving(df, columns):# 效果一般
    ma_lst = [3, 6, 9]
    new_cols = []
    for col in columns:
        for ma in ma_lst:
            col_name = col+'_'+'MA'+str(ma)
            df[col_name] = df[col].rolling(window=ma).mean()
            new_cols.append(col_name)
    df = fil_na(df, new_cols)
    return df


def stat(df, columns, window=3):
    stat_methods = ['max', 'min', 'mean', 'std']
    stat_cols = []
    for col in columns:
        for method in stat_methods:
            df[col+'_'+method] = df[col].rolling(window=window).max()
            df[col+'_'+method] = df[col].rolling(window=window).min()
            df[col+'_'+method] = df[col].rolling(window=window).mean()
            df[col+'_'+method] = df[col].rolling(window=window).std()
            stat_cols.append(col + '_' + method)
    df = fil_na(df, stat_cols)
    return df


if __name__ == '__main__':
    df = pre_parse()
    df = fil_na(df, ['asset_mean'], 2)
    # df = lagging(df, ['M2_adj'])
    # df = avg_moving(df, ['M2_adj'])
    # df = stat(df, ['M2_adj', 'CPI_adj', 'unemployment', 'bank_borrow'])
    print(len(df))
    df.to_csv('../data_gen/month_v3.csv', header=True, index=False)
