import json
import PVcalc
import numpy as np
from datetime import datetime



#read file with defined input to simulation
with open("PVInput.json", "r", encoding="utf-8") as requestfile:
    requestdata = json.load(requestfile) #dictionary containing input objects

    #TBD: validation of input data

#read file with defined PV models
with open("PVPanels.json", "r", encoding="utf-8") as panelsfile:
     panelsdata = json.load(panelsfile)

     # TBD: validation of input data

## construct objects of a class "PVfarm"
noi = len(requestdata["Installations"]) #check the number of installations
lon=requestdata["GEOdata"]["lon"]
lat=requestdata["GEOdata"]["lat"]
sy=int(requestdata["TimeRange"]["Start"]["SYear"])
ey=int(requestdata["TimeRange"]["End"]["EYear"])
farms=[] #array of declared PV farms

#calculate the number of minutes of simulation


for i in range(noi):
    paneltype = str(requestdata["Installations"][i]["PanelType"])
    azim = int(requestdata["Installations"][i]["Direction"])
    slop = int(requestdata["Installations"][i]["Elevation"])
    nop = int(requestdata["Installations"][i]["NumberOfPanels"])

    farm=PVcalc.PVfarm(paneltype,azim,slop,nop,lat,lon,i+1) #create new temprorary object of a single PV farm
    farms.append(farm) #add created farm to farms array
    farm.create_irradiance_file(sy,ey)
    farm.power_array()
    farm.simulate_pv()

del paneltype, azim, slop, nop #delete the unnecessary variables created in the loop

#number of minutes of simulation
minutes= len(farms[0].calculate_minute_power(2023,1,1,2023,12,31))

total_power=np.zeros(minutes) #array containing sum of power of installations

for i in range(noi):
    total_power=total_power+farms[i].calculate_minute_power(2023, 1, 1, 2023, 12, 31)

sm=int(requestdata["TimeRange"]["Start"]["SMonth"])
em=int(requestdata["TimeRange"]["End"]["EMonth"])
sd=int(requestdata["TimeRange"]["Start"]["SDay"])
ed=int(requestdata["TimeRange"]["End"]["EDay"])
output_dict={"TimeRange":{"Start":{"SYear":sy,"SMonth":sm,"SDay":sd},"End":{"EYear":ey,"EMonth":em,"EDay":ed}},"PVPower":total_power.tolist()}
client=str(requestdata["CustomerName"])
timestamp = str(datetime.now().strftime("%Y%m%d_%H%M%S"))
output_file_name=client+"_"+timestamp+".json"
with open(output_file_name, 'w') as output_file:
    json.dump(output_dict, output_file, indent=4)
#print(vars(farms[0]))
#print(vars(farms[1]))
# print(output_dict)