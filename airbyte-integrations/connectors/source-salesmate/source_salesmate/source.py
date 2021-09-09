# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
import json
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator

"""
TODO: Most comments in this class are instructive and should be deleted after the source is implemented.

This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.json file.
"""


# Basic full refresh stream
class SalesmateStream(HttpStream, ABC):
    """
    TODO remove this comment

    This class represents a stream output by the connector.
    This is an abstract base class meant to contain all the common functionality at the API level e.g: the API base URL, pagination strategy,
    parsing responses etc..

    Each stream should extend this class (or another abstract subclass of it) to specify behavior unique to that stream.

    Typically for REST APIs each stream corresponds to a resource in the API. For example if the API
    contains the endpoints
        - GET v1/customers
        - GET v1/employees

    then you should have three classes:
    `class SalesmateStream(HttpStream, ABC)` which is the current class
    `class Customers(SalesmateStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(SalesmateStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalSalesmateStream((SalesmateStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    url_base = 'https://apis.salesmate.io/v3/'
    # url_base = "https://4a28bad45212.ngrok.io/"
    http_method = "POST"
    _current_page = 1

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        TODO: Override this method to define a pagination strategy. If you will not be using pagination, no action is required - just return None.

        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        For example, if the API accepts a 'page' parameter to determine which page of the result to return, and a response from the API contains a
        'page' number, then this method should probably return a dict {'page': response.json()['page'] + 1} to increment the page count by 1.
        The request_params method should then read the input next_page_token and set the 'page' param to next_page_token['page'].

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        if (self._current_page < response.json()['Data']["totalPages"]):
            self._current_page+=1
            return {'pageNo': self._current_page} 

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"rows": 1000}

        # Handle pagination by inserting the next page's token in the request parameters
        if next_page_token:
            params.update(next_page_token)

        return params


    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json.get("Data", []).get("data", [])  # Salesmate puts records in a container array "data"


class Companies(SalesmateStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "companies/search"
    
    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        return json.loads('{"fields":["annualRevenue","associatedContacts","billingAddressLine1","billingAddressLine2","billingCity","billingCountry","billingState","billingZipCode","checkboxCustomField1","closedActivities","company","createdAddress","createdAt","createdBy","createdLatitude","createdLongitude","currency","decimalCustomField1","deletedAt","deletedBy","description","emailOptOut","facebookHandle","googlePlusHandle","id","instagramHandle","intCustomField1","intCustomField2","isDeleted","lastCommunicationAt","lastCommunicationBy","lastCommunicationMode","lastModifiedAt","lastModifiedBy","lastNote","lastNoteAddedAt","lastNoteAddedBy","latitude","linkedInHandle","longitude","lostDealCount","multiSelectCustomField1","multiSelectCustomField2","name","numberOfEmployees","openActivities","openDealCount","otherPhone","owner","phone","shippingAddressLine1","shippingAddressLine2","shippingCity","shippingCountry","shippingState","shippingZipCode","skypeId","smsOptOut","tags","textCustomField1","textCustomField10","textCustomField2","textCustomField3","textCustomField4","textCustomField5","textCustomField6","textCustomField7","textCustomField8","textCustomField9","totalActivities","totalAmountOfLostDeal","totalAmountOfOpenDeal","totalAmountOfWonDeal","twitterHandle","type","website","wonDealCount"],"query":{}}')
    
class Activities(SalesmateStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "activities/search"
    
    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        return json.loads('{"fields":["associatedCallId","automationId","automationInstanceId","automationInstanceNodeId","calendarEventId","calendarId","completedAt","createdAddress","createdAt","createdBy","createdLatitude","createdLongitude","deletedAt","deletedBy","description","dueDate","duration","endDate","followers","id","isCalendarInvite","isCompleted","isCreatedFromSystem","isDeleted","lastModifiedAt","lastModifiedBy","lastNote","lastNoteAddedAt","lastNoteAddedBy","location","meetingSchedulerId","note","outcome","owner","primaryCompany","primaryContact","purpose","recordingUrl","recurrence","recurrenceId","relatedTo","relatedToModule","seriesMasterId","tags","title","type","videoURL","visibility"],"query":{}}')

class Contacts(SalesmateStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "contacts/search"
    
    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        return json.loads('{"fields":["billingAddressLine1","billingAddressLine2","billingCity","billingCountry","billingState","billingZipCode","browser","browserVersion","clicksOfLastEmailCount","closedActivities","company","countryCode","createdAddress","createdAt","createdBy","createdLatitude","createdLongitude","currentUrl","decimalCustomField1","deletedAt","deletedBy","description","designation","device","email","emailMessageCount","emailOptOut","emailOptOutReason","eventType","facebookHandle","firstName","googlePlusHandle","host","id","initialReferralDomain","initialReferralUrl","instagramHandle","ipAddress","isDeleted","lastCommunicationAt","lastCommunicationBy","lastCommunicationMode","lastEmailReceivedAt","lastEmailSentAt","lastModifiedAt","lastModifiedBy","lastName","lastNote","lastNoteAddedAt","lastNoteAddedBy","lastSendEmailId","latitude","library","libraryVersion","linkedInHandle","longitude","lostDealCount","mobile","name","openActivities","openDealCount","os","otherPhone","owner","pathName","phone","referralDomain","referralUrl","region","salesmateScore","screenHeight","screenWidth","searchEngine","shippingAddressLine1","shippingAddressLine2","shippingCity","shippingCountry","shippingState","shippingZipCode","skypeId","smsOptOut","tags","timezone","totalActivities","totalAmountOfLostDeal","totalAmountOfOpenDeal","totalAmountOfWonDeal","twitterHandle","type","userId","utmCampaign","utmContent","utmMedium","utmSource","utmTerm","viewsOfLastEmailCount","website","wonDealCount"],"query":{}}')

class Deals(SalesmateStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "deals/search"
    
    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        return json.loads('{"fields":["closedDate","closedPipeline","closedStage","createdAddress","createdAt","createdBy","createdLatitude","createdLongitude","currency","dealValue","deletedAt","deletedBy","description","estimatedCloseDate","followers","id","isDeleted","isWinProbabilityModifiedByUser","lastActivityAt","lastActivityBy","lastCommunicationAt","lastCommunicationBy","lastCommunicationMode","lastModifiedAt","lastModifiedBy","lastNote","lastNoteAddedAt","lastNoteAddedBy","lostReason","owner","pipeline","primaryCompany","primaryContact","priority","source","stage","status","tags","title","winProbability"],"query":{}}')

class Users(SalesmateStream):
    primary_key = "id"
    http_method = "GET"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "users"
    
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json.get("Data", [])  # Users endpoint does not have a nested "data" array
    
# # Basic incremental stream
# class IncrementalSalesmateStream(SalesmateStream, ABC):
#     """
#     TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
#          if you do not need to implement incremental sync for any streams, remove this class.
#     """

#     # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
#     state_checkpoint_interval = None

#     @property
#     def cursor_field(self) -> str:
#         """
#         TODO
#         Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
#         usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

#         :return str: The name of the cursor field.
#         """
#         return []

#     def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
#         """
#         Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
#         the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
#         """
#         return {}


# class Contacts(IncrementalSalesmateStream):
#     """
#     TODO: Change class name to match the table/data source this stream corresponds to.
#     """

#     # TODO: Fill in the cursor_field. Required.
#     cursor_field = "start_date"

#     # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
#     primary_key = "employee_id"

#     def path(self, **kwargs) -> str:
#         """
#         TODO: Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/employees then this should
#         return "single". Required.
#         """
#         return "employees"

#     def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
#         """
#         TODO: Optionally override this method to define this stream's slices. If slicing is not needed, delete this method.

#         Slices control when state is saved. Specifically, state is saved after a slice has been fully read.
#         This is useful if the API offers reads by groups or filters, and can be paired with the state object to make reads efficient. See the "concepts"
#         section of the docs for more information.

#         The function is called before reading any records in a stream. It returns an Iterable of dicts, each containing the
#         necessary data to craft a request for a slice. The stream state is usually referenced to determine what slices need to be created.
#         This means that data in a slice is usually closely related to a stream's cursor_field and stream_state.

#         An HTTP request is made for each returned slice. The same slice can be accessed in the path, request_params and request_header functions to help
#         craft that specific request.

#         For example, if https://example-api.com/v1/employees offers a date query params that returns data for that particular day, one way to implement
#         this would be to consult the stream state object for the last synced date, then return a slice containing each date from the last synced date
#         till now. The request_params function would then grab the date from the stream_slice and make it part of the request by injecting it into
#         the date query param.
#         """
#         raise NotImplementedError("Implement stream slices or delete this method!")


class SalesmateAuthenticator(HttpAuthenticator):
    def __init__(self, api_key: str, link_name: str):
        self._api_key = api_key
        self._link_name = link_name

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"sessionToken": self._api_key, "x-linkname": self._link_name}

# Source
class SourceSalesmate(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        TODO: Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        # TODO remove the authenticator if not required.
        auth = SalesmateAuthenticator(api_key=config["access_key"], link_name=config["link_name"])  
        return [Companies(authenticator=auth), Activities(authenticator=auth), Contacts(authenticator=auth), Deals(authenticator=auth), Users(authenticator=auth)]

    def _make_request(self, config):
        parsed_config = self._parse_config(config)
        http_method = parsed_config.get("http_method").lower()
        url = parsed_config.get("url")
        headers = parsed_config.get("headers", {})
        body = parsed_config.get("body", {})

        if http_method == "get":
            r = requests.get(url, headers=headers, json=body)
        elif http_method == "post":
            r = requests.post(url, headers=headers, json=body)
        else:
            raise Exception(f"Did not recognize http_method: {http_method}")
