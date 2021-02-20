# Grocery Saver
Author: Rui Li

Semester: Fall 2020

Contact Information: ruili2020@ischool.berkeley.edu

## Overview of Project

With this project, I intend to build a price comparison program for grocery shopping. User can upload a grocery list to this program. The program takes the grocery list then search on the website of a few major local grocery stores (Walmart, Kroger, Meijer, Audi, Giant Eagle, etc.) to get the price and unit price, then provides a price comparison ( both for total price, and total unit price) for the uploaded grocery list. Users can select all grocery store, all pick some to compare. Users can also switch the comparison between total price or unit price. Basing on the user selection, the program will suggest the user which store to shop for the items on the grocery list.

## Instruction
•	Go to terminal and navigate to the GrocerySaver folder

•	Type in python GrocerySaver.py to launch the program

![ScreenShot](/LaunchProgram.jpg)
    
•	Type in Grocery items

•	Select at least a store (or multiple stores)

•	Select the saving option: by total price or by unit price

•	Click on the “Compare Price” button

•	The Price Comparison window will pop up and display suggestion

 ![ScreenShot](/PriceComparison.jpg)

## Reflection
This project is working as designed as the proposal. Using tkinter for UI, sqlite for database and requests for API calls.
Main functions
•	The Grocery Saver UI takes the grocery lists entered by the user and save the grocery list to a csv file for later use
•	The Grocery Saver UI takes the store selections made by the user and save the store list to csv files for later use
•	User input validation – if the grocery list is empty or store is not selected, notification window will pop up
•	By Total Price and By Unit Price option on UI is for user to pick the price saving model
•	Once clicking “Compare Price” button, the program will loop through each store and check price of each item on the shopping list.
•	Check price function supports both checking price from the SQLite database or checking from the store API
Main challenges

1.	It was not easy to get the API working. I’ve got Kroger API working and successfully call Kroger API to retrieve grocery item information. Not all grocery stores have API available. Some stores (like Walmart) have API, however, it doesn’t allow new application to register for API due to holiday season.

I overcame this problem by switching gear to load grocery price by store to SQLite database. I developed the databases and the SQLite connections to retrieve grocery item information.

Also, I stored the indicator whether a store has API, and check DB price or API price basing on if store API is available. This is for ease and flexibility of API extension in the future . If the store API is available in the future, I can easily extend and switch the API on.
 
2.	Get the repr to display in a nice format was also challenging.
It took me a while to display the estimated receipt in aligned columns. I overcame the issue by
using .ljust(length, “-“), so the columns are all in the same length and left aligned.


