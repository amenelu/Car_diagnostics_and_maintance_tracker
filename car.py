class Car:
    def_init_(self,make,model,year,milage,vin):
        self.make=make
        self.model=model
        self.year=year
        self.milage=milage
        self.vin=vin
        self.menntnce_logs=[]
    def add_milge(self,miles):
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
