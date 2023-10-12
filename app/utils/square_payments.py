from square.client import Client

def get_square_connection(access_token):
    square_client = Client(access_token, environment='sandbox')
    result = square_client.locations.list_locations()
    if result.is_success():
        square_location_id = result.body['locations'][0]['id']
        return square_client, square_location_id
    elif result.is_error():
        for error in result.errors:
            raise Exception(
                f"Error connecting to Square --> Category :{error['category']} Code: {error['code']} Detail: {error['detail']}")
