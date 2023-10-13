from enum import Enum


# Responsible for mapping avaliable types in database to read-able names.
class GreetingType(str, Enum):
    Birthday_Boyfriend = "birthday_boyfriend_message"
    Birthday_Girlfriend = "birthday_girlfriend_message"
    Birthday_Love = "birthday_love_message"
    Birthday_Wife = "birthday_wife_message"
    Birthday_Bestfriend = "birthday-bestfriend-messages"
    Birthday_Brother = "birthday-to-brother-messages"
    Birthday_Dad = "birthday-to-dad-messages"
    Birthday_Mom = "birthday-to-mom-messages"
    Birthday_Sister = "birthday-to-sister-messages"
    Christmas_Boyfriend = "christmas-message-to-boyfriend"
    Christmas_Girlfriend = "christmas-message-to-girlfriend"
    Christmas_General = "christmas-messages"
    Morning_Romantic = "morning-romantic"
