---
name: External API
---

# External API

The **ExtensiveTesting** solution can be controled throught the `REST API`.

The authentication can be done with 2 differents way:

- API key (need a specific account), execute the script **generate-apikey.py** to obtain a the api key to use
      
    ```  
    # /opt/xtc/current/Scripts/generate-apikey.py --user=api
    API Key ID: api
    API Key Secret: 9a273099bad03199cda7d32c798e5d82cfc37ee4
    API Key: YXBpOjlhMjczMDk5YmFkMDMxOTljZGE3ZDMyYzc5OGU1ZDgyY2ZjMzdlZTQ=
    ```
    
    Add the api Key in the Authorization header of your request
    
    ```
    Authorization: Basic YXBpOjlhMjczMDk5YmFkMDMxOTljZGE3ZDMyYzc5OGU1ZDgyY2ZjMzdlZTQ=
    ```

- Cookie (you can use directly your account use on with the client)


Read the [swagger documentation](https://demo.extensive-testing.org/web/api-rest/index.html) for more informations about the functions availables.