from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine, ForeignKeyConstraint
from sqlalchemy.orm import sessionmaker
import os
import csv
import datetime

db_url = 'sqlite:///app.db'
engine = create_engine(db_url, echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Country(Base):
    __tablename__ = 'countries'
    name = Column(String, primary_key=True)

    dataPoints = relationship("DataPoint", back_populates="country")

    def __repr__(self):
        return "Country<(name={})>".format(self.name)

class DataPoint(Base):
    __tablename__ = 'dataPoints'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    country_name = Column(String, ForeignKey('countries.name'))
    country = relationship("Country", back_populates="dataPoints")
    value = Column(Integer)
    eventType_name = Column(String, ForeignKey('eventTypes.name'))
    eventType = relationship("EventType", back_populates="dataPoints")
    final = Column(Boolean)

    def __repr__(self):
        return "DataPoint<(blerp)>"

class EventType(Base):
    __tablename__ = 'eventTypes'
    name = Column(String, primary_key=True)
    category = Column(String)
    dataPoints = relationship("DataPoint", back_populates="eventType")

    def __repr__(self):
        return "EventType<(name={}, category={})>".format(self.name, self.category)

def populateCountries():
    dbSession = Session()
    dirName = "COVID-19/csse_covid_19_data/csse_covid_19_time_series"
    fBaseName = "time_series_19-covid"
    fName = "{}-{}.csv".format(fBaseName, 'Confirmed')
    fPath = os.path.join(dirName, fName)
    with open(fPath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            country = Country(name=row['Country/Region'])
            country = dbSession.merge(country)
    dbSession.commit()
    dbSession.close()


def populateData():
    dbSession = Session()
    dirName = "COVID-19/csse_covid_19_data/csse_covid_19_time_series"
    fBaseName = "time_series_19-covid"
    et = EventType(name='Confirmed')
    et = dbSession.merge(et)
    fName = "{}-{}.csv".format(fBaseName, 'Confirmed')
    fPath = os.path.join(dirName, fName)
    with open(fPath, 'r') as f:
        reader = csv.DictReader(f)
        seenCountries = []
        for row in reader:
            country = Country(name=row['Country/Region'])
            country = dbSession.merge(country)
            if country in seenCountries:
                seen = True
            else:
                seen = False
                seenCountries.append(country)
            for d, value in row.items():
                if d in ['Province/State','Country/Region','Lat','Long',]:
                    continue
                #wow what a bad date format
                dTmp = [int(t) for t in d.split('/')]
                dNew = "{:02d}/{:02d}/20{:02d}".format(*dTmp)
                date = datetime.datetime.strptime(dNew, "%m/%d/%Y")
                if not seen:
                    dp = DataPoint(
                        date = date,
                        value = value,
                    )
                    dp.country = country
                    dp.eventType = et
                    dbSession.add(dp)
                else:
                    dp = dbSession.query(DataPoint).filter(
                            DataPoint.date == date
                        ).filter(
                            DataPoint.country_name == country.name
                        ).one()
                    try:
                        dp.value += value
                    except TypeError:
                        print('!!!!!!!!!!!! {}'.format(value))


    dbSession.commit()
    dbSession.close()

