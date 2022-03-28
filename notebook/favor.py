import os
from tabulate import tabulate
from init import initname, loaddatalist, ToExcel

PATH=os.path.dirname(os.path.realpath(__file__))
PATH_RAW = 'Excel'
Folder='output_Favor'
filename = 'MasterTable.xlsx'
textfile = 'FavorSum.txt'

def main():
    destFolder=os.path.join(PATH,Folder)
    rawFolder = os.path.join(PATH,PATH_RAW)
    os.makedirs(destFolder, exist_ok = True)
    dest = '%s\%s'%(destFolder,filename)

    favorsum = favor(destFolder,rawFolder)
    ToExcel(favorsum,dest,'FavorSum')

def favor(path,rawdata):
    print('Processing... FavorSum Table')
    maxFavor = 20
    detaillevel = False

    bond = generate_favor(rawdata,maxFavor,detaillevel)

    with open('%s\%s'%(path,textfile),'w',encoding='utf8') as f:
        f.write('%s'%(tabulate(bond,headers='firstrow')))

    return bond,len(bond[0])

def generate_favor(rawdata,maxFavor,detaillevel):
    chara,itemname = initname(rawdata)
    cdata = loaddatalist(rawdata,'CharacterSkillListExcelTable.json')
    data = loaddatalist(rawdata,'FavorLevelRewardExcelTable.json')
    cdata = {item['CharacterId']:item for item in cdata}
    clist = sorted(set([item['CharacterId'] for item in data])) #all char id
    StatHead = {
        'MaxHP_Base':0,
        'AttackPower_Base':1,
        'DefensePower_Base':2,
        'HealPower_Base':3,
    }

    bond = []
    for cid in clist:
        cname = chara[cid]
        favortable = {item["FavorLevel"]:item for item in data if item["CharacterId"] == cid and item["FavorLevel"] <= maxFavor}
        StatSum = [0,0,0,0]
        for flv,fdata in favortable.items():
            size = len(fdata["StatType"])
            for i in range(size):
                field = StatHead[fdata["StatType"][i]]
                StatSum[field] = StatSum[field] + fdata["StatValue"][i]
            if detaillevel :
                bond.append([cid,cname,flv]+StatSum)

        if not detaillevel:
            bond.append([cid,cname,flv]+StatSum)

    bond = [["Id","Name","Favor","HP","ATK","DEF","HEAL"]] + bond

    return bond



if __name__ == '__main__':
    print('favor main')
    main()