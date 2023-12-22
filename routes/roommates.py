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
        doIHavePets = request.args.get("doIHavePets", default=False, type=is_it_true)
        fineWithHavingPets = request.args.get("fineWithHavingPets", default=False, type=is_it_true)
        doISmoke = request.args.get("doISmoke", default=False, type=is_it_true)
        fineWithSmokers = request.args.get("fineWithSmokers", default=False, type=is_it_true)
        if (city == None or
            gender == None or
            roomWithGender == None or
            doIHavePets == None or
            fineWithHavingPets == None or
            doISmoke == None or
            fineWithSmokers == None):
            userPreferenceMetadata = get_user_preference_metadata(uid)
            if userPreferenceMetadata:
                city = userPreferenceMetadata.get("city")
                gender = userPreferenceMetadata.get("gender")
                roomWithGender = userPreferenceMetadata.get("roomWithGender")
                doIHavePets = userPreferenceMetadata.get("doIHavePets")
                fineWithHavingPets = userPreferenceMetadata.get("fineWithHavingPets")
                doISmoke = userPreferenceMetadata.get("doISmoke")
                fineWithSmokers = userPreferenceMetadata.get("fineWithSmokers")
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
    return value.lower() == 'true'

def filter_roommates(gender: str, roomWithGender: str, doISmoke: bool, fineWithSmokers: bool, doIHavePets: bool, fineWithHavingPets: bool) -> dict[str, any]:
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

def get_user_preference_metadata(uid: str):
    print("get_user_preference_metadata")
    try:
        raw_profile = db.collection(u'profiles').document(uid).get()
        if raw_profile.exists:
            profile = raw_profile.to_dict()
            prefs = profile.get('preferences')
            preferences = {
                'city': profile.get('city'),
                'gender': profile.get('gender'),
                'roomWithGender':prefs.get('roomWithGender'),
                'doIHavePets':prefs.get('doIHavePets'),
                'fineWithHavingPets':prefs.get('fineWithHavingPets'),
                'doISmoke':prefs.get('doISmoke'),
                'fineWithSmokers':prefs.get('fineWithSmokers'),
            }
            return preferences
        return {}
    except:
        return {}