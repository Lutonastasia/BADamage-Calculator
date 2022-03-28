import os,json
from tabulate import tabulate
from init import initname, loaddatalist, ToExcel2
from favor import generate_favor as favor
from weapon import weaponcalc as wstat
import xlsxwriter

PATH=os.path.dirname(os.path.realpath(__file__))
PATH_RAW = 'Excel'
Folder='output_Maxstat'
filename = 'MasterTable.xlsx'
textfile = 'MaxStat.txt'

def main():
    destFolder=os.path.join(PATH,Folder)
    rawFolder = os.path.join(PATH,PATH_RAW)
    os.makedirs(destFolder, exist_ok = True)
    dest = '%s\%s'%(destFolder,filename)

    workbook = xlsxwriter.Workbook(dest)
    maxstat = MaxStat(destFolder,rawFolder,20)
    maxstat2 = MaxStat(destFolder,rawFolder,50)
    ToExcel2(maxstat,workbook,'MaxStat_b20')
    ToExcel2(maxstat2,workbook,'MaxStat_b50')
    workbook.close()


def MaxStat(path,rawdata,bond):
    print('Processing... MaxStat Table')

    MaxLevel = loaddatalist(rawdata,"ConstCommonExcelTable.json")[0]["AccountMaxLevel"]
    UELevel = [30,50,70]
    print(f"Max Level = {MaxLevel}, Bond Level = {bond}")

    data = calcstat(rawdata,MaxLevel,bond,UELevel)
    with open('%s\%s'%(path,f'b{bond}_{textfile}'),'w',encoding='utf8') as f:
        f.write('%s'%(tabulate(data,headers='firstrow')))


    return data,len(data[0])

def calcstat(rawdata,MaxLevel,bondlevel,UELevel):

    Stats = ["ATK","HP","DEF","HEAL"]
    chara,itemname = initname(rawdata)
    cdata = loaddatalist(rawdata,'CharacterExcelTable.json')
    cequip = {item["Id"]:item["EquipmentSlot"] for item in cdata if item["Id"] in chara}
    sdata = loaddatalist(rawdata,'CharacterStatExcelTable.json')
    sdata = {item['CharacterId']:item for item in sdata if item['CharacterId'] in chara}


    bond = getfavor(rawdata,bondlevel)         #{ID : {HP, ATK,DEF,HEAL} }
    weapon = getweapon(rawdata)                                 #{ID : 30: {ATK,HP,HEAL}, 50:{ATK,HP,HEAL} 70: {ATK,HP,HEAL} }
    starstat = getstargrowth(rawdata,5)                         #{ID: ATK, HP, HEAL}
    statlevel = getstatlevel(rawdata,sdata,MaxLevel,starstat)   #{ID : {ATK, HP,DEF,HEAL} }
    equip = getequipment(rawdata)                           #{equip: ATK,HP,DEF,HEAL,ATK%,HP%,DEF%,HEAL%}

    ce_flat,ce_per = {},{}
    for k,v in cequip.items():
        ce_flat[k] = {"ATK":0,"HP":0,"DEF":0,"HEAL":0}
        ce_per[k] = {"ATK":0,"HP":0,"DEF":0,"HEAL":0}
        for item in Stats:
            for eq in v:
                ce_flat[k][item] = ce_flat[k][item] + equip[eq][item]
                ce_per[k][item] = ce_per[k][item] + equip[eq][f'{item}%']

    calc = {}
    for item in statlevel:
        calc[item] = {}
        for LV in UELevel:
            for stat in Stats:
                cstat = statlevel[item][stat]
                ceflat = ce_flat[item][stat]
                ceper = (ce_per[item][stat] + 10000)/10000

                try:
                    bstat = bond[item][stat]
                except:
                    bstat = 0
                    continue        #skip non-release (no bond data)

                try:
                    wstat = weapon[item][LV][stat]
                except:
                    wstat = 0       #DEF

                temp = cstat + bstat + ceflat + wstat
                calc[item][f'{stat}_UE{LV}'] = round(temp * ceper)

    data = []
    for k,v in calc.items():
        if v == {}:
            continue
        else:
            tdata = []
            tdata.append(k)
            tdata.append(chara[k])
            tdata.append(bondlevel)
            for LV in UELevel:
                for stat in Stats:
                    tdata.append(v[f'{stat}_UE{LV}'])
            data = data + [tdata]

    data = [["Id","Name","Bond"]+[f'{i}_UE{j}' for j in UELevel for i in Stats]] + data

    return data


def getfavor(rawdata,bondlevel):
    data = favor(rawdata,bondlevel,False)
    header = data[0]
    del data[0]

    ftable = {}
    for item in data:
        ftable[item[0]] = {}
        for i in range(1,len(header)):
            ftable[item[0]][header[i]] = item[i]

    ctag = loaddatalist(rawdata,"CharacterAcademyTagsExcelTable.json")
    cname = {item["Id"]:[item["FavorItemUniqueTags"][i] for i in range(len(item["FavorItemUniqueTags"])) if item["FavorItemUniqueTags"][i].startswith("F_")][0] for item in ctag}

    linkbond = {}
    for item in cname:
        linkbond[item] = []
        key = '_'.join(cname[item].split('_')[0:-1]) if len(cname[item].split('_')) > 2 else cname[item]
        for k,v in cname.items():
            if key in v:
                linkbond[item].append(k)

    bond = {}
    for item in ftable:
        bond[item] = {}
        key = linkbond[item]
        for i in range(3,len(header)):
            temp = 0
            for j in range(len(key)):
                try:
                    temp = int(ftable[key[j]][header[i]]) + temp
                except:
                    pass
            bond[item][header[i]] = temp

    return ftable

def getweapon(rawdata):
    data = wstat(rawdata)
    del data[0]
    wtable = {}
    for item in data:
        wtable[item[0]] = {30:{},50:{},70:{}} #use only lv30 and lv70 stats
        wtable[item[0]][30]["ATK"] = item[3]
        wtable[item[0]][50]["ATK"] = item[5]
        wtable[item[0]][70]["ATK"] = item[7]
        wtable[item[0]][30]["HP"] = item[9]
        wtable[item[0]][50]["HP"] = item[11]
        wtable[item[0]][70]["HP"] = item[13]
        wtable[item[0]][30]["HEAL"] = item[15]
        wtable[item[0]][50]["HEAL"] = item[17]
        wtable[item[0]][70]["HEAL"] = item[19]

    return wtable

def getstargrowth(rawdata,starlimit):

    data = loaddatalist(rawdata,"CharacterTranscendenceExcelTable.json")
    data = {item["CharacterId"]:{"ATK":item["StatBonusRateAttack"],"HP":item["StatBonusRateHP"],"HEAL":item["StatBonusRateHeal"]} 
        for item in data if item["CharacterId"] < 30000}

    starstat={}
    for item in data:
        starstat[item] = {"ATK":0,"HP":0,"HEAL":0}
        for i in range(starlimit):
            starstat[item]["ATK"] = starstat[item]["ATK"] + data[item]["ATK"][i]
            starstat[item]["HP"] = starstat[item]["HP"] + data[item]["HP"][i]
            starstat[item]["HEAL"] = starstat[item]["HEAL"] + data[item]["HEAL"][i]

    return starstat

def getequipment(rawdata):

    EquipParts = ["Hat","Gloves","Shoes","Bag","Badge","Hairpin","Charm","Watch","Necklace"]
    StatType = {
        "AttackPower_Base":"ATK",           #not exist yet
        "MaxHP_Base":"HP",
        "DefensePower_Base":"DEF",
        "HealPower_Base":"HEAL",            #not exist yet
        "AttackPower_Coefficient":"ATK%",
        "MaxHP_Coefficient":"HP%",
        "DefensePower_Coefficient":"DEF%",  #not exist yet
        "HealPower_Coefficient":"HEAL%"
        }

    data = loaddatalist(rawdata,"EquipmentExcelTable.json")
    equipid = {item["EquipmentCategory"]:item["Id"] for item in data if item["EquipmentCategory"] in EquipParts and "Piece" not in item["Icon"]}
    stattable = loaddatalist(rawdata,"EquipmentStatExcelTable.json")
    stattable = {item["EquipmentId"]:{"StatType":item["StatType"],"MaxStat":item["MaxStat"]} for item in stattable}

    equipstat = {}
    for k,v in equipid.items():
        #print(k,v)
        equipstat[k] = {"ATK":0,"HP":0,"DEF":0,"HEAL":0,"ATK%":0,"HP%":0,"DEF%":0,"HEAL%":0}
        data = stattable[v]
        for i in range(len(data["StatType"])):
            try:
                key = StatType[data["StatType"][i]]
                equipstat[k][key] = data["MaxStat"][i]
            except:
                pass

    return equipstat

def getstatlevel(rawdata,data,level,starstat):

    stathead = ["AttackPower","MaxHP","DefensePower","HealPower"]
    starhead = {"AttackPower":"ATK","MaxHP":"HP","DefensePower":"DEF","HealPower":"HEAL"}
    StatLevel = loaddatalist(rawdata,'StatLevelInterpolationExcelTable.json')
    StatLevel = {item["Level"]:item for item in StatLevel}

    charstatlevel = {}
    for k,v in data.items():
        charstatlevel[k] = {}
        sBase,s100 = [],[]
        for head in stathead:
            sBase.append(v[f'{head}1'])
            s100.append(v[f'{head}100'])

        for i in range(len(stathead)):
            dif = (s100[i]-sBase[i])/100
            try:
                star_coef = (starstat[k][starhead[stathead[i]]]+10000)/10000
            except:
                star_coef = 1   #DEF

            charstatlevel[k][starhead[stathead[i]]] = round((sBase[i] + (dif*(StatLevel[level]["Standard"]/100)))*star_coef) #asumming using Standard for all

    return charstatlevel


if __name__ == '__main__':
    print('charstat main')
    main()
