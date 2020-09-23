from sqlalchemy import create_engine, Table , Column, Integer, String, ForeignKey, Text, ARRAY, MetaData, Date,exc
from sqlalchemy.ext.declarative import declarative_base
from selenium import webdriver
from sqlalchemy.orm import  backref, sessionmaker
import pandas 

engine = create_engine("postgres://postgres:@127.0.0.1/track_parcel1", echo = True) # bind engine with PostgreSQL database

Base = declarative_base()

Session = sessionmaker(bind=engine) # bound session
session = Session()

class Parcel(Base):  # table which stores information about user parcels
    __tablename__ = "parcel"
    parcel_id = Column(Integer, primary_key=True) 
    track_number = Column(String(50), nullable=False) # every parcel have unique track - number which allows to track it's tranfers
    track_status_date = Column(String(20))   # stores last parcel status date
    track_info = Column(String(50), nullable=False)  #stores last information about parcel transfers
    
    def __init__(self, track_number, track_status_date, track_info):
        self.track_number = track_number
        self.track_status_date = track_status_date
        self.track_info = track_info
    
    
Base.metadata.create_all(engine)
    

def getting_site_data(track_num , filename = 'parcel_info.csv'):  # 'JNTCU3000376688YQ'
    try:
        # immitation of user actions and data scraping using Selenium and google webdriver
        driver = webdriver.Chrome() 
        driver.get("https://gdeposylka.ru/")  # Launch website
        search_field = driver.find_element_by_xpath('//*[@id="tracking_form_tracking_number"]')
        cl_button = driver.find_element_by_xpath('//*[@id="tracking_form_track"]')
        search_field.send_keys(track_num)
        cl_button.click()
        i, site_data = 1, []
        while True:    # until NoSuchElementException occured
            site_data.append(driver.find_element_by_xpath(f'//*[@id="fragment-checkpoints"]/ul/li[{i}]').text)
            i += 1
    except:
        pass
    
    driver.close()
    if not site_data:
        print('An error occured. Maybe you entered invalid data. Restart the program and repeat your request ' )
    date_list, status_list, postal_operator_list = [], [], []

    for data in site_data:
        data = data.split('\n')
        date_list.append(data[0] + ' ' + data[1])
        status_list.append(data[2])
        postal_operator_list.append(data[3])
        
    #adding parcel info into database
    new_parcel = Parcel(track_num,date_list[-1], status_list[-1]) #creating Parcel object
    session.add(new_parcel)
    session.commit()
    
    
    #creating and saving formatted data into .csv file
    if input('Do you want to save full information about the parcel into .csv file ?  yes/no') == 'yes':
        file_name = input('Enter the filename you want to save data about your parcel : ')
        parcel_info_table = pandas.DataFrame(
        { 
            'Date' : date_list, 
            'Parcel status': status_list, 
            'Postal operator':postal_operator_list
        })

        parcel_info_table.to_csv(file_name + '.csv')   #saving  into .csv file 
        print('Information was successfully written into file ')


def get_track_info(track_num):

    track = session.query(Parcel).filter(Parcel.track_number == track_num).order_by(Parcel.parcel_id)
    res = track.one_or_none()
    if res:
        return ('\n'+ f'The latest track information for {res.track_status_date} with status {res.track_info}' + '\n')
    return ('\n'+ 'Unfortunately you have not added this track number for tracking yet. Use "add" command on the next iteration. ' + '\n')
       

choice = ''
while choice!= 'end':
    choice = input('''What would you like to do?  Enter one of the commands:
                'show' - for showing status of one of your order ;
                'add' - for adding new parcel track-number for tracking ;
                'end' - for closing the program.
                ''')

    if choice == 'show':
        track_number = input('Enter enter required parcel  track-number:  ')
        print(get_track_info(track_number))
    
    if choice == 'add':
        track_number = input('Enter parcel  track-number you want to add :  ')
        getting_site_data(track_number)


