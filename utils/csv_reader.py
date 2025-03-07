import pandas as pd
from datetime import datetime

def convert_csv_to_df(file: str):
    csv_df = pd.read_csv(file)
    csv_df.drop(csv_df.columns[[0,2,3,4,5,6,7,8,9,10,12]], axis = 1, inplace = True) # Removing unnecessary columns
    df = csv_df.rename(columns={csv_df.columns[0]: "NHS_Number",csv_df.columns[1]: "Kit_ID"}) # Renaming the columns to something more meaningful
    df.dropna(inplace = True) # Deleting any Null records
    df["NHS_Number"] = df["NHS_Number"].str.replace(" ", "") # Removing the space from the nhs number
    df["FIT_Device_ID"] = df["Kit_ID"].apply(convert_kit_id_to_fit_device_id)
    return df

def convert_kit_id_to_fit_device_id(kit_id):
        today = datetime.now()
        year = today.strftime("%y") # Get the year from todays date in YY format
        return f"{kit_id}12{int(year)+1}12345/KD00001" # Creating the fit device id with an expiry date set to December next year
