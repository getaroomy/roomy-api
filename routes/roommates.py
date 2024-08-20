import datetime
from flask import request, jsonify, Blueprint
from models.db import db
from models.wrappers import token_required
from google.cloud.firestore_v1.base_query import FieldFilter

roommates_bp = Blueprint('roommates_bp', __name__)

@roommates_bp.route('/get_roommates', methods=['GET'])
@token_required
def get_roommates():
    """
    Request Input:
    - uid: (string)
    - city: (optional, string)
    - gender: (optional, string)
    - roomWithGender: (optional, string)
    - doIHavePets: (optional, boolean)
    - fineWithHavingPets: (optional, boolean)
    - doISmoke: (optional, boolean)
    - fineWithSmokers: (optional, boolean)

    Return all available roommates in the users requested city, 15 at a time"""
    try:
        uid = request.args.get("uid")
        if not uid:
            return "UID not supplied", 400

        params = {
            'city': request.args.get("city"),
            'gender': request.args.get("gender"),
            'roomWithGender': request.args.get("roomWithGender"),
            'doIHavePets': request.args.get("doIHavePets", default=None, type=is_it_true),
            'fineWithHavingPets': request.args.get("fineWithHavingPets", default=None, type=is_it_true),
            'doISmoke': request.args.get("doISmoke", default=None, type=is_it_true),
            'fineWithSmokers': request.args.get("fineWithSmokers", default=None, type=is_it_true)
        }

        if any(value is None for value in params.values()):
            user_metadata = get_user_preference_metadata(uid, **{k: v is None for k, v in params.items()})
            params = {k: user_metadata.get(k, v) if v is None else v for k, v in params.items()}

        prefered_roommates_props = filter_roommates(params['gender'], params['roomWithGender'], 
                                                    params['doISmoke'], params['fineWithSmokers'], 
                                                    params['doIHavePets'], params['fineWithHavingPets'])

        query = (
            db.collection(u'profiles')
            .where(filter=FieldFilter(u'looking','==',True))
            .where(filter=FieldFilter(u'city','==',params['city']))
            .where(filter=FieldFilter(u'gender', 'in', prefered_roommates_props['gender']))
            .where(filter=FieldFilter(u'preferences.roomWithGender', 'in', prefered_roommates_props['preferences.roomWithGender']))
            .where(filter=FieldFilter(u'preferences.fineWithSmokers', '==', prefered_roommates_props['preferences.fineWithSmokers']))
            .where(filter=FieldFilter(u'preferences.doISmoke', 'in', prefered_roommates_props['preferences.doISmoke']))
            .where(filter=FieldFilter(u'preferences.fineWithHavingPets', '==', prefered_roommates_props['preferences.fineWithHavingPets']))
            .where(filter=FieldFilter(u'preferences.doIHavePets', 'in', prefered_roommates_props['preferences.doIHavePets']))
            .limit(15)
        )
        results = query.stream()
        roommates = [res.to_dict() for res in results]
        return jsonify({"roommates": roommates}), 200
    except Exception as e:
        return f"An error occurred: {e}", 500

def is_it_true(value):
    """
    Convert a string of a boolean to an actual boolean value.

    (Weird workaround b/c request args aren't accepting booleans properly)
    """
    if value == None:
        return None
    if value.lower() == 'true':
        return True
    return False

def filter_roommates(gender, roomWithGender, doISmoke, fineWithSmokers, doIHavePets, fineWithHavingPets):
    """
    Filter out people based on their preferences
    """
    try:
        roommatesGenderPreference = [gender, "any"]
        usersGenderPreference = ["male","female","nonbinary"] if roomWithGender == "any" else [roomWithGender]
        roommatesSmokerPreference = False if not doISmoke else True
        usersSmokerPreference = [False] if not fineWithSmokers else [True, False]
        roommatesPetsPreference = True if not doIHavePets else False
        usersPetPreference = [False] if not fineWithHavingPets else [True, False]
            
        preferedRoommatesProps = {
            "gender": usersGenderPreference,
            "preferences.roomWithGender": roommatesGenderPreference,
            "preferences.fineWithSmokers": roommatesSmokerPreference,
            "preferences.doISmoke": usersSmokerPreference,
            "preferences.fineWithHavingPets": roommatesPetsPreference,
            "preferences.doIHavePets": usersPetPreference
        }
        return preferedRoommatesProps
    except Exception as e:
        print("Error in filter_roommates:", e)
        return {
            "gender": None,
            "preferences.roomWithGender": None,
            "preferences.fineWithSmokers": None,
            "preferences.doISmoke": None,
            "preferences.fineWithHavingPets": None,
            "preferences.doIHavePets": None
        }

def get_user_preference_metadata(uid, city=False, gender=False, roomWithGender=False, doIHavePets=False, fineWithHavingPets=False, doISmoke=False, fineWithSmokers=False):
    """
    Only get user data that's not supplied through the URL
    """
    try:
        raw_profile = db.collection(u'profiles').document(uid).get()
        if raw_profile.exists:
            profile = raw_profile.to_dict()
            prefs = profile.get('preferences', {})
            preferences = {}
            if city: preferences['city'] = profile.get('city')
            if gender: preferences['gender'] = profile.get('gender')
            if roomWithGender: preferences['roomWithGender'] = prefs.get('roomWithGender')
            if doIHavePets: preferences['doIHavePets'] = prefs.get('doIHavePets')
            if fineWithHavingPets: preferences['fineWithHavingPets'] = prefs.get('fineWithHavingPets')
            if doISmoke: preferences['doISmoke'] = prefs.get('doISmoke')
            if fineWithSmokers: preferences['fineWithSmokers'] = prefs.get('fineWithSmokers')
            return preferences
        return {}
    except:
        return {}