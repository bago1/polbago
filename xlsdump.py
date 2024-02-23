import pandas as pd
import json

class ExcelToMongoDB:
    def __init__(self, excel_path):
        self.excel_path = excel_path

    def read_excel(self):
        # Using pandas to read the Excel file and return it
        excel = pd.read_excel(self.excel_path)
        return excel

    def transform_to_json(self, dataframe):
        # Initialize an empty list to hold the transformed data
        transformed_data = []

        # Iterate over each row in the DataFrame
        for _, row in dataframe.iterrows():
            # Construct the base structure for each verb entry
            verb_data = {
                "infinitive_eng": row["infinitive_eng"],
                "infinitive_pol": row["infinitive_pol"],
                "infinitive_aze": row["infinitive_aze"],
                "infinite_pol_perfectiveness": row["infinite_pol_perfectiveness"],
                "conjugations": [],
                 "image_url": row.get("image_url", None)

            }



            # There are 7 conjugations based on your example. Adjust if your actual data differs.
            for i in range(7):
                # Construct each conjugation entry
                conjugation = {
                    "pronoun_eng": row[f"conjugations[{i}].pronoun_eng"],
                    "pronoun_pol": row[f"conjugations[{i}].pronoun_pol"],
                    "pronoun_aze": row[f"conjugations[{i}].pronoun_aze"],
                    "conjugation_eng": row[f"conjugations[{i}].conjugation_eng"],
                    "conjugation_pol": row[f"conjugations[{i}].conjugation_pol"],
                    "conjugation_aze": row[f"conjugations[{i}].conjugation_aze"]
                }
                # Append the conjugation to the 'conjugations' list in the verb data
                verb_data["conjugations"].append(conjugation)

            # Append the fully constructed verb entry to the transformed data list
            transformed_data.append(verb_data)

        return transformed_data

    def save_to_json(self, json_data):
        # Save the JSON data to a file in the same directory
        with open('upload3.json', 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
        print("Data saved to upload2.json successfully.")

    def execute(self):
        df = self.read_excel()
        json_data = self.transform_to_json(df)
        self.save_to_json(json_data)

if __name__ == "__main__":
    excel_path = '/home/bahmadov/Downloads/poldb.xlsx'
    converter = ExcelToMongoDB(excel_path)
    converter.execute()
