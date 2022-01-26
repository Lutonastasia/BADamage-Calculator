import os
from tabulate import tabulate
from init import initname, loaddatalist, ToExcel

PATH=os.path.dirname(os.path.realpath(__file__))
PATH_RAW = 'Excel'
Folder='output_Weaponstat'
filename = 'MasterTable.xlsx'
textfile = 'Weaponstat.txt'
terrainAdapt = {1:'D',2:'C',3:'B',4:'A',5:'S',6:'SS'}
terrainValue = {'D':1,'C':2,'B':3,'A':4,'S':5,'SS':6}
Terrain = {"Outdoor":0,"Street":1,"Indoor":2}

def main():
    destFolder=os.path.join(PATH,Folder)
    rawFolder = os.path.join(PATH,PATH_RAW)
    os.makedirs(destFolder, exist_ok = True)
    dest = '%s\%s'%(destFolder,filename)

    weaponstat = WeaponStat(destFolder,rawFolder)
    ToExcel(weaponstat,dest,'WeaponStat')

def WeaponStat(path,rawdata):
    print('Processing... Weapon Table')
    diag = weaponcalc(rawdata)

    with open('%s\%s'%(path,textfile),'w',encoding='utf8') as f:
        f.write('%s'%(tabulate(diag,headers='firstrow')))

    return diag,len(diag[0])

def weaponcalc(rawdata):

    chara,itemname = initname(rawdata)
    wdata = loaddatalist(rawdata,'CharacterWeaponExcelTable.json')
    wdata = {item['Id']:item for item in wdata}
      # "Id": 10000,
      # "ImagePath": "UIs/01_Common/04_Weapon/Weapon_Icon_10000",
      # "SetRecipe": 0,
      # "StatLevelUpType": "Standard",
      # "AttackPower": 162,
      # "AttackPower100": 1621,
      # "MaxHP": 561,
      # "MaxHP100": 5607,
      # "HealPower": 0,
      # "HealPower100": 0,

    StatLevel = loaddatalist(rawdata,'StatLevelInterpolationExcelTable.json')
    StatLevel = {item["Level"]:item for item in StatLevel}
    # {
      # "Level": 2,
      # "Standard": 101,
      # "Premature": 51,
      # "LateBloom": 152,
      # "Obstacle": 101,
      # "WeaponU": 152,
      # "WeaponS": 101,
      # "WeaponD": 51
    # },

    tdata = loaddatalist(rawdata,'CharacterStatExcelTable.json')
    tdata = {item['CharacterId']:{
        "Street":terrainValue[item["StreetBattleAdaptation"]],
        "Outdoor":terrainValue[item["OutdoorBattleAdaptation"]],
        "Indoor":terrainValue[item["IndoorBattleAdaptation"]]}
        for item in tdata}

    weaponprofile = loaddatalist(rawdata,'LocalizeCharProfileExcelTable.json')
    weaponprofile = {item["CharacterId"]:{"Name":item["WeaponNameJp"],"Desc":item["WeaponDescJp"]} for item in weaponprofile}

    diag = []
    stat = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,None,None,None,None,None]
    level = [1,30,40,50,60,70]

    for item in wdata:
        data = wdata[item]
        stat[0] = data["Id"]
        stat[1] = chara[data["Id"]]
        Attack,HP,Healing = calcstat(data,level,StatLevel)
        for i in range(6):
            stat[i+2] = Attack[level[i]]
            stat[i+8] = HP[level[i]]
            stat[i+14] = Healing[level[i]]

        Adapt = data["StatType"][2].replace("BattleAdaptation_Base","")
        tdata[data["Id"]][Adapt] = tdata[data["Id"]][Adapt] + data["StatValue"][2]
        stat[Terrain[Adapt]+20] = terrainAdapt[tdata[data["Id"]][Adapt]]
        try:
            stat[23] = weaponprofile[data["Id"]]["Name"]
            stat[24] = weaponprofile[data["Id"]]["Desc"].replace("\n","")
        except:
            pass

        diag = diag + [stat]
        stat = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,None,None,None,None,None]

    diag = [["Id","Name","A1","A30","A40","A50","A60","A70","HP1","HP30","HP40","HP50","HP60","HP70","Heal1","Heal30","Heal40","Heal50","Heal60","Heal70","Outdoor","Urban","Indoor","WName","WDesc"]] + diag

    return diag

def calcstat(data,Levels,StatLevel):
    ATKdif = data["AttackPower100"] - data["AttackPower"]
    sBase,s100 = [0,0,0],[0,0,0]
    sBase[0] = data["AttackPower"]
    sBase[1] = data["MaxHP"]
    sBase[2] = data["HealPower"]
    s100[0] = data["AttackPower100"]
    s100[1] = data["MaxHP100"]
    s100[2] = data["HealPower100"]
    temp ={}
    for i in range(3):
        dif = (s100[i]-sBase[i])/100
        cal = {}
        for level in Levels:
            if level == 1:
                cal[level] = sBase[i]
            else:
                cal[level] = (sBase[i] + round(dif*(StatLevel[level]["Standard"]/100))) #asumming using Standard for all
        temp[i] = cal

    return temp[0],temp[1],temp[2]

if __name__ == '__main__':
    print('Weaponstat main')
    main()
