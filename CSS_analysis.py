import pandas as pd
import matplotlib.pyplot as plt


df=pd.read_csv("CSS_dataFrame_1.csv")
print(df)

print(df.columns)
plt.hist(x=df["isCSS_URl_Same"]) # ugly bue gets the job done
plt.show()