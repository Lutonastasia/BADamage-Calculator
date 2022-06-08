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
	
def getCharStats():
    url = 'https://raw.githubusercontent.com/aizawey479/ba-data/jp/Excel/CharacterStatExcelTable.json'
    response = urlopen(url)
    df = pd.read_json(response)
    df = pd.json_normalize(df['DataList'])
    
    return df
	
def getCharDetails():
    url = "https://raw.githubusercontent.com/aizawey479/ba-data/jp/Excel/CharacterExcelTable.json"
    response = urlopen(url)
    df = pd.read_json(response)
    df = pd.json_normalize(df['DataList'])
    
    return df
	
def getUEStats():
    url = "https://raw.githubusercontent.com/aizawey479/ba-data/jp/Excel/CharacterWeaponExcelTable.json"
    response = urlopen(url)
    df = pd.read_json(response)
    df = pd.json_normalize(df['DataList'])
    
    return df
	
def listToString(s): 
    
    # initialize an empty string
    str1 = " " 
    
    # return string  
    return (str1.join(s))
	
def main():
    charnames = getCharNames()
    
    stats_df = getCharStats()
    stats_df.index = stats_df.CharacterId
    stats_df = stats_df.loc[list(charnames.keys())]
    stats_df['Charactername'] = stats_df['CharacterId'].map(charnames)
    
    details_df = getCharDetails()
    details_df.index = details_df.Id
    details_df = details_df.loc[list(charnames.keys())]
    details_df['EquipmentSlot']=details_df['EquipmentSlot'].apply(lambda x: listToString(x))
    equipment_df = details_df['EquipmentSlot'].str.split(' ', expand=True)
    stats_df = stats_df.merge(equipment_df, how='inner', left_index=True, right_index=True)
    
    ue_df = getUEStats()
    ue_df.index = ue_df.Id
    ue_df = ue_df.loc[list(charnames.keys())]
    ue_df = ue_df.drop('Id', axis=1)
    ue_columns = ['AfterSkillGroupId','AttackPower','AttackPower100', 'MaxHP','MaxHP100','HealPower','HealPower100','StatType','StatValue']
    stats_df = stats_df.merge(ue_df[ue_columns], how='inner', left_index=True, right_index=True, suffixes = [None,'_UE']) 
    
    column_dict = {
        'Charactername':'Charactername',
        'CharacterId':'CharacterId',
        'StabilityRate':'StabilityRate',
        'StabilityPoint':'Stability',
        'AttackPower1':'AttackPower1',
        'AttackPower100':'AttackPower100',
        'MaxHP1':'MaxHP1',
        'MaxHP100':'MaxHP100',
        'DefensePower1':'DefensePower1',
        'DefensePower100':'DefensePower100',
        'HealPower1':'HealPower1',
        'HealPower100':'HealPower100',
        'DodgePoint':'Evasion',
        'AccuracyPoint':'Accuracy',
        'CriticalPoint':'Crit Rate',
        'CriticalResistPoint':'Crit Res',
        'CriticalDamageRate':'Crit Damage',
        'CriticalDamageResistRate':'Crit Dmg Res',
        'BlockRate':'BlockRate',
        'HealEffectivenessRate':'Recovery Rate',
        'OppressionPower':'CC Strength',
        'OppressionResist':'CC Res',
        'DefensePenetration1':'DefensePenetration1',
        'DefensePenetration100':'DefencePenetration100',
        'AmmoCount':'AmmoCount',
        'AmmoCost':'AmmoCost',
        'IgnoreDelayCount':'IgnoreDelayCount',
        'NormalAttackSpeed':'NormalAttackSpeed',
        'Range':'Firing Range',
        'InitialRangeRate':'InitialRangeRate',
        'MoveSpeed':'MoveSpeed',
        'SightPoint':'SightPoint',
        'ActiveGauge':'ActiveGauge',
        'GroggyGauge':'GroggyGauge',
        'GroggyTime':'GroggyTime',
        'StrategyMobility':'StrategyMobility',
        'ActionCount':'ActionCount',
        'StrategySightRange':'StrategySightRange',
        'DamageRatio':'DamageRatio',
        'DamagedRatio':'DamagedRatio',
        'StreetBattleAdaptation':'StreetBattleAdaptation',
        'OutdoorBattleAdaptation':'OutdoorBattleAdaptation',
        'IndoorBattleAdaptation':'IndoorBattleAdaptation',
        'RegenCost':'RegenCost',
        0:'EquipmentSlot1',
        1:'EquipmentSlot2',
        2:'EquipmentSlot3',
        'AfterSkillGroupId':'UE',
        'AttackPower':'AttackPower1_UE',
        'AttackPower100_UE':'AttackPower100_UE',
        'MaxHP':'MaxHP1_UE',
        'MaxHP100_UE':'MaxHP100_UE',
        'HealPower':'HealPower1_UE',
        'HealPower100_UE':'HealPower100_UE',
        'StatType':'StatType',
        'StatValue':'StatValue'

    }
    stats_df = stats_df.rename(columns=column_dict)
    stats_df = stats_df[list(column_dict.values())]
    stats_df.to_csv('BA_Char_Stats.csv',index=False)
	
main()