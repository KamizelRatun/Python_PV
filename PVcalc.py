import numpy

import PV_API_CALL
import json
import numpy as np
class PVfarm:
    def __init__(self, panel_type: str, azimuth: int, slope: int, numberofpanels: int, latitude: float, longitude:float, ID:int):
        """
        Class representing a photovoltaic farm.

        :param panel_type: Type of photovoltaic panels .
        :param azimuth: Panel azimuth in degrees (-180-180, where 0 is north).
        :param slope: Panel tilt angle in degrees (0-90).
        """
        self.panel_type = panel_type
        self.azimuth = azimuth
        self.slope = slope
        self.nop = numberofpanels
        self.lat = latitude
        self.lon = longitude
        self.ID = ID
        self.name = "Farm_"+str(ID)
    def create_irradiance_file(self,sy,ey):
        """
        Method creating file with irradiance and temperature data for selected farm
        :param sy:
        :param ey:
        :return: 0 - incorrect creation, 1 correct creation
        """
        result=PV_API_CALL.sarah2(sy,ey,self.slope,self.lat,self.lon,self.azimuth,self.name)
        return result
    def power_array(self):
        """
        Method creating lookup table P(G) for the object
        :return:
        """
        try:
            with open("PVPanels.json", "r", encoding="utf-8") as panelsfile:
                panels_data = json.load(panelsfile)
        except FileNotFoundError:
            print(f"Plik PVPanels.json nie został znaleziony.")
            return 0
        except json.JSONDecodeError:
            print(f"Plik PVPanels.json nie jest poprawnym plikiem JSON.")
            return 0
        except IOError as e:
            print(f"Błąd podczas otwierania pliku PVPanels.json: {e}")
            return 0
        except Exception as e:
            print(f"Nieoczekiwany błąd: {e}")
            return 0

        panel_area=panels_data["panels"][self.panel_type]["area"] #single panel area [m2]
        power=np.array(panels_data["panels"][self.panel_type]["Power"]) #electrical power array for the selected paneltype [W]
        self.power =power/panel_area #specific electrical power array for the selected paneltype [W/m2]
        self.irradiance=panels_data["panels"][self.panel_type]["Irradiance"] #irradiance array [W/m2]
        self.area = self.nop*panel_area # total area of panels in the farm [m2]


        return 1

    def simulate_pv(self):
        try:
            with open(self.name + ".json", "r", encoding="utf-8") as ir_data_file:
                ir_data = json.load(ir_data_file)
        except FileNotFoundError:
            print(f"Plik {self.name}.json nie został znaleziony.")
            return 0
        except json.JSONDecodeError:
            print(f"Plik {self.name}.json nie jest poprawnym plikiem JSON.")
            return 0
        except IOError as e:
            print(f"Błąd podczas otwierania pliku {self.name}.json: {e}")
            return 0
        except Exception as e:
            print(f"Nieoczekiwany błąd: {e}")
            return 0

        arr_length=len(ir_data)
        el_pow = []
        for i in range(arr_length):
            electric_power_specific=numpy.interp(ir_data[i]["irradiance"], self.irradiance, self.power, left=0, right=0)
            electric_power=int(electric_power_specific*self.area)
            year=ir_data[i]["year"]
            month = ir_data[i]["month"]
            day = ir_data[i]["day"]
            hour = ir_data[i]["hour"]
            sub_element = {'year': year, 'month': month, 'day': day, 'hour': hour, 'ElectricPower': electric_power}
            el_pow.append(sub_element)

        file_path = self.name+"_hour_PV_power.json"
        with open(file_path, 'w') as json_file:
            json.dump(el_pow, json_file, indent=4)
    def calculate_minute_power(self,sy,sm,sd,ey,em,ed):
        # print("Start symulacji, Rok:"+str(sy)+ " Miesiąc:"+str(sm)+" Dzień:"+str(sd))
        # print("Koniec symulacji, Rok:" + str(ey) + " Miesiąc:" + str(em) + " Dzień:" + str(ed))
        # Initialize an empty dictionary
        hour_power = {}

        # Path to the file
        file_path = 'Farm_1_hour_PV_power.json'

        try:
            # Try opening the file in read mode
            with open(file_path, 'r', encoding='utf-8') as json_file:
                # Load data from the JSON file into the dictionary
                hour_power = json.load(json_file)
        except FileNotFoundError:
            # Handles the case when the file is not found
            print(f"Error: The file '{file_path}' was not found.")
        except json.JSONDecodeError:
            # Handles the case when the file is not a valid JSON
            print("Error: The file does not contain valid JSON data.")
        except Exception as e:
            # General handler for other unexpected errors
            print(f"An unexpected error occurred: {e}")

        # print("Długość tablicy:"+str(len(hour_power)))
        #print(hour_power)
        minute_power = np.zeros(0)

        i=0
        while not (hour_power[i]["year"] == sy and hour_power[i]["month"] == sm and hour_power[i]["month"] == sd):
            i=i+1
        while not (hour_power[i]["year"] == ey and hour_power[i]["month"] == em and hour_power[i]["month"] == ed and hour_power[i]["hour"] == 23):
            minute_power_minor = np.zeros(60)
            sp= hour_power[i]["ElectricPower"]
            if (i+1) == len(hour_power):
                ep=sp
            else:
                ep = hour_power[i+1]["ElectricPower"]
            dif = ep-sp
            for j in range(60):
                minute_power_minor[j] = sp + dif * j/60
            # print(minute_power_minor)
            # print(i)
            if (i + 1) == len(hour_power):
                break
            minute_power=np.append(minute_power,minute_power_minor)
            i=i+1
        np.savetxt(self.name+"_power_data.csv", minute_power, delimiter=",")
        return minute_power




