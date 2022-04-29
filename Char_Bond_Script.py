import pandas as pd
import json
from urllib.request import urlopen

def getCharNames() -> dict:
    # Ensure arg types
    
    url = 'https://raw.githubusercontent.com/aizawey479/ba-data/jp/Excel/CharacterAcademyTagsExcelTable.json'
    response = urlopen(url)
    data = json.loads(response.read())['DataList']

    result = {}
    for node in data:
        name = next(tag for tag in node["FavorItemUniqueTags"] if tag.startswith("F_"))
        name = name[2:].lower()

        # Correct the name
        name = name.replace("zunko", "junko")
        name = name.replace("hihumi", "hifumi")
		name = name.replace("tusbaki", "tsubaki")

        components = name.split("_")
        result[node["Id"]] = components[0].capitalize()
        if len(components) > 1:
            if not (len(components) == 2 and components[1] == "default"):
                result[node["Id"]] += " ({})".format(" ".join(components[1:]))

    return result
	
def getBondStats():
    url = "https://raw.githubusercontent.com/aizawey479/ba-data/jp/Excel/FavorLevelRewardExcelTable.json"
    response = urlopen(url)
    df = pd.read_json(response)
    df = pd.json_normalize(df['DataList'])
    
    return df
	
def listToString(s): 
    
    # initialize an empty string
    str1 = " " 

    result = (str1.join(map(str,s)))
    return result
	
def getBondBaseTable():
    charnames = getCharNames()
    bond_df = getBondStats()

    bond_df['StatType'] = bond_df['StatType'].apply(lambda x: listToString(x))
    bond_df = bond_df.merge(bond_df['StatType'].str.split(' ', expand=True), how='inner', left_index=True, right_index=True)

    bond_df['StatValue'] = bond_df['StatValue'].apply(lambda x: listToString(x))
    bond_df = bond_df.merge(bond_df['StatValue'].str.split(' ', expand=True), how='inner', left_index=True, right_index=True)
    bond_df['Charactername'] = bond_df['CharacterId'].map(charnames)

    column_dict = {
        'Charactername':'CharacterName',
        'CharacterId':'CharacterId',
        'FavorLevel':'Favorlevel',
        '0_x':'Stat1',
        '0_y':'Value1',
        '1_x':'Stat2',
        '1_y':'Value2'
    }

    bond_df = bond_df.rename(columns=column_dict)
    bond_df = bond_df[list(column_dict.values())]
    
    bond_df['Value2'] = bond_df['Value2'].apply(lambda x: 0 if x== None else x)
    bond_df['Value1'] = bond_df['Value1'].astype('int')
    bond_df['Value2'] = bond_df['Value2'].astype('int')
    
    StatHead = {
        'MaxHP_Base':'HP',
        'AttackPower_Base':'Attack',
        'DefensePower_Base':'Defence',
        'HealPower_Base':'Healing'}
    
    for column in ['Stat1','Stat2']:
        for stat in StatHead:
            bond_df[column] = bond_df[column].apply(lambda x: StatHead[stat] if x==stat else x)
    
    return bond_df
	
def main():
    bond_df = getBondBaseTable()
    chars = list(bond_df.CharacterName.unique())
    bondstat_dict = {}

    for character in chars:
        if character not in bondstat_dict:
            bondstat_dict[character] = {}

        for stat in ['Stat1','Stat2']:
            bondstat_dict[character][stat] = list(bond_df[bond_df['CharacterName']==character][stat].unique())[-1]
            
    bondsum_dict = {}

    for favor in range(2,51):
        bondsum = bond_df[bond_df['Favorlevel']<=favor].groupby(['CharacterName']).sum()
        for character, row in bondsum.iterrows():
            if character not in bondsum_dict:
                bondsum_dict[character] = {}
            if favor not in bondsum_dict[character]:
                bondsum_dict[character][favor] = {}

            bondsum_dict[character][favor]['Stat1'] = bondstat_dict[character]['Stat1']
            bondsum_dict[character][favor]['Value1'] = row['Value1']

            bondsum_dict[character][favor]['Stat2'] = bondstat_dict[character]['Stat2']
            bondsum_dict[character][favor]['Value2'] = row['Value2']
            
    bond_final_df = pd.DataFrame.from_dict({(i,j): bondsum_dict[i][j] 
                               for i in bondsum_dict.keys() 
                               for j in bondsum_dict[i].keys()},
                           orient='index').reset_index()

    bond_final_df = bond_final_df.rename(columns={'level_0':'CharacterName','level_1':'Bond'})

    bond_final_df.to_csv('BA_Bond_Stats.csv',index=False)
	
main()