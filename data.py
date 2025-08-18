commands = ["nosedive", "rules", "links", "codes", "helmet", "help", "pads", "rides"]
admin_commands = ["test_admin", "announce", "make_ride_poll"]

command_descriptions = {
    "nosedive": "Sends a link to a nosedive video",
    "rules": "Sends the rules of the group",
    "links": "Sends a list of useful links",
    "codes": "Sends a link to a list of discount codes",
    "helmet": "Sends a list of recommended helmet brands",
    "help": "Sends a list of commands",
    "pads": "Sends a list of recommended pads",
    "i2s": "Sends a message about Intro 2 Speed",
    "rides": "Sends a list of upcoming rides",
    "inline": "Sends information about collab rides with Inline Insomniacs",
    "econtact": "Sends a link to the emergency contact form"
}

admin_command_descriptions = {
    "test_admin": "Tests if the user is an admin",
    "announce": "Announces a message to the group and mirror it in the Discord",
    "make_ride_poll": "Makes a poll for the next ride (or a selected ride)",
    "send_topic_id": "Sends the topic ID of the current topic (for admin use only)",
}

emergency_contact_form_url = "https://forms.gle/ZooQHi9JM5Jj2Jba7" # ALSO UPDATE IN LINKS WHEN CHANGED

responses = { # Eventually, this will all be pulled from a database editable on the website. For now, it's hardcoded. Because I am lazy.
    "welcome": "Welcome to UIUC PEV! Do /rules to check the rules of the group, and /help to see other commands!",
    "rules_header": "The rules of this group are generally pretty simple. They are:",
    "rules": [
        "Wear a helmet",
        "WEAR A HELMET: They are required for any rides casual and above, along with any I2S events.",
        "Follow the rules of the road",
        "Keep a safe riding distance",
        "Stagger while riding",
        "Don't wear loose clothes that might get caught",
        "Be careful where you point your flashlight (@Dylan)",
        "Know your limits, and ride within them",
        "Communicate with your fellow riders",
        "Come prepared to rides (Charger, water, light, etc.)",
        "Keep some form of emergency contact on you (Or fill out our emergency contact form /econtact)",
        "Do not share crash videos of someone without their permission",
        "We have very little AI tolerance. Keep it to a minimum and relevant, otherwise skip it. This rule specifically will have very little leniency.",
        "Have fun!"
    ],
    "nosedive": "<a href='https://www.youtube.com/watch?v=kc6IEVV9mp0'>ayy lmao</a>", # stolen directly from ChiPEV
    "links": "All of our links can be found <a href='https://linktr.ee/UIUCPEV'>here</a>\n\nPlease also fill out our emergency contact form <a href='https://forms.gle/ZooQHi9JM5Jj2Jba7'>here</a>",
    "codes": "Discount codes are stolen from ChiPEV, and can be found <a href='https://docs.google.com/spreadsheets/d/1QTMuWO8k5719MeBt535rA_kPvSEVmiTI3wVA9Bcwu5g/edit?usp=sharing'>here</a>",
    "helmet": """<a href='https://www.youtube.com/watch?v=b9yL5usLFgY'>I LOVE HELMETS</a>\n
            Make sure you wear a good helmet!\n
            Some good brands:\n
            <a href='http://www.bernunlimited.com/'>Bern</a>\n
            <a href='https://www.zeitbike.com/collections/helmets/'>Zeitbike</a>\n
            <a href='https://www.explorethousand.com/'>Thousand</a>\n
            <a href='https://www.ruroc.com/en/'>Ruroc</a>
            """,
    "pads": "TSG, G-Form, Revzilla\n\n<a href='https://g-form.com/'>GForm</a>\n<a href='https://www.revzilla.com'>Revzilla</a>",
    "i2s": "Intro 2 Speed (I2S) is an event where new and experienced riders can practice together and learn new skills. It is a great way to meet other riders and learn how to ride safely. We try to hold I2S every week at lot E14 when weather permits, but it occasionally gets moved, so keep up to date using /rides!",
    "inline": "Inline Insomniacs (Inline) is another RSO on campus that we very occasionally collaborate with for rides. They ride non-electric skateboards/longboards/skates, so rides with them are a slower pace and it is important that we are respectful of this. Make sure to not ride too fast or aggressively, and be sure to communicate with other riders. PEV's historically haven't been allowed to ride with them, and we want to keep this privilege, so please be respectful and follow their rules and only join them when explicitly allowed to."
}

chat_id_map_dev = {
    "0": 1186544426835791874, # Telegram's "General" chat doesn't have a channel ID, it is just the group chat ID
    "3": 1186544831892312164
}

chat_id_map = { # This is really, REALLY stupid that I have it going both ways but oh well
    "0": 1402431046015778928,
    "2": 1402431131428589750,
    "4": 1402431181122965524,
    "6": 1402431078446268568,
    "4635": 1402431199493750924,
    "8": 1402431219320229970,
    "9": 1402431168099516487,
    "10": 1402431152744173578,
    "15631": 1402431104396431501,
    "3": 1402431253067726979
}

announcement_topic_dev = 1201
announcement_topic_prod = None