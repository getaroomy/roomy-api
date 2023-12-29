import datetime
from flask import request, jsonify, Blueprint
from models.db import db
from models.wrappers import token_required
from google.cloud.firestore_v1.base_query import FieldFilter

roommates_bp = Blueprint('roommates_bp', __name__)

@roommates_bp.route('/get_roommates', methods=['GET'])
@token_required
def get_roommates():
    """Return all available roommates in the users requested city, 15 at a time"""
    try:
        uid, city, gender, roomWithGender, doIHavePets, fineWithHavingPets, doISmoke, fineWithSmokers = None, None, None, None, None, None, None, None
        uid = request.args.get("uid")
        if not uid:
            raise NameError("UID not supplied")
        city = request.args.get("city")
        gender = request.args.get("gender")
        roomWithGender = request.args.get("roomWithGender")
        doIHavePets = request.args.get("doIHavePets", default=None, type=is_it_true)
        fineWithHavingPets = request.args.get("fineWithHavingPets", default=None, type=is_it_true)
        doISmoke = request.args.get("doISmoke", default=None, type=is_it_true)
        fineWithSmokers = request.args.get("fineWithSmokers", default=None, type=is_it_true)
        if (city == None or gender == None or roomWithGender == None or doIHavePets == None or
            fineWithHavingPets == None or doISmoke == None or fineWithSmokers == None):
            userPreferenceMetadata = get_user_preference_metadata(uid, city == None, gender == None, roomWithGender == None, doIHavePets == None, fineWithHavingPets == None, doISmoke == None, fineWithSmokers == None)
            if userPreferenceMetadata:
                if city == None: city = userPreferenceMetadata.get("city")
                if gender == None: gender = userPreferenceMetadata.get("gender")
                if roomWithGender == None: roomWithGender = userPreferenceMetadata.get("roomWithGender")
                if doIHavePets == None: doIHavePets = userPreferenceMetadata.get("doIHavePets")
                if fineWithHavingPets == None: fineWithHavingPets = userPreferenceMetadata.get("fineWithHavingPets")
                if doISmoke == None: doISmoke = userPreferenceMetadata.get("doISmoke")
                if fineWithSmokers == None: fineWithSmokers = userPreferenceMetadata.get("fineWithSmokers")
        preferedRoommatesProps = filter_roommates(gender, roomWithGender, doISmoke, fineWithSmokers, doIHavePets, fineWithHavingPets)

        query = (
            db.collection(u'profiles')
            .where(filter=FieldFilter(u'looking','==',True))
            .where(filter=FieldFilter(u'city','==',city))
            .where(filter=FieldFilter(u'gender', 'in', preferedRoommatesProps.get('gender')))
            .where(filter=FieldFilter(u'preferences.roomWithGender', 'in', preferedRoommatesProps.get('preferences.roomWithGender')))
            .where(filter=FieldFilter(u'preferences.fineWithSmokers', '==', preferedRoommatesProps.get('preferences.fineWithSmokers')))
            .where(filter=FieldFilter(u'preferences.doISmoke', 'in', preferedRoommatesProps.get('preferences.doISmoke')))
            .where(filter=FieldFilter(u'preferences.fineWithHavingPets', '==', preferedRoommatesProps.get('preferences.fineWithHavingPets')))
            .where(filter=FieldFilter(u'preferences.doIHavePets', 'in', preferedRoommatesProps.get('preferences.doIHavePets')))
            .limit(15)
        )
        results = query.stream()
        roommates = []
        for res in results:
            curr_roomy = res.to_dict()
            roommates.append(curr_roomy)
        return jsonify({"roommates": roommates}), 200
    except Exception as e:
        return f"An error occured: {e}", 500

def is_it_true(value):
    if value == None:
        return None
    if value.lower() == 'true':
        return True
    return False

def filter_roommates(gender: str, roomWithGender: str, doISmoke: bool, fineWithSmokers: bool, doIHavePets: bool, fineWithHavingPets: bool) -> dict:
    """
    Filter out people based on their preferences
    """
    try:
        roommatesGenderPreference = [gender, "any"]
        usersGenderPreference = []
        roommatesSmokerPreference = True
        usersSmokerPreference = [True, False]
        roommatesPetsPreference = False
        usersPetPreference = [True, False]

        # Gender
        if roomWithGender == "any":
            usersGenderPreference = ["male","female","nonbinary"]
        else:
            usersGenderPreference = [roomWithGender]

        # Smoking
        if not doISmoke:
            roommatesSmokerPreference = False
        if not fineWithSmokers:
            usersSmokerPreference = [False]

        # Pets
        if not doIHavePets:
            roommatesPetsPreference = True
        if not fineWithHavingPets:
            usersPetPreference = [False]
            
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
        preferedRoommatesProps = {
            "gender": None,
            "preferences.roomWithGender": None,
            "preferences.fineWithSmokers": None,
            "preferences.doISmoke": None,
            "preferences.fineWithHavingPets": None,
            "preferences.doIHavePets": None
        }
        return preferedRoommatesProps

def get_user_preference_metadata(uid: str, city: bool, gender: bool, roomWithGender: bool, doIHavePets: bool, fineWithHavingPets: bool, doISmoke: bool, fineWithSmokers: bool):
    """
    Only get user data that's not supplied through the URL
    """
    try:
        raw_profile = db.collection(u'profiles').document(uid).get()
        if raw_profile.exists:
            profile = raw_profile.to_dict()
            prefs = profile.get('preferences')
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