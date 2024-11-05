commands = ["nosedive", "rules", "links", "codes", "helmet", "help", "pads", "rides"]
admin_commands = ["test_admin", "announce", "add_ride"]

command_descriptions = {
    "nosedive": "Sends a link to a nosedive video",
    "rules": "Sends the rules of the group",
    "links": "Sends a list of useful links",
    "codes": "Sends a link to a list of discount codes",
    "helmet": "Sends a list of recommended helmet brands",
    "help": "Sends a list of commands",
    "pads": "Sends a list of recommended pads",
    "i2s": "Sends a message about Intro 2 Speed",
    "rides": "Sends a list of upcoming rides"
}

admin_command_descriptions = {
    "test_admin": "Tests if the user is an admin",
    "announce": "Announces a message to the group and mirror it in the Discord",
    "add_ride": "Adds a ride to the list of rides"
}

responses = { # Eventually, this will all be pulled from a database editable on the website. For now, it's hardcoded. Because I am lazy.
    "welcome": "Welcome to UIUC PEV! Do /rules to check the rules of the group, and /help to see other commands!",
    "rules_header": "The rules of this group are generally pretty simple. They are:",
    "rules": [
        "Wear a helmet",
        "WEAR A HELMET",
        "Follow the rules of the road",
        "Keep a safe riding distance",
        "Stagger while riding",
        "Don't wear loose clothes that might get caught",
        "Be careful where you point your flashlight",
        "Know your limits, and ride within them",
        "Communicate with your fellow riders",
        "Have fun!"
    ],
    "nosedive": "<a href='https://www.youtube.com/watch?v=kc6IEVV9mp0'>ayy lmao</a>", # stolen directly from ChiPEV
    "links": "All of our links can be found <a href='https://linktr.ee/UIUCPEV'>here</a>",
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
    "i2s": "Intro 2 Speed (I2S) is an event where new and experienced riders can practice together and learn new skills. It is a great way to meet other riders and learn how to ride safely. We try to hold I2S every week at lot E14 when weather permits, but it occasionally gets moved, so keep up to date using /rides!"
}