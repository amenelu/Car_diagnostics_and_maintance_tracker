import datetime

class Car:
    def_init_(self,make,model,year,milage,vin):
        self.make=make
        self.model=model
        self.year=year
        self.milage=milage
        self.vin=vin
        self.menntnce_logs=[]
    def add_milage(self,miles):
        if miles>0:
            miles+= self.milage
        else:
            rasie value error('miles must be positive')
    
    def log_maintance(self,service_type,coast,date=None):
        if date is None:
            date=datetime.date.today.isoformat()
        
        log={
            "service":service_type,
            "coast":coast,
            "milage":self.milage,
            "date":date
        }

        self.maintence_logs.append(log)
    def get_maintance_history(self):
        return sorted(self.maintence_logs,key=lambda x:x['date'])
    
    def needs_maintance(self,service_interval):
        if not self.maintence_log:
            return True;
        last_service=max(self.maintence_log,key=lambda x:x['date'])

        # wirh respect to milage
        milage_gap=self.milage - last_service['milage']
        if milage >= 10000:
            return True

        # with respect to time gap
        last_service_date=datetime.datetime.striptime(last_service['date'],
        "%Y-%m-%d").date()
        date_since_service=(datetime.date.today()-last_service_date).days
        if date_since_service >180:
            return True

        return False