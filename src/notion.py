import json

import requests


class NotionAPI:

    def __init__(self, token: str) -> None:
        self.token = token

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def get_db_rows(self, db_id: str):

        url = f"https://api.notion.com/v1/databases/{db_id}/query"

        page_size = 100
        start_cursor = None
        has_more = True
        results = []

        while has_more:

            params = {"page_size": page_size}
            if start_cursor:
                params["start_cursor"] = start_cursor

            response = requests.post(url, json.dumps(params), headers=self.headers)
            response_json = response.json()

            has_more = response_json["has_more"]
            start_cursor = response_json["next_cursor"]
            results.extend(response_json["results"])

        return results
