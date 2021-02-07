API Access
==========

Duplicate Checker may be accessed via a web-based API, permitting it to be
integrated into existing platforms such as Case Management Systems or Clinical
Database Management Systems. Authentication is handled via a user-specific API
key provided by the system administrator. It is critical that this key be
stored and used in a secure manner.

The API has just two endpoints, as described below.

.. http:post:: /check
   
   Checks for previously enrolled participants who share the same information
   
   **Example request**
   
   .. sourcecode:: http
   
      POST /check HTTP/1.1
      Host: https://rcg.bsd.uchicago.edu/jcoin/duplicate-checker
   
   **Example response**
   
   .. sourcecode:: http
   
      HTTP/1.1 200 OK
      Content-Type: application/json
      
      {
         "duplicates":[
            {
               "recruited_by":"pschumm",
               "recruitment_date":"02/06/2021 07:24 PM CST",
               "site":"University of Chicago"
            }
         ]
      }
   
   :form api_key: API key
   :form first_initial: First letter of first name (caps insensitive)
   :form last_initial: First letter of last name (caps insensitive)
   :form dob: Date of birth in mm/dd/yyyy format
   :form sex: One of "Male" or "Female"
   :resheader Content-Type: application/json
   :>json array duplicates: List of duplicates (empty if no duplicates found),
                            each indicating the location where the participant
                            was recruited ("site"), the date on which the
                            participant was entered ("recruitment_date"), and
                            the user who entered the participant (("recruited_by").
   :>json string message: In case of an unsuccessful request, indicates nature
                          of the error
   :statuscode 200: Successful request
   :statuscode 400: Invalid request
   :statuscode 401: Unauthorized request

.. http:post:: /add
   
   Add new participant to the database
   
   **Example request**
   
   .. sourcecode:: http
   
      POST /add HTTP/1.1
      Host: https://rcg.bsd.uchicago.edu/jcoin/duplicate-checker
   
   **Example response**
   
   .. sourcecode:: http
   
      HTTP/1.1 200 OK
      Content-Type: application/json
      
      {
         "message":"Participant added"
      }
   
   :form api_key: API key
   :form first_initial: First letter of first name (caps insensitive)
   :form last_initial: First letter of last name (caps insensitive)
   :form dob: Date of birth in mm/dd/yyyy format
   :form sex: One of "Male" or "Female"
   :resheader Content-Type: application/json
   :>json string message: Equal to "Participant added" if the request was
                          successful, otherwise indicates nature of the error
   :statuscode 200: Successful request
   :statuscode 400: Invalid request
   :statuscode 401: Unauthorized request
