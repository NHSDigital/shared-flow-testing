from jsonschema import validate
import json

class TestSplunkLoging:
    def test_firstTest(self):


        with open('test_splunk/sample.json') as f:
            sample = json.load(f)
        
        with open('test_splunk/splunk_logging_schema.json') as f:
            schema = json.load(f)
       

        # A sample schema, like what we'd get from json.load()
        # schema = {
        #     "type" : "object",
        #     "properties" : {
        #         "price" : {"type" : "number"},
        #         "name" : {"type" : "string"},
        #     },
        # }

        # If no exception is raised by validate(), the instance is valid.
        validate(instance=sample, schema=schema)

        # validate(
        #     instance={"name" : "Eggs", "price" : "Invalid"}, schema=schema,
        # )                                   # doctest: +IGNORE_EXCEPTION_DETAIL


