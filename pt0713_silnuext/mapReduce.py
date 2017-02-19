import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import sodapy

class property_crime(dml.Algorithm):
    contributor = 'pt0713_silnuext'
    reads = []
    writes = ['pt0713_silnuext.property_crime']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('pt0713_silnuext', 'pt0713_silnuext')

        client = sodapy.Socrata("data.cityofboston.gov", None)
        response = client.get("crime")
        #r = json.loads(response)
        s = json.dumps(response, sort_keys=True, indent=2)
        print(s)
        repo.dropCollection("property_crime")
        repo.createCollection("property_crime")
        repo['pt0713_silnuext.property_crime'].insert_many(response)
        repo['pt0713_silnuext.property_crime'].metadata({'complete':True})
        print(repo['pt0713_silnuext.property_crime'].metadata())

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start":startTime, "end":endTime}
    
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('pt0713_silnuext', 'pt0713_silnuext')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:pt0713_silnuext#example', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:wc8w-nujj', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_property_crime = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_property_crime, this_script)

        doc.usage(get_property_crime, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?type=Animal+property_crime&$select=type,latitude,longitude,OPEN_DT'
                  }
                  )

        property_crime = doc.entity('dat:pt0713_silnuext#property_crime', {prov.model.PROV_LABEL:'Animals property_crime', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(property_crime, this_script)
        doc.wasGeneratedBy(property_crime, get_property_crime, endTime)
        doc.wasDerivedFrom(property_crime, resource, get_property_crime, get_property_crime, get_property_crime)


        repo.logout()
                  
        return doc

property_crime.execute()
doc = property_crime.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof


