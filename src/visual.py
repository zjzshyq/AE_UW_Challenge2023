import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

data = pd.read_csv('../data_gen/month_v3.csv')
data.drop('Days_From_2000', axis=1, inplace=True)

corr = data.corr()
sns.heatmap(corr, annot=True, cmap='coolwarm')
plt.show()
