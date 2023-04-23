import pandas as pd
import numpy as np
import lightgbm as lgb
import re
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error

data = pd.read_csv('../data_gen/month_v3.csv')\
    .rename(columns=lambda x:re.sub('[^A-Za-z0-9_]+', '', x))
X = data.drop('Adj_Close', axis=1)
X = X.drop('Days_From_2000', axis=1)
X = X.drop('CPI', axis=1)
X = X.drop('bank_borrow', axis=1)

X['DATE'] = pd.to_datetime(X['DATE'])
X.set_index('DATE', inplace=True)
y = data['Adj_Close']

params_lit = {
    'boosting_type': 'gbdt',
    'objective': 'regression',
    'metric': 'rmse',
    'max_depth': 7,
    'num_leaves': 30,
    'learning_rate': 0.15,
    'n_estimators': 90,
    'reg_alpha': 0.12,
    'reg_lambda': 0.1,
    'subsample': 1,
    'feature_fraction': 0.98
}

model = lgb.LGBMRegressor(**params_lit)

print('进行时序交叉验证')
mse_scores = []
tscv = TimeSeriesSplit(n_splits=10)
for train_index, test_index in tscv.split(X):
    X_train, X_test = X.iloc[train_index], X.iloc[test_index]
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    mse_scores.append(mse)

rmse = np.mean([mse**0.5 for mse in mse_scores])
# rmse = (sum(mse_scores)/len(mse_scores))**0.5
print('交叉验证均方根误差 (RMSE)：', rmse)
