import sys

import pandas as pd

print('Arguments', sys.argv)

month = sys.argv[1]

df = pd.DataFrame({'Day': [1,2], 'Num_Passengers': [3,4]})
df['Month'] = month
print(df)   

df.to_parquet(f'output_{month}.parquet')    

print("Hello pipeline!, month:", month)
