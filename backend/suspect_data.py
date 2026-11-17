"""
Curated suspect case associations and simple evidence movement traces.
Provides instant, clear evidence verification for TraceHunt investigation.
"""

SUSPECT_TRACES = {
    # ------------------------------------------------------------------------
    # INC001: Armed Robbery at Ratna Diamond Jewellers (Manek Chowk)
    # ------------------------------------------------------------------------
    "P000501": {
        "case_id": "INC001",
        "case_name": "ROBBERY at Ratna Diamond Jewellers (Manek Chowk)",
        "role": "Main Suspect",
        "score": 95,
        "is_planted": True,
        "accomplice_id": "P000502",
        "accomplice_name": "Farhana Chawla",
        "summary": "Visited the shop 3 times before to spy on it. Entered 5 minutes before the robbery with partner Farhana Chawla (P000502), and quickly escaped 5.5 km away in 17 minutes.",
        "journey": [
            {
                "event_id": "EVT01802101",
                "timestamp": "2026-08-10 08:30:15",
                "place": "Isanpur Residential Area (Isanpur)",
                "source": "WIFI",
                "evidence_tag": "DAILY_LIFE",
                "evidence_note": "Morning at home"
            },
            {
                "event_id": "EVT01824050",
                "timestamp": "2026-08-10 14:00:00",
                "place": "Ratna Diamond Jewellers (Manek Chowk)",
                "source": "CCTV",
                "evidence_tag": "SPYING_1",
                "evidence_note": "First Spying Visit: Visited the shop 2 days before the robbery with partner Farhana"
            },
            {
                "event_id": "EVT01859012",
                "timestamp": "2026-08-10 18:45:20",
                "place": "Isanpur Market (Isanpur)",
                "source": "CELL",
                "evidence_tag": "DAILY_LIFE",
                "evidence_note": "Back home in Isanpur"
            },
            {
                "event_id": "EVT01948130",
                "timestamp": "2026-08-11 15:45:00",
                "place": "Ratna Diamond Jewellers (Manek Chowk)",
                "source": "CCTV",
                "evidence_tag": "SPYING_2",
                "evidence_note": "Second Spying Visit: Visited 1 day before to check when workers change shift"
            },
            {
                "event_id": "EVT02081015",
                "timestamp": "2026-08-12 07:30:00",
                "place": "Ratna Diamond Jewellers (Manek Chowk)",
                "source": "CCTV",
                "evidence_tag": "SPYING_3",
                "evidence_note": "Third Spying Visit: Visited on morning of robbery to check guards opening the shop"
            },
            {
                "event_id": "EVT02093840",
                "timestamp": "2026-08-12 14:10:00",
                "place": "Ratna Diamond Jewellers (Manek Chowk)",
                "source": "CCTV",
                "evidence_tag": "CRIME_SCENE",
                "evidence_note": "CRIME SCENE: Posed as diamond buyer, asking salesman for heavy trays while Farhana grabbed the gold"
            },
            {
                "event_id": "EVT02093842",
                "timestamp": "2026-08-12 14:27:00",
                "place": "Vastrapur Road (LOC0151)",
                "source": "CELL",
                "evidence_tag": "QUICK_ESCAPE",
                "evidence_note": "QUICK ESCAPE: Swapped scooter for stolen black motorbike at market corner, fleeing through pedestrian lanes"
            },
            {
                "event_id": "EVT02102910",
                "timestamp": "2026-08-12 19:40:12",
                "place": "Isanpur Residential Area (Isanpur)",
                "source": "CELL",
                "evidence_tag": "DAILY_LIFE",
                "evidence_note": "Back at home"
            }
        ]
    },
    "P000502": {
        "case_id": "INC001",
        "case_name": "ROBBERY at Ratna Diamond Jewellers (Manek Chowk)",
        "role": "Partner / Accomplice",
        "score": 95,
        "is_planted": False,
        "accomplice_id": "P000501",
        "accomplice_name": "Anand Pandya",
        "summary": "Accompanied Anand Pandya on all 3 spying visits. Entered the shop with him at 2:10 PM and escaped together on bike.",
        "journey": [
            {
                "event_id": "EVT01802102",
                "timestamp": "2026-08-10 09:10:00",
                "place": "Bodakdev Square (Bodakdev)",
                "source": "CELL",
                "evidence_tag": "DAILY_LIFE",
                "evidence_note": "Morning in Bodakdev"
            },
            {
                "event_id": "EVT01824051",
                "timestamp": "2026-08-10 14:00:00",
                "place": "Ratna Diamond Jewellers (Manek Chowk)",
                "source": "CCTV",
                "evidence_tag": "SPYING_1",
                "evidence_note": "First Spying Visit: At the jewellery shop with Anand Pandya (P000501)"
            },
            {
                "event_id": "EVT01948131",
                "timestamp": "2026-08-11 15:45:00",
                "place": "Ratna Diamond Jewellers (Manek Chowk)",
                "source": "CCTV",
                "evidence_tag": "SPYING_2",
                "evidence_note": "Second Spying Visit: At the shop again with Anand Pandya"
            },
            {
                "event_id": "EVT02081016",
                "timestamp": "2026-08-12 07:30:00",
                "place": "Ratna Diamond Jewellers (Manek Chowk)",
                "source": "CCTV",
                "evidence_tag": "SPYING_3",
                "evidence_note": "Third Spying Visit: Morning spying visit with Anand Pandya"
            },
            {
                "event_id": "EVT02093841",
                "timestamp": "2026-08-12 14:10:00",
                "place": "Ratna Diamond Jewellers (Manek Chowk)",
                "source": "CCTV",
                "evidence_tag": "CRIME_SCENE",
                "evidence_note": "CRIME SCENE: Entered the jewellery shop with Anand 5 minutes before the robbery"
            },
            {
                "event_id": "EVT02093843",
                "timestamp": "2026-08-12 14:27:00",
                "place": "Vastrapur Road (LOC0151)",
                "source": "CELL",
                "evidence_tag": "QUICK_ESCAPE",
                "evidence_note": "QUICK ESCAPE: Escaped together with Anand along the same road"
            }
        ]
    },

    # ------------------------------------------------------------------------
    # INC004: Robbery at Maninagar Express ATM
    # ------------------------------------------------------------------------
    "P000531": {
        "case_id": "INC004",
        "case_name": "ROBBERY at Maninagar Express ATM (Maninagar)",
        "role": "Main Suspect",
        "score": 110,
        "is_planted": True,
        "accomplice_id": "P000532",
        "accomplice_name": "Mansi Chhajed",
        "summary": "Visited the ATM 3 times late at night to spy on it. Entered 5 minutes before the robbery with partner Mansi, cut open the ATM, escaped fast 5.5 km to Sola, and kept his phone off for almost 4 hours.",
        "journey": [
            {
                "event_id": "EVT04710120",
                "timestamp": "2026-09-01 08:30:15",
                "place": "Naroda Residential Area (Naroda)",
                "source": "WIFI",
                "evidence_tag": "DAILY_LIFE",
                "evidence_note": "Morning at home"
            },
            {
                "event_id": "EVT04802620",
                "timestamp": "2026-09-02 03:00:00",
                "place": "Maninagar Express ATM (Maninagar)",
                "source": "CCTV",
                "evidence_tag": "SPYING_1",
                "evidence_note": "First Spying Visit: Came at 3:00 AM (2 days before robbery) with partner Mansi"
            },
            {
                "event_id": "EVT04825100",
                "timestamp": "2026-09-02 11:15:30",
                "place": "Nikol Office Area (Nikol)",
                "source": "CELL",
                "evidence_tag": "DAILY_LIFE",
                "evidence_note": "Normal office work"
            },
            {
                "event_id": "EVT04948137",
                "timestamp": "2026-09-03 04:45:00",
                "place": "Maninagar Express ATM (Maninagar)",
                "source": "CCTV",
                "evidence_tag": "SPYING_2",
                "evidence_note": "Second Spying Visit: Came at 4:45 AM (1 day before robbery) to check cameras"
            },
            {
                "event_id": "EVT04948139",
                "timestamp": "2026-09-03 20:30:00",
                "place": "Maninagar Express ATM (Maninagar)",
                "source": "CCTV",
                "evidence_tag": "SPYING_3",
                "evidence_note": "Third Spying Visit: Came in evening (7 hours before robbery) to check guard shift"
            },
            {
                "event_id": "EVT05093846",
                "timestamp": "2026-09-04 03:10:00",
                "place": "Maninagar Express ATM (Maninagar)",
                "source": "CCTV",
                "evidence_tag": "CRIME_SCENE",
                "evidence_note": "CRIME SCENE: ATM thermal sensor logged 60°C heat spike from gas cutter; camera sprayed with black paint"
            },
            {
                "event_id": "EVT05093848",
                "timestamp": "2026-09-04 03:27:00",
                "place": "Sola Flyover (LOC0083)",
                "source": "CELL",
                "evidence_tag": "QUICK_ESCAPE",
                "evidence_note": "QUICK ESCAPE: Sped 5.5 km away to Sola in just 17 minutes right after the robbery"
            },
            {
                "event_id": "EVT05094200",
                "timestamp": "2026-09-04 03:28:00 to 07:11:00",
                "place": "Phone Switched Off (No Signal)",
                "source": "SENSOR",
                "evidence_tag": "PHONE_OFF",
                "evidence_note": "PHONE OFF: Switched off phone for 4 hours while hiding inside empty warehouse in Naroda"
            },
            {
                "event_id": "EVT04953972",
                "timestamp": "2026-09-04 07:11:53",
                "place": "Naroda Residential Area (Naroda)",
                "source": "WIFI",
                "evidence_tag": "PHONE_ON",
                "evidence_note": "Phone Turned Back On: Signal reappeared at home after 4 hours"
            }
        ]
    },
    "P000532": {
        "case_id": "INC004",
        "case_name": "ROBBERY at Maninagar Express ATM (Maninagar)",
        "role": "Partner / Lookout",
        "score": 110,
        "is_planted": False,
        "accomplice_id": "P000531",
        "accomplice_name": "Rohan Dholakia",
        "summary": "Partner in the ATM robbery. Came on all 3 spying visits with Rohan Dholakia (P000531), entered the ATM with him at 3:10 AM, and escaped together.",
        "journey": [
            {
                "event_id": "EVT04710125",
                "timestamp": "2026-09-01 10:20:00",
                "place": "Law Garden Campus (Law Garden)",
                "source": "WIFI",
                "evidence_tag": "DAILY_LIFE",
                "evidence_note": "College hours in morning"
            },
            {
                "event_id": "EVT04802621",
                "timestamp": "2026-09-02 03:00:00",
                "place": "Maninagar Express ATM (Maninagar)",
                "source": "CCTV",
                "evidence_tag": "SPYING_1",
                "evidence_note": "First Spying Visit: At the ATM with Rohan Dholakia at 3:00 AM"
            },
            {
                "event_id": "EVT04948138",
                "timestamp": "2026-09-03 04:45:00",
                "place": "Maninagar Express ATM (Maninagar)",
                "source": "CCTV",
                "evidence_tag": "SPYING_2",
                "evidence_note": "Second Spying Visit: At the ATM with Rohan Dholakia at 4:45 AM"
            },
            {
                "event_id": "EVT04948140",
                "timestamp": "2026-09-03 20:30:00",
                "place": "Maninagar Express ATM (Maninagar)",
                "source": "CCTV",
                "evidence_tag": "SPYING_3",
                "evidence_note": "Third Spying Visit: At the ATM with Rohan Dholakia in the evening"
            },
            {
                "event_id": "EVT05093847",
                "timestamp": "2026-09-04 03:10:00",
                "place": "Maninagar Express ATM (Maninagar)",
                "source": "CCTV",
                "evidence_tag": "CRIME_SCENE",
                "evidence_note": "CRIME SCENE: Inside ATM booth with Rohan 5 minutes before the alarm"
            },
            {
                "event_id": "EVT05093849",
                "timestamp": "2026-09-04 03:27:00",
                "place": "Sola Flyover (LOC0083)",
                "source": "CELL",
                "evidence_tag": "QUICK_ESCAPE",
                "evidence_note": "QUICK ESCAPE: Escaped together with Rohan along highway"
            }
        ]
    },

    # ------------------------------------------------------------------------
    # INC006: Murder at Sabarmati Riverfront Promenade North
    # ------------------------------------------------------------------------
    "P000102": {
        "case_id": "INC006",
        "case_name": "MURDER at Sabarmati Riverfront Promenade North",
        "role": "Main Suspect",
        "score": 50,
        "is_planted": True,
        "accomplice_id": None,
        "accomplice_name": None,
        "summary": "Met victim Rupal Vora 3 times in the last 2 weeks. Caught on camera talking to Rupal 13 minutes before she died, then quickly boarded a bus to leave.",
        "journey": [
            {
                "event_id": "EVT01102001",
                "timestamp": "2026-08-04 18:30:00",
                "place": "Riverfront Garden (Sabarmati)",
                "source": "CCTV",
                "evidence_tag": "MET_VICTIM_1",
                "evidence_note": "First Meeting: Met with victim Rupal Vora (P000101)"
            },
            {
                "event_id": "EVT01340150",
                "timestamp": "2026-08-09 19:15:00",
                "place": "Sabarmati Market (Sabarmati)",
                "source": "CCTV",
                "evidence_tag": "MET_VICTIM_2",
                "evidence_note": "Second Meeting: Met with victim Rupal Vora"
            },
            {
                "event_id": "EVT01520110",
                "timestamp": "2026-08-13 20:00:00",
                "place": "Sabarmati Riverfront Promenade (Riverfront)",
                "source": "CCTV",
                "evidence_tag": "MET_VICTIM_3",
                "evidence_note": "Third Meeting: Arguing with victim on the walkway"
            },
            {
                "event_id": "EVT01720810",
                "timestamp": "2026-08-16 21:17:00",
                "place": "Sabarmati Riverfront Promenade North (Riverfront)",
                "source": "CCTV",
                "evidence_tag": "CRIME_SCENE",
                "evidence_note": "CRIME SCENE: Caught on camera with victim 13 minutes before she was found dead"
            },
            {
                "event_id": "EVT01720815",
                "timestamp": "2026-08-16 21:28:31",
                "place": "Sabarmati Bus Station (LOC0031)",
                "source": "TRANSIT",
                "evidence_tag": "QUICK_ESCAPE",
                "evidence_note": "QUICK ESCAPE: Jumped onto a bus 11 minutes later to flee the area"
            }
        ]
    },

    # ------------------------------------------------------------------------
    # INC008: Murder at Kankaria West Quiet Gate
    # ------------------------------------------------------------------------
    "P000302": {
        "case_id": "INC008",
        "case_name": "MURDER at Kankaria West Quiet Gate (Kankaria)",
        "role": "Main Suspect",
        "score": 45,
        "is_planted": True,
        "accomplice_id": None,
        "accomplice_name": None,
        "summary": "Came late at night all the way from Thaltej (11 km away). Caught on camera at the quiet lake gate 13 mins before murder, fled towards Danilimda, and has no alibi.",
        "journey": [
            {
                "event_id": "EVT04610200",
                "timestamp": "2026-09-02 09:15:00",
                "place": "Thaltej Office Complex (Thaltej)",
                "source": "WIFI",
                "evidence_tag": "DAILY_LIFE",
                "evidence_note": "Daytime office hours in Thaltej"
            },
            {
                "event_id": "EVT04702110",
                "timestamp": "2026-09-02 22:47:00",
                "place": "Kankaria West Quiet Gate (Kankaria)",
                "source": "CCTV",
                "evidence_tag": "CRIME_SCENE",
                "evidence_note": "CRIME SCENE: Camera caught her at secluded gate 13 mins before murder"
            },
            {
                "event_id": "EVT04702125",
                "timestamp": "2026-09-02 23:35:00",
                "place": "Danilimda Crossroad (LOC0041)",
                "source": "CELL",
                "evidence_tag": "QUICK_ESCAPE",
                "evidence_note": "QUICK ESCAPE: Fled lake area towards Danilimda"
            }
        ]
    },
    "P000303": {
        "case_id": "INC008",
        "case_name": "MURDER at Kankaria West Quiet Gate (Kankaria)",
        "role": "Proven Innocent (Alibi Checked)",
        "score": -10,
        "is_planted": False,
        "accomplice_id": None,
        "accomplice_name": None,
        "summary": "Proven completely innocent. ATM camera in Sarkhej (12 km away) shows her taking out money at 10:50 PM during the murder, so she could not have been at Kankaria Lake.",
        "journey": [
            {
                "event_id": "EVT04610205",
                "timestamp": "2026-09-02 18:20:00",
                "place": "Sarkhej Residential Area (Sarkhej)",
                "source": "CELL",
                "evidence_tag": "DAILY_LIFE",
                "evidence_note": "Evening at home in Sarkhej"
            },
            {
                "event_id": "EVT04702115",
                "timestamp": "2026-09-02 22:50:00",
                "place": "Sarkhej Express ATM (Sarkhej)",
                "source": "CCTV",
                "evidence_tag": "PROVEN_INNOCENT",
                "evidence_note": "PROVEN INNOCENT: Taking out cash at ATM in Sarkhej (12 km away from crime scene). Completely cleared (Score: -10)."
            }
        ]
    }
}
