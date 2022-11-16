import argparse, sys

from core.features.dialpad import utils

parser=argparse.ArgumentParser()

parser.add_argument("--dialpad-user-id", help="Dialpad user id.")
parser.add_argument("--dialpad-api-key", help="Dialpad Public API Key.")

args=parser.parse_args()
print(utils.get_mock_idtoken(user_id=args.dialpad_user_id, api_key=args.dialpad_api_key))
