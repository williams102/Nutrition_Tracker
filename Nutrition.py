"""_summary_
Nutrition.py
Author: Ben Williams

Date Modified: 15 July 2024

Version: 1.0

Summary: This program is designed to serve as a daily nutrition tracker to help users track their eating
habits and view their nutritional intake over time. Users can report their daily meals and view charts that 
summarize their nutrition. This program is designed to be run using the command terminal. For more information, 
view the "info" option while running the program. 

Functions:
- main(): contains the code for program. 

Arguments:
none

Returns:
none
    _type_: _description_
"""

import pandas as pd
import numpy as np
import os
import ntnpro as nt
from ntnpro import ask_user
from ntnpro import user_response
import datetime 
from datetime import datetime as dt
from dateutil import parser
from matplotlib import pyplot as plt
from matplotlib.colors import Normalize
from colorama import init, Fore, Back, Style

def main():
    init()
    print(Back.WHITE+Fore.BLACK)

    run = True

    try:
        patient_database = os.path.join(os.path.expanduser('~'), 'OneDrive - Milwaukee School of Engineering', 'Patient Profiles.csv')
        food_database = os.path.join(os.path.expanduser('~'), 'OneDrive - Milwaukee School of Engineering', 'Food List.xlsx')
        day_database = os.path.join(os.path.expanduser('~'), 'OneDrive - Milwaukee School of Engineering', 'Daily Chart.xlsx')

        patient_df = pd.read_csv(patient_database)
        food_df = pd.read_excel(food_database)
        day_df = pd.read_excel(day_database)
    except FileNotFoundError:
        input(Fore.RED+Back.WHITE+'\nFile or directory could not be found. Please check location of file.')

    while run:
        today = dt.now()

        while run:
            os.system('cls')
            print(Back.WHITE+Style.NORMAL+Fore.BLACK+"___________"*10)
            print('\nWelcome to the Nutrition Tracker Program! Please enter your patient ID number to login (1) or create a new profile to join (2). Type "dir" to view the profile directory, "info" to view information regarding the program, and "quit" to exit.')
           
            answer = user_response(Style.BRIGHT+"\nPlease type option number: ", [1, 2, 'dir', 'info', 'quit'])

            if answer == 1:
                while True:
                    profile = nt.Profile()
                    
                    login = ask_user(Style.NORMAL+Fore.BLACK+"\nPlease enter your patient ID number to login.\n\nID: ", int)

                    pat_frame = nt.search_data(login, patient_df, 'id', disp=False)
                    
                    if isinstance(pat_frame, bool):
                        continue
                    elif isinstance(pat_frame, pd.DataFrame):
                        loc = 0

                        for n in pat_frame.index:
                            if loc == 0:
                                loc = n
                            elif datetime.datetime.strptime(pat_frame.loc[n, 'update'], '%m/%d/%Y') > datetime.datetime.strptime(pat_frame.loc[loc, 'update'], '%m/%d/%Y'):
                                loc = n

                        profile.load_profile(pat_frame.loc[loc])
                        break

                    else:
                        profile.load_profile(pat_frame)
                        break

                break

            if answer == 2:
                os.system('cls')
                profile = nt.Profile()
                profile.name = ask_user(Style.NORMAL+"\nPlease enter your name: ", str)
                birthday = parser.parse(input("\nPlease enter your birthday (MM/DD/YYYY): "))
                profile.birthday = datetime.datetime.strftime(birthday, "%m/%d/%Y")
                profile.sex = user_response("\nPlease enter your the sex that most reflects your hormonal makeup (male/female): ", ['male', 'female'])
                feet = ask_user("\nPlease enter your current height (feet): ", int)
                inches = ask_user("\n Please enter your current height (inches): ", float)
                profile.height = (feet*12) + inches
                profile.weight = ask_user("\nPlease enter your current weight (lbs): ", float)
                profile.lifestyle = ask_user("\nHow active is your lifestyle?\n1. Sedentary\t2. Low physical activity\t3. Moderate physical activity\t4. High physical activity\n", int)
                profile.bmi = profile.weight / (profile.height**2)*703
                profile.goal = ask_user("\nWhat is your weight goal?\n1. Loss\t2. Maintenance\t3. Gain", int)
                profile.id = len(patient_df['id']) + 1
                profile.update = today.strftime('%m/%d/%Y')

                profile.calc_eer()

                res = user_response(Style.BRIGHT+"\nWould you like to save this profile? (Y/N)", ['y', 'n'])

                if res == 'y':
                    patient_df = profile.save_data(patient_df, patient_database)
                    print("\nYour patient ID is "+str(profile.id))
                    break
                else:
                    print(Style.NORMAL+Fore.RED+"\nData discarded.\n\n")
                    print(Fore.BLACK)

            if answer == 'dir':
                while True:
                    os.system('cls')
                    profile = nt.Profile()

                    category = user_response(Style.NORMAL+"\nPlease enter the category you would like to search:\n\n|\tName\t|\tBirthday\t|\tSex\t|\n\nCategory: ", ['name', 'birthday', 'sex'])
                    specific = input("\nSearch "+ category +": ")

                    pat_frame = nt.search_data(specific, patient_df, category, disp=True)

                    if isinstance(pat_frame, pd.DataFrame):
                        res = user_response("\nPlease enter the number of the option you would like to view: ", list(range(1, len(pat_frame.index)+1)))
                                
                        if res in ['all', 'none']:
                            pass
                        else:
                            os.system('cls')
                            pat_frame = pat_frame.iloc[res-1]
                            profile.load_profile(pat_frame)
                            profile.disp_info()

                    elif isinstance(pat_frame, pd.Series):
                        res = user_response(Style.BRIGHT+"\nWould you like to view this option? (Y/N)\n", ['y', 'n'])

                        if res == 'y':
                            os.system('cls')
                            profile.load_profile(pat_frame)
                            profile.disp_info()

                    res = input(Style.NORMAL+Fore.BLACK+'\nType any key to perform new search or type "exit" to return to main menu.\n')

                    if res == 'exit':
                        break

            if answer == 'info':
                os.system('cls')

                try:
                    with open(r"C:/Users/williamsben/OneDrive - Milwaukee School of Engineering/Nutrition Welcome.txt", "r") as f:
                        print(Style.NORMAL+Fore.BLACK+f.read())
                        f.close()
                except PermissionError:
                    print(Style.NORMAL+Fore.RED+"\nNutrition information file is currently in use. Please close file and try again to save.")
                    print(Fore.BLACK) 
                
                input('\nType any key to return to main menu.')

            if answer == 'quit': 
                run = False

        day = nt.Day(today.strftime('%m/%d/%Y'), profile.id)

        last_update = today - datetime.datetime.strptime(profile.update, '%m/%d/%Y')

        if last_update.days > 30:
            os.system('cls')
            print("___________"*10)
            print(Style.NORMAL+Fore.RED+f"\nIt has been {last_update.days} days since you last updated your profile.")
            res = user_response(Style.BRIGHT+Fore.BLACK+"\nHas any information changed in that time? (Y/N)\n", ['y', 'n'])
            
            if res== 'y':
                print(Style.NORMAL+"\nPlease select the following information to update: \n\n|\tHeight\t|\tWeight\t|\tLifestyle\t|\tGoal\t|\n")
                update_list = []

                while len(update_list) < 4:
                    sel = user_response('\nEnter option: ', ['height', 'weight', 'lifestyle', 'goal', 'end'])
                    if sel == 'end':
                        break
                    elif sel == 'all':
                        update_list = ['height', 'weight', 'lifestyle', 'goal']
                    else:
                        update_list.append(sel)

                for n in update_list:
                    match n:
                        case 'height':
                            feet = ask_user(Style.NORMAL+"\nPlease enter your current height (feet): ", int)
                            inches = ask_user("\n Please enter your current height (inches): ", float)
                            profile.height = (feet*12) + inches
                            profile.bmi = profile.weight / (profile.height**2)*703
                        case 'weight':
                            profile.weight = ask_user(Style.NORMAL+"\nPlease enter your current weight (lbs): ", float)
                            profile.bmi = profile.weight / (profile.height**2)*703
                        case 'lifestyle':
                            profile.lifestyle = ask_user(Style.NORMAL+"\nHow active is your lifestyle?\n1. Sedentary\t2. Low physical activity\t3. Moderate physical activity\t4. High physical activity\n", int)
                        case 'goal':
                            profile.goal = ask_user(Style.NORMAL+"\nWhat is your weight goal?\n1. Loss\t2. Maintenance\t3. Gain", int)
                
                profile.calc_eer()
                profile.update = today.strftime('%m/%d/%Y')
                print(profile.update)
                print(type(profile.update))
                patient_df = profile.save_data(patient_df, patient_database)
                print(Style.NORMAL+Fore.GREEN+"\nYour profile has been successfully updated.")
                print(Fore.BLACK)

        dvs = nt.daily_value(profile.eer)

        while run:
            os.system('cls')

            print("___________"*10)
            print(Style.BRIGHT+"\nWelcome " + profile.name+"!\n")

            day.summary(profile.eer, day_df, place='ldg')

            print("___________"*10)
            answer = user_response(Style.NORMAL+"\n1. Report meal\n2. View nutrition analysis and progress\n3. Add new food\n4. View food\n5. Create new recipe\n\nEnter selection: ", [1, 2, 3, 4, 5, 'exit', 'quit'])

            if answer == 1:
                os.system('cls')

                food = nt.Food()

                day.time = today.strftime('%I:%M:%S %p')

                day.meal = user_response(Style.NORMAL+"\nPlease enter which meal you are reporting:\n|\tBreakfast\t|\tLunch\t|\tDinner\t|\tSnack\t|\tDessert\t|\nMeal: ", ['breakfast', 'lunch', 'dinner', 'snack', 'dessert'])

                food_list = ''

                adding = True
                count = 1

                while adding:
                    os.system('cls')
                    
                    category = user_response(Style.NORMAL+Fore.BLACK+f"\nPlease enter the category of food #{count:.0f}:\n\n|\tName\t|\tType\t|\tBrand\t|\n\nCategory: ", ['name', 'type', 'brand'])
                    specific = input("\nSearch "+ category +": ")

                    food_frame = nt.search_data(specific, food_df, category, disp=True)
                        
                    if isinstance(food_frame, pd.DataFrame):
                        res = user_response(Style.BRIGHT+"\nPlease enter the number of the option you would like to view: ", list(range(1, len(food_frame.index)+1)))
                            
                        food_frame = food_frame.iloc[res-1]
                        food.load_food(food_frame)

                    elif isinstance(food_frame, pd.Series):
                        res = user_response(Style.BRIGHT+"\nWould you like to select this item? (Y/N)\n", ['y', 'n'])

                        if res == 'y':
                            food.load_food(food_frame)
                        else:
                            res = input(Fore.BLACK+'\nPress any key to search again or type "exit" to return to main menu. ')
                            if res == 'exit':
                                break
                            else:
                                continue
                    
                    elif food_frame is False:
                        res = input(Fore.BLACK+'\nPress any key to search again or type "exit" to return to main menu. ')
                        if res == 'exit':
                            break
                        else:
                            continue

                    serv_txt = input(Style.NORMAL+"\nHow many "+nt.add_s(food.measurement)+": ")
                
                    food_list += (food.name+'BREAK'+serv_txt+'BREAK')

                    res = user_response("\nWould you like to add another food (Y/N)?\n", ['y', 'n'])
                    if res == 'y':
                        count += 1
                    else:
                        adding = False

                os.system('cls')

                adjusted = nt.adjust(day, food_list, food_df) 
                day.load_date(adjusted.loc[0])
                day.summary(profile.eer, day_df, place='meal')

                res = user_response(Style.BRIGHT+"\nWould you like to save this meal to your daily tracker (Y/N)?\n", ['y', 'n'])
                if res == 'y':
                    day_df = day.save_data(day_df, day_database)

            if answer == 2:
                while True:
                    os.system('cls')

                    day.summary(profile.eer, day_df, place='anl')
                    res = input(Style.NORMAL+Fore.BLACK+'\nWould you like to view an analysis chart? If no, type "exit" to exit back to menu.')
                    
                    if res != 'exit':
                        res = user_response("\nPlease select a chart to view:\n1. Daily values\t2. Progress\t3. Plate proportions\t4. Caloric Density\n\nSelection: ", [1, 2, 3, 4])

                        match res:
                            case 1:
                                while True:
                                    os.system('cls')

                                    period = user_response(Style.NORMAL+"\nPlease enter the time period you would like to view this parameter over: \n|     today\t|    1 week\t|    2 weeks\t|    1 month\t|    3 months\t|    6 months\t|    1 year\t|    custom\t|\n", ['today', '1 week', '2 weeks', '1 month', '3 months', '6 months', '1 year', 'custom'])
                                    timef = nt.timepass(period)

                                    breakfastdf = nt.date_index(profile.id, timef, day_df, 'breakfast')
                                    lunchdf = nt.date_index(profile.id, timef, day_df, 'lunch')
                                    dinnerdf = nt.date_index(profile.id, timef, day_df, 'dinner')
                                    snackdf = nt.date_index(profile.id, timef, day_df, 'snack')
                                    dessertdf = nt.date_index(profile.id, timef, day_df, 'dessert')

                                    newbreakfast = {}
                                    newlunch = {}
                                    newdinner = {}
                                    newsnack = {}
                                    newdessert = {}

                                    dvals = pd.Series(dvs)
                                    daves = pd.DataFrame(np.float64(0), columns = ['Breakfast', 'Lunch', 'Dinner', 'Snack', 'Dessert'], index = dvals.index)
                                    
                                    time_range = timef[1] - timef[0]
                                    time_range = time_range.days+1
                                    max_time = day_df.loc[0, 'date']
                                    max_time = dt.strptime(max_time, '%m/%d/%Y')

                                    if max_time.date() > timef[0]:
                                        tstart = max_time.date()
                                    else:
                                            tstart = timef[0]

                                    time_range = timef[1] - tstart
                                    time_range = time_range.days+1

                                    for newdf, df in [(newbreakfast, breakfastdf), (newlunch, lunchdf), (newdinner, dinnerdf), (newsnack, snackdf), (newdessert, dessertdf)]:
                                        df.drop(columns = ['time', 'meal', 'id', 'foods'], inplace = True)
                                        df = nt.combdf(df)

                                        for n in df.columns:
                                            newdf[n] = df[n].sum() / time_range

                                    for num, dictionary in enumerate([newbreakfast, newlunch, newdinner, newsnack, newdessert]):
                                        for n in dictionary.keys():
                                            if n in dvals.index:
                                                daves.at[n, daves.columns[num]] = (dictionary[n] / dvals[n])*100
                                    
                                    daves.index = ['Calories', 'Total fat', 'Saturated fat', 'Cholesterol', 'Sodium', 'Carbohydrates', 'Dietary fiber', 'Added sugar', 'Protein']

                                    ytop = 90.0
                                    for n in daves.index:
                                        if daves.loc[n].sum() > 100.0:
                                            ytop = daves.loc[n].sum()

                                    mtitle, ttitle = nt.mp_title(False, timef)
                                    
                                    daves.plot(kind = 'bar', stacked=True, title = 'Daily Nutritional Intake from '+ttitle+mtitle, xlabel='Nutrients', ylabel='Percent Daily Value [%]', ylim = (0, ytop+10))
                                    plt.xticks(rotation=45, ha='right')
                                    plt.legend(loc='center left', title='Meal', bbox_to_anchor = (1, 0.5))
                                    plt.tight_layout()
                                    plt.show()

                                    cond = input(Style.NORMAL+'\nEnter any key to view new chart or type "exit" to exit. ')
                                    if cond == 'exit':
                                        break

                            case 2:
                                while True:
                                    os.system('cls')

                                    sel = user_response(Style.NORMAL+Fore.BLACK+'\nWould you like to view nutritional progress or weight progress?\n\nType option here: ', ['nutrition', 'weight', 'n', 'w'])
                                    par = ''
                                    meal = False
                                    
                                    if sel in ['nutrition', 'n']:
                                        parnum = ask_user("\nPlease enter the parameter that you would like to view:\n\n1. Calories\t\t2. Total fat\t\t3. Saturated fat\n4. Trans fat\t\t5. Polyunsaturated fat\t6. Monounsaturated fat\n7. Cholesterol\t\t8. Sodium\t\t9. Carbohydrates\n10. Dietary fiber\t11. Soluble fiber\t 12. Sugar\n13.Added sugar\t\t14. Protein\n\nSelection: ", int)

                                        period = user_response("\nPlease enter the time period you would like to view this parameter over: \n|    1 week\t|    2 weeks\t|    1 month\t|    3 months\t|    6 months\t|    1 year\t|    custom\t|\n", ['1 week', '2 weeks', '1 month', '3 months', '6 months', '1 year', 'custom'])
                                        timef = nt.timepass(period)

                                        meal = user_response("\nWould you like to view this chart for a specific meal (Y/N)?\n", ['y', 'n'])
                                        if meal == 'y':
                                            meal = user_response("\nPlease enter the meal you would like to view:\n\n|\tBreakfast\t|\tLunch\t|\tDinner\t|\tSnack\t|\tDessert\t|\n\nMeal: ", ['breakfast', 'lunch', 'dinner', 'snack', 'dessert'])
                                        else:
                                            meal = False

                                        ddata = nt.date_index(profile.id, timef, day_df, meal)
                                        if isinstance(meal, str):
                                            ddata = ddata.loc[ddata['meal'] == meal]
                                            if ddata.empty:
                                                print(Fore.RED+'\nNo data entered for this meal')
                                                res = input(Fore.BLACK+'\nPress any key to search again or type "exit" to return to main menu. ')
                                                if res == 'exit':
                                                    break
                                                else:
                                                    continue

                                        ddata.drop(columns = ['time', 'meal', 'id', 'foods'], inplace = True)
                                        parameter = ddata.columns[parnum - 1]
                                        ddata = ddata[parameter]

                                        newdaydf = nt.combine(ddata)
                                        plti, yl, isave = nt.plotti(parameter)
                                        mtitle, ttitle = nt.mp_title(meal, timef)

                                        newdaydf.plot(title= "Daily "+plti.title()+' Intake of '+profile.name+' from '+ttitle+mtitle, xlim = (timef[0], timef[1]), xlabel = 'time', ylabel = plti.title()+' '+yl, legend=True, label='Patient daily value', color = 'deepskyblue')

                                        if meal in ['snack', 'dessert']:
                                            multiplier = 1 / 8
                                        elif meal in ['breakfast', 'lunch', 'dinner']:
                                            multiplier = 0.25
                                        else:
                                            multiplier = 1
                                        
                                        if isave and parameter != 'calories':
                                            plt.plot([timef[0], timef[1]], [multiplier*dvs[parameter], multiplier*dvs[parameter]], label='Recommended daily value', linestyle = '--', color = 'gray')

                                        ave = newdaydf.mean()
                                        if parameter in dvs.keys():
                                            color = nt.color(parameter, ave, multiplier*dvs[parameter])
                                        else: 
                                            color = 'gray'

                                        plt.plot([timef[0], timef[1]], [ave, ave], label='Average', color = color, linestyle = '--')

                                        if parameter == 'calories':
                                            sel = 'weight'
                                            par = 'eer'

                                    if sel in ['weight', 'w']:
                                        if par != 'eer':
                                            par = user_response(Style.NORMAL+Fore.BLACK+"\nPlease enter the parameter that you would like to view:\n\n|\tWeight\t|\tBMI\t|\n\nSelection: ", ['weight', 'bmi'])

                                            period = user_response("\nPlease enter the time period you would like to view this parameter over: \n|    1 week\t|    2 weeks\t|    1 month\t|    3 months\t|    6 months\t|    1 year\t|    custom\t|\n", ['1 week', '2 weeks', '1 month', '3 months', '6 months', '1 year', 'custom'])
                                            timef = nt.timepass(period)

                                            multiplier = 1

                                        ddata = patient_df.copy()
                                        ddata = ddata[ddata['id'] == profile.id]
                                        ddata = ddata[[par, 'update']]
                                        ddata['update'] = pd.to_datetime(ddata['update'])
                                        ddata.set_index(ddata['update'], inplace = True)
                                        ddata.drop(columns = 'update', inplace = True)
                                        ddata.loc[today] = ddata.iloc[len(ddata.index)-1, 0]

                                        days = pd.date_range(start=ddata.index[0], end=timef[1])

                                        serplot = pd.Series(float('NaN'), index = days)

                                        for row in ddata.index:
                                            if row in serplot.index:
                                                serplot[row] = ddata.at[row, par]*multiplier

                                        serplot = serplot.ffill()
                                        serplot = serplot.truncate(before = timef[0])

                                        if par in dvs.keys():
                                            if serplot.max() > dvs[par]:
                                                ytop = serplot.max()*(1 / multiplier)
                                            else:
                                                ytop = dvs[par]*(1 / multiplier)
                                        else:
                                            ytop = serplot.max()*(1 / multiplier)

                                        if par == 'eer':
                                            color = 'gray'
                                            lined = '--'
                                        else: 
                                            color = 'deepskyblue'
                                            lined = '-'
                                        
                                        plti, yl, isave = nt.plotti(par)
                                        mtitle, ttitle = nt.mp_title(meal, timef)
                                        serplot.plot(title = plti+' of '+profile.name+' from '+ttitle+mtitle, xlim = (timef[0], timef[1]), ylim = (0, ytop+(0.2*ytop)), label=plti, xlabel = 'time', ylabel=plti+' '+yl, linestyle = lined, drawstyle = 'steps-post', color = color)
                                        
                                    plt.legend(loc='center left', title='Legend', bbox_to_anchor = (1, 0.5))
                                    plt.ylim(ymin = 0)
                                    plt.tight_layout()
                                    plt.show()

                                    cond = input('\nEnter any key to view new chart or type "exit" to exit. ')
                                    if cond == 'exit':
                                        break

                            case 3:
                                while True:
                                    os.system('cls')

                                    parameter = user_response(Style.NORMAL+Fore.BLACK+"\nWould you like to view a chart for the 1) food type or the 2) composition?\n", [1, 2])
                                    period = user_response("\nPlease enter the time period you would like to view this parameter over: \n|    today\t|     1 week\t|    2 weeks\t|    1 month\t|    3 months\t|    6 months\t|    1 year\t|    custom\t|\n", ['today', '1 week', '2 weeks', '1 month', '3 months', '6 months', '1 year', 'custom'])
                                    timef = nt.timepass(period)

                                    meal = user_response("\nWould you like to view this chart for a specific meal (Y/N)?\n", ['y', 'n'])
                                    if meal == 'y':
                                        meal = user_response("\nPlease enter the meal you would like to view:\n\n|\tBreakfast\t|\tLunch\t|\tDinner\t|\tSnack\t|\tDessert\t|\n\nMeal: ", ['breakfast', 'lunch', 'dinner', 'snack', 'dessert'])
                                    else:
                                        meal = False

                                    ddata = nt.date_index(profile.id, timef, day_df, meal)
                                    ddata = ddata['foods']
                                    
                                    foods = ''
                                    if ddata.empty:
                                        print(Fore.RED+"\nNo data entered for this meal")
                                        res = input(Fore.BLACK+'\nPress any key to search again or type "exit" to return to main menu. ')
                                        if res == 'exit':
                                            break
                                        else:
                                            continue

                                    else:
                                        foods = ddata.sum()
                                        flist = foods.split('BREAK')
                                        flist.remove('')
                                    
                                    fooddf = food_df.copy()
                                    
                                    fooddf = fooddf.drop_duplicates(subset = 'name', inplace = False)
                                    fooddf.set_index('name', inplace = True)
                                    fooddf.replace(float('NaN'), 0, inplace = True)

                                    flist = nt.ingredients_list(flist, fooddf)

                                    if parameter == 1:
                                        typedict = {'grain':0, 'protein': 0, 'fruit':0, 'vegetable':0, 'dairy':0, 'other':0}

                                        total = 0

                                        for n in range(0, len(flist)-1, 2):
                                            fname = flist[n]
                                            servings = flist[n+1]
                                            servings = nt.split_serv(servings)

                                            for cat in typedict.keys(): 
                                                if fooddf.at[fname, 'type'] == cat:
                                                    multi = servings[0] / fooddf.at[fname, 'size']
                                                    typedict[cat] += fooddf.at[fname, 'weight']*multi
                                                    total += fooddf.at[fname, 'weight']*multi                                                    

                                        for cat in typedict.keys():
                                            typedict[cat] = (typedict[cat] / total)*100

                                        piedf = pd.Series(typedict)

                                        colors = ['darkorange', 'blueviolet', 'red', 'yellowgreen', 'dodgerblue', 'gray']
                                        title = 'MyPlate Proportions for '+profile.name.title()+' from '

                                    elif parameter == 2:
                                        compdict = {'carbohydrates':0, 'lipids':0, 'proteins':0}
                                        
                                        total = 0

                                        for n in range(0, len(flist)-1, 2):
                                            fname = flist[n]
                                            servings = flist[n+1]
                                            servings = nt.split_serv(servings)
                                            multi = servings[0] / fooddf.at[fname, 'size']

                                            for ing in ['carbohydrates', 'sugar', 'addedsugar']:
                                                compdict['carbohydrates'] += fooddf.at[fname, ing]*multi*4
                                            
                                            compdict['lipids'] += fooddf.at[fname, 'totalfat']*multi*9
                                            compdict['lipids'] += (fooddf.at[fname, 'cholesterol'] / 1000)*multi*9
                                            compdict['proteins'] += fooddf.at[fname, 'protein']*multi*4
                                                        
                                            for k in compdict.keys():
                                                total += compdict[k]

                                        for cat in compdict.keys():
                                                compdict[cat] = (compdict[cat] / total)*100

                                        piedf = pd.Series(compdict)
                                        
                                        colors = ['darkorange', 'gold', 'tomato']
                                        title = 'Macronutrition Proportions for '+profile.name.title()+' from ' 

                                    mtitle, ttitle = nt.mp_title(meal, timef)
                                    piedf.plot(kind = 'pie', title=title+ttitle+mtitle, autopct='%1.1f%%', colors = colors, shadow=True, startangle=140)
                                    plt.tight_layout()
                                    plt.legend(loc='center left', title='Legend', bbox_to_anchor = (1, 0.5))
                                    plt.show()

                                    cond = input('\nEnter any key to view new chart or type "exit" to exit. ')
                                    if cond == 'exit':
                                        break
                            case 4:
                                while True:
                                    os.system('cls')

                                    period = user_response(Style.NORMAL+Fore.BLACK+"\nPlease enter the time period you would like to view this parameter over: \n|    1 week\t|    2 weeks\t|    1 month\t|    3 months\t|    6 months\t|    1 year\t|    custom\t|\n", ['1 week', '2 weeks', '1 month', '3 months', '6 months', '1 year', 'custom'])
                                    timef = nt.timepass(period)

                                    ddata = nt.date_index(profile.id, timef, day_df, False)
                                    ddata = ddata['foods']

                                    foods = ''

                                    if ddata.empty:
                                        print(Fore.RED+"\nNo data entered for this meal")
                                        res = input(Fore.BLACK+'\nPress any key to search again or type "exit" to return to landing page. ')
                                        if res == 'exit':
                                            break
                                        else:
                                            continue
                                    else:
                                        foods = ddata.sum()
                                        flist = foods.split('BREAK')
                                        flist.remove('')

                                    fooddf = food_df.copy()
                                    fooddf.drop_duplicates(subset = 'name', inplace = True)
                                    fooddf.set_index('name', inplace = True)
                                    fooddf.replace(float('NaN'), 0, inplace = True)

                                    freq = []
                                    amount = []
                                    labels = []

                                    for n in fooddf.index:
                                        if n not in flist:
                                            fooddf.drop(index = n, inplace = True)
                                        else:
                                            freq.append(flist.count(n))
                                            serving = [nt.split_serv(flist[m+1]) for m in range(len(flist)) if flist[m] == n]
                                            serving = [t[0]/fooddf.loc[n, 'size'] for t in serving]
                                            serving = nt.list_ave(serving)
                                            amount.append(serving)
                                            labels.append(n)
                                    
                                    for i in range(len(freq)):
                                        plt.annotate(labels[i], (freq[i], amount[i]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8)
                                    
                                    density = [fooddf.loc[n, 'calories'] / fooddf.loc[n, 'weight'] for n in fooddf.index]
                                    norms = Normalize(vmin = 0, vmax=9)

                                    mtitle, ttitle = nt.mp_title(False, timef)
                                    
                                    plt.scatter(freq, amount, c = density, cmap = 'RdYlGn_r', norm = norms, s = 100)
                                    plt.title('Caloric Density of Foods Consumed by '+profile.name+' from '+ttitle+mtitle)
                                    plt.tight_layout()
                                    plt.xlabel('Frequency consumed')
                                    plt.ylabel('Average servings')
                                    plt.ylim(ymin = 0)
                                    plt.xlim(xmin = 0)
                                    plt.colorbar()
                                    plt.show()

                                    cond = input('\nEnter any key to view new chart or type "exit" to exit. ')
                                    if cond == 'exit':
                                        break
                    
                    if res == 'exit':
                        break

            if answer == 3:
                os.system('cls')

                food = nt.Food()

                food.name = input(Style.NORMAL+Fore.BLACK+"\nPlease enter the food name: ")
                food.type = input("\nPlease enter the food type: ")
                food.brand = input("\nPlease enter the food brand: ")
                food.weight = ask_user("\nPlease enter the serving weight (g): ", float)
                size_text = input("\nPlease enter the serving size: ")
                szm = nt.split_serv(size_text)
                food.size = szm[0]
                food.measurement = szm[1]
                food.calories = ask_user("\nPlease enter the amount of calories (Calories): ", float)
                food.totalfat = ask_user("\nPlease enter the amount of total fat (g): ", float)
                food.saturated = ask_user("\nPlease enter the amount of saturated fat (g): ", float)
                food.trans = ask_user("\nPlease enter the amount of trans fat (g): ", float)
                food.polyunsaturated = ask_user("\nPlease enter the amount of polyunsaturated fat (g): ", float)
                food.monounsaturated = ask_user("\nPlease enter the amount of monounsaturated fat (g): ", float)
                food.cholesterol = ask_user("\nPlease enter the amount of cholesterol (mg): ", float)
                food.sodium = ask_user("\nPlease enter the amount of sodium (mg): ", float)
                food.carbohydrates = ask_user("\nPlease enter the amount of total carbohydrates (g): ", float)
                food.dietaryfiber = ask_user("\nPlease enter the amount of dietary fiber (g): ", float)
                food.solublefiber = ask_user("\nPlease enter the amount of soluble fiber (g): ", float)
                food.sugar = ask_user("\nPlease enter the amount of sugar (g): ", float)
                food.addedsugar = ask_user("\nPlease enter the amount of added sugar (g): ", float)
                food.protein = ask_user("\nPlease enter the amount of protein (g): ", float)

                res = user_response(Style.BRIGHT+"\nWould you like to save this food (Y/N)?\n", ['y', 'n'])

                if res == 'y':
                    food_df = food.save_data(food_df, food_database)

                else:
                    print(Fore.RED+"\nData discarded.\n\n")

            if answer == 4:
                food = nt.Food()
                while True:
                    os.system('cls')

                    category = user_response(Style.NORMAL+Fore.BLACK+"\nPlease enter the category you would like to search:\n\n|\tName\t|\tType\t|\tBrand\t|\n\nCategory: ", ['name', 'type', 'brand', 'all'])
                    specific = input("\nSearch "+ category +": ")

                    food_frame = nt.search_data(specific, food_df, category, disp=True)

                    if isinstance(food_frame, pd.DataFrame):
                        res = user_response("\nPlease enter the number of the option you would like to view: ", list(range(1, len(food_frame.index)+1)))

                        food_frame = food_frame.iloc[res-1]
                        food.load_food(food_frame)
                        os.system('cls')
                        food.disp_info(profile.eer)

                    elif isinstance(food_frame, pd.Series):
                        res = user_response(Style.BRIGHT+"\nWould you like to view this item? (Y/N)\n", ['y', 'n'])

                        if res == 'y':
                            food.load_food(food_frame)
                            os.system('cls')
                            food.disp_info(profile.eer)
                    
                    res = input(Style.NORMAL+Fore.BLACK+'\nType any key to search again or type "exit" to main menu.')

                    if res == 'exit':
                        break
            
            if answer == 5:
                os.system('cls')
                recipe = nt.Food()
                recipe_list = ''
                
                recipe.name = input(Style.NORMAL+Fore.BLACK+"\nPlease enter the name of the recipe: ")
                servings = input("\nPlease enter the serving measurement of the recipe: ")
                (recipe.size, recipe.measurement) = nt.split_serv(servings)

                adding = True
                count = 1

                while adding:

                    category = user_response(Style.NORMAL+Fore.BLACK+f"\nPlease enter the category of ingredient #{count:.0f}:\n\n|\tName\t|\tType\t|\tBrand\t|\n\nCategory: ", ['name', 'type', 'brand', 'all'])
                    specific = input("\nSearch "+ category +": ")

                    food_frame = nt.search_data(specific, food_df, category, disp=True)
                        
                    if isinstance(food_frame, pd.DataFrame):
                        res = user_response("\nPlease enter the number of the option you would like to view: ", list(range(1, len(food_frame.index)+1)))

                        food_frame = food_frame.iloc[res-1]
                        recipe_name = food_frame['name']

                    elif isinstance(food_frame, pd.Series):
                        res = user_response(Style.BRIGHT+"\nWould you like to select this item? (Y/N)\n", ['y', 'n'])

                        if res == 'y':
                            recipe_name = food_frame['name']
                        else:
                            res = input(Fore.BLACK+'\nPress any key to search again or type "exit" to return to main menu. ')
                            if res == 'exit':
                                break
                            else:
                                continue

                    elif food_frame is False:
                        res = input(Fore.BLACK+'\nPress any key to search again or type "exit" to return to main menu. ')
                        if res == 'exit':
                            break
                        else:
                            continue

                    serv_txt = input(Style.NORMAL+"\nHow many "+nt.add_s(food_frame['measurement'])+": ")

                    recipe_list += (recipe_name+'BREAK'+serv_txt+'BREAK')

                    res = user_response(Style.BRIGHT+"\nWould you like to add another ingredient (Y/N)?\n", ['y', 'n'])
                    if res == 'y':
                        count += 1
                        os.system('cls')
                    else:
                        adding = False
                
                adjusted = nt.adjust(recipe, recipe_list, food_df) 

                os.system('cls')

                print(Style.BRIGHT+"\nFinal Recipe:")
                recipe.disp_info(profile.eer)

                res = user_response(Style.BRIGHT+"\nWould you like to save this recipe (Y/N)?\n", ['y', 'n'])
                if res.lower() == 'y':
                    food_df = recipe.save_data(food_df, food_database)

            if answer == 'exit':
                break

            if answer == 'quit': 
                run = False
                exit()

if __name__ == '__main__':
    main()