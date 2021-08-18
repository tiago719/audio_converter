from database import database, gridfs


def convert(email):
    email_audio = database.db.audios.find_one({'email': email})
    if email_audio:
        # Get original audio
        original_reference = email_audio.get('original', '')
        if original_reference:
            # Get original audio from gridfs
            original_audio = gridfs.get(original_reference)
            # TODO: Convert audio
            # Use some librabry or API
            # I'm sure there is some kind of magic doing this already
            converted_audio = original_audio
            # Write converted audio to gridfs
            converted_reference = gridfs.put(converted_audio)
            # Add converted reference to database
            database.db.audios.update_one({'email': email}, {'$set': {'converted': converted_reference}})
            # Return job successful
            return True
    return False