# app/seed_data.py
"""
Database seeder for EventPro AI.
Creates a comprehensive set of demo data on first application start.
"""

from __future__ import annotations
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

def seed_database(db) -> None:
    from app.models import User, Event, Guest, Task, Vendor, Feedback, BudgetItem
    
    # Guard: only seed if the DB is empty
    if User.query.first() is not None:
        return

    print("Seeding database with demo data...")

    # 1. Demo User
    demo_user = User(
        username="demo",
        email="demo@eventpro.ai"
    )
    demo_user.set_password("demo123")
    db.session.add(demo_user)
    db.session.flush()

    now = datetime.utcnow()
    today_date = now.date()

    # 2. Events (10 events)
    events_data = [
        {
            "name": "Raj & Meera's Wedding",
            "event_type": "Wedding",
            "date": today_date + timedelta(days=45),
            "venue": "The Grand Palace, Jaipur",
            "description": "A grand celebration of love uniting two beautiful souls. Three-day festivities including Mehendi, Sangeet, and the main ceremony.",
            "budget": 1500000.0,
            "guest_count": 250,
            "status": "Upcoming",
            "user_id": demo_user.id
        },
        {
            "name": "Sarah's Sweet 16 Bash",
            "event_type": "Birthday",
            "date": today_date + timedelta(days=12),
            "venue": "Skyline Rooftop Lounge, Mumbai",
            "description": "An elegant teenage birthday celebration overlooking the city lights. Neon theme with private DJ and custom cake.",
            "budget": 150000.0,
            "guest_count": 50,
            "status": "Upcoming",
            "user_id": demo_user.id
        },
        {
            "name": "National Youth Tech Summit",
            "event_type": "College Event",
            "date": today_date + timedelta(days=60),
            "venue": "University Auditorium, Bengaluru",
            "description": "Annual tech confluence hosting hackathons, developer talks, and innovation showcases for students across the nation.",
            "budget": 350000.0,
            "guest_count": 400,
            "status": "Upcoming",
            "user_id": demo_user.id
        },
        {
            "name": "Global Investors Conference",
            "event_type": "Corporate",
            "date": today_date - timedelta(days=2),
            "venue": "Convention Centre, New Delhi",
            "description": "High-profile investment summit bringing international venture capital firms and pioneering founders under one roof.",
            "budget": 800000.0,
            "guest_count": 150,
            "status": "Completed",
            "user_id": demo_user.id
        },
        {
            "name": "Karan & Divya's Sangeet Night",
            "event_type": "Wedding",
            "date": today_date + timedelta(days=44),
            "venue": "Zenana Mahal, Udaipur",
            "description": "A vibrant evening filled with traditional music, energetic dance performances, and exquisite Rajasthani cuisine.",
            "budget": 500000.0,
            "guest_count": 180,
            "status": "Upcoming",
            "user_id": demo_user.id
        },
        {
            "name": "AI Synergy Developers Hackathon",
            "event_type": "College Event",
            "date": today_date + timedelta(days=10),
            "venue": "Innovators Hub, Bengaluru",
            "description": "24-hour non-stop developers hackathon focused on AI products, speech assistants, and large language models.",
            "budget": 250000.0,
            "guest_count": 150,
            "status": "Upcoming",
            "user_id": demo_user.id
        },
        {
            "name": "Corporate Strategy Offsite",
            "event_type": "Corporate",
            "date": today_date + timedelta(days=20),
            "venue": "Grand Hyatt, Goa",
            "description": "Annual executive planning retreat, alignment workshops, and dinner.",
            "budget": 600000.0,
            "guest_count": 60,
            "status": "Upcoming",
            "user_id": demo_user.id
        },
        {
            "name": "Arjun's Graduation Party",
            "event_type": "Party",
            "date": today_date + timedelta(days=5),
            "venue": "Hard Rock Cafe, Bengaluru",
            "description": "Celebration party for engineering graduates with music and dinner.",
            "budget": 100000.0,
            "guest_count": 40,
            "status": "Upcoming",
            "user_id": demo_user.id
        },
        {
            "name": "Meera's Baby Shower",
            "event_type": "Party",
            "date": today_date + timedelta(days=15),
            "venue": "Sheraton Grand, Pune",
            "description": "Baby shower celebration with high tea, games, and floral decorations.",
            "budget": 180000.0,
            "guest_count": 50,
            "status": "Upcoming",
            "user_id": demo_user.id
        },
        {
            "name": "Anjali & Rohan Engagement",
            "event_type": "Wedding",
            "date": today_date + timedelta(days=30),
            "venue": "Umaid Bhawan Palace, Jodhpur",
            "description": "Traditional royal engagement ceremony with family banquet and musical performance.",
            "budget": 800000.0,
            "guest_count": 100,
            "status": "Upcoming",
            "user_id": demo_user.id
        }
    ]

    events = []
    for data in events_data:
        ev = Event(**data)
        db.session.add(ev)
        events.append(ev)

    db.session.flush()

    # 3. Guests (100 guests per event -> 1000 guests total)
    import random
    first_names = ["Arjun", "Rohan", "Rahul", "Priya", "Sneha", "Karan", "Neha", "Aditya", "Ishita", "Tanvi", "Siddharth", "Pooja", "Vikram", "Anita", "Deepika", "Kavya", "Amit", "Suresh", "Meera", "Abhay", "Rajesh", "Sunita", "Anjali", "Vivek", "Lakshmi", "Divya", "Prasad", "Harish", "Kunal", "Ritesh"]
    last_names = ["Sharma", "Singh", "Patel", "Reddy", "Mehta", "Iyer", "Banerjee", "Tiwari", "Saxena", "Dhawan", "Rao", "Kumar", "Verma", "Pandey", "Gowda", "Mishra", "Sinha", "Chauhan", "Pillai", "Pratap"]
    
    rsvp_statuses = ["Confirmed", "Confirmed", "Confirmed", "Pending", "Declined"]

    for idx, ev in enumerate(events):
        for g_idx in range(100):
            fn = random.choice(first_names)
            ln = random.choice(last_names)
            name = f"{fn} {ln}"
            email = f"{fn.lower()}.{ln.lower()}.{g_idx + 1}@eventpro.ai"
            rsvp = random.choice(rsvp_statuses)
            checked = False
            if rsvp == "Confirmed":
                # ~60% of confirmed guests actually checked in
                checked = (random.random() < 0.6)
            
            g = Guest(
                event_id=ev.id,
                name=name,
                email=email,
                rsvp_status=rsvp,
                checked_in=checked,
                check_in_time=now - timedelta(hours=random.randint(1, 4)) if checked else None
            )
            db.session.add(g)

    # 4. Tasks (10 events)
    tasks_pool = {
        0: [  # Wedding
            ("Book wedding venue", "Completed", "High", today_date - timedelta(days=30)),
            ("Finalise catering menu", "Completed", "High", today_date - timedelta(days=20)),
            ("Send invitations", "In Progress", "High", today_date + timedelta(days=5)),
            ("Arrange floral decorations", "In Progress", "Medium", today_date + timedelta(days=10)),
            ("Book photographer & videographer", "Completed", "High", today_date - timedelta(days=15)),
            ("Plan sangeet performances", "To Do", "Medium", today_date + timedelta(days=20)),
        ],
        1: [  # Birthday
            ("Book rooftop venue", "Completed", "High", today_date - timedelta(days=10)),
            ("Order custom cake", "In Progress", "High", today_date + timedelta(days=3)),
            ("Hire DJ", "Completed", "Medium", today_date - timedelta(days=7)),
            ("Plan surprise element", "To Do", "High", today_date + timedelta(days=5)),
            ("Arrange party favours", "To Do", "Low", today_date + timedelta(days=8)),
        ],
        2: [  # College Event
            ("Reserve auditorium", "Completed", "High", today_date - timedelta(days=25)),
            ("Confirm keynote speakers", "Completed", "High", today_date - timedelta(days=15)),
            ("Set up registration portal", "Completed", "High", today_date - timedelta(days=10)),
            ("Arrange AV equipment", "In Progress", "Medium", today_date + timedelta(days=5)),
            ("Design event banners & posters", "In Progress", "Medium", today_date + timedelta(days=7)),
            ("Coordinate volunteer teams", "To Do", "Medium", today_date + timedelta(days=12)),
        ],
        3: [  # Corporate
            ("Book convention centre", "Completed", "High", today_date - timedelta(days=40)),
            ("Finalise agenda & speakers", "Completed", "High", today_date - timedelta(days=25)),
            ("Send corporate invitations", "Completed", "High", today_date - timedelta(days=20)),
            ("Arrange networking dinner", "Completed", "Medium", today_date - timedelta(days=12)),
            ("Prepare presentation materials", "Completed", "Medium", today_date - timedelta(days=11)),
            ("Collect post-event feedback", "In Progress", "Medium", today_date + timedelta(days=2)),
        ],
        4: [  # Karan & Divya's Sangeet Night
            ("Book choreographer", "Completed", "High", today_date - timedelta(days=15)),
            ("Select sangeet playlist", "In Progress", "Medium", today_date + timedelta(days=5)),
            ("Finalise dance outfits", "To Do", "High", today_date + timedelta(days=10)),
            ("Arrange custom stage lighting", "To Do", "Medium", today_date + timedelta(days=18)),
            ("Reserve Udaipur palace lawns", "Completed", "High", today_date - timedelta(days=25)),
        ],
        5: [  # AI Synergy Developers Hackathon
            ("Draft hackathon rules & criteria", "Completed", "High", today_date - timedelta(days=5)),
            ("Order snacks, energy drinks & coffee", "In Progress", "High", today_date + timedelta(days=2)),
            ("Finalise judges panel & mentors", "In Progress", "High", today_date + timedelta(days=4)),
            ("Deploy testing staging server", "Completed", "Medium", today_date - timedelta(days=2)),
            ("Set up high-speed network routers", "To Do", "High", today_date + timedelta(days=8)),
            ("Order hackathon custom stickers & swag", "To Do", "Low", today_date + timedelta(days=9))
        ],
        6: [  # Corporate Strategy Offsite
            ("Finalise strategy agenda", "Completed", "High", today_date - timedelta(days=5)),
            ("Arrange keynote slides", "In Progress", "Medium", today_date + timedelta(days=2)),
            ("Book Goa flights", "Completed", "High", today_date - timedelta(days=12)),
            ("Set up dinner seating plan", "To Do", "Low", today_date + timedelta(days=10))
        ],
        7: [  # Arjun's Graduation Party
            ("Book private lounge area", "Completed", "High", today_date - timedelta(days=4)),
            ("Create music playlist", "Completed", "Medium", today_date - timedelta(days=2)),
            ("Design invitations flyer", "Completed", "Medium", today_date - timedelta(days=3))
        ],
        8: [  # Meera's Baby Shower
            ("Order theme pastries", "Completed", "High", today_date - timedelta(days=2)),
            ("Buy party game supplies", "In Progress", "Low", today_date + timedelta(days=1)),
            ("Hire florist decor team", "Completed", "Medium", today_date - timedelta(days=5))
        ],
        9: [  # Anjali & Rohan Engagement
            ("Finalise engagement ring booking", "Completed", "High", today_date - timedelta(days=20)),
            ("Order customized invitation boxes", "In Progress", "High", today_date + timedelta(days=5)),
            ("Coordinate photographer schedule", "Completed", "Medium", today_date - timedelta(days=10))
        ]
    }

    for idx, ev in enumerate(events):
        for title, status, priority, due in tasks_pool[idx]:
            t = Task(
                event_id=ev.id,
                title=title,
                status=status,
                priority=priority,
                deadline=due,
                category="General"
            )
            db.session.add(t)

    # 5. Vendors (10 events)
    vendors_pool = {
        0: [  # Wedding
            ("Royal Caterers", "Catering", "royalcaterers@mail.com", "9876543210", 525000, "Confirmed"),
            ("Shutter Studio", "Photography", "shutter@mail.com", "9876543211", 150000, "Confirmed"),
            ("Bloom & Petal", "Decoration", "bloom@mail.com", "9876543212", 200000, "Confirmed"),
            ("DJ Ravi", "Music", "djravi@mail.com", "9876543213", 75000, "Contacted"),
            ("The Grand Palace, Jaipur", "Venue", "grandpalace@mail.com", "9876543219", 450000, "Confirmed"),
            ("Elite Event Management", "General", "elitemgmt@mail.com", "9876543209", 120000, "Confirmed")
        ],
        1: [  # Birthday
            ("Cakewalk Bakery", "Catering", "cakewalk@mail.com", "9876543220", 25000, "Confirmed"),
            ("DJ Spin Master", "Music", "spinmaster@mail.com", "9876543221", 30000, "Confirmed"),
            ("Party Props Co.", "Decoration", "partyprops@mail.com", "9876543222", 20000, "Confirmed"),
            ("Skyline Rooftop Lounge, Mumbai", "Venue", "skyline@mail.com", "9876543229", 45000, "Confirmed"),
            ("Neon Lights & Sound Host", "General", "neonhost@mail.com", "9876543218", 15000, "Confirmed")
        ],
        2: [  # College Event
            ("Campus Bites", "Catering", "campusbites@mail.com", "9876543230", 87500, "Confirmed"),
            ("TechAV Solutions", "General", "techav@mail.com", "9876543231", 52500, "Confirmed"),
            ("Print Express", "Decoration", "printex@mail.com", "9876543232", 35000, "Contacted"),
            ("Stage Crafters", "Decoration", "stagecraft@mail.com", "9876543233", 52500, "Confirmed"),
            ("University Auditorium, Bengaluru", "Venue", "uniauditorium@mail.com", "9876543239", 100000, "Confirmed")
        ],
        3: [  # Corporate
            ("Marriott In-House Catering", "Catering", "marriott@mail.com", "9876543240", 240000, "Confirmed"),
            ("ProAV India", "General", "proav@mail.com", "9876543241", 120000, "Confirmed"),
            ("Elite Decor", "Decoration", "elitedecor@mail.com", "9876543242", 80000, "Confirmed"),
            ("Lens Kraft Studios", "Photography", "lenskraft@mail.com", "9876543243", 60000, "Confirmed"),
            ("Convention Centre, New Delhi", "Venue", "conventiondelhi@mail.com", "9876543249", 250000, "Confirmed")
        ],
        4: [  # Karan & Divya's Sangeet Night
            ("Beat Drop DJ", "Music", "beatdrop@mail.com", "9876543245", 45000, "Confirmed"),
            ("Royal Lights", "Decoration", "royallights@mail.com", "9876543246", 80000, "Confirmed"),
            ("Lakeview Caterers", "Catering", "lakeview@mail.com", "9876543249", 150000, "Confirmed"),
            ("Zenana Mahal, Udaipur", "Venue", "zenanamahal@mail.com", "9876543244", 150000, "Confirmed"),
            ("Sangeet Choreography Crew", "General", "choreographer@mail.com", "9876543238", 60000, "Confirmed")
        ],
        5: [  # AI Synergy Developers Hackathon
            ("Cloud Servers Inc", "General", "cloud@mail.com", "9876543247", 120000, "Confirmed"),
            ("Mega Pizzas", "Catering", "megapizzas@mail.com", "9876543248", 50000, "Confirmed"),
            ("Hackathon T-Shirts Co", "Decoration", "shirts@mail.com", "9876543250", 15000, "Confirmed"),
            ("Innovators Hub, Bengaluru", "Venue", "innovators@mail.com", "9876543259", 75000, "Confirmed")
        ],
        6: [  # Corporate Strategy Offsite
            ("Hyatt Banquet Catering", "Catering", "hyatt@mail.com", "9876543261", 200000, "Confirmed"),
            ("Goa Sound & Lights", "Music", "goasound@mail.com", "9876543262", 50000, "Confirmed"),
            ("Grand Hyatt, Goa", "Venue", "grandhyattgoa@mail.com", "9876543269", 180000, "Confirmed"),
            ("Corporate Team Building Facilitators", "General", "facilitators@mail.com", "9876543258", 75000, "Confirmed")
        ],
        7: [  # Arjun's Graduation Party
            ("Hard Rock Catering", "Catering", "hrc@mail.com", "9876543263", 40000, "Confirmed"),
            ("Party Beats DJ", "Music", "partybeats@mail.com", "9876543264", 25000, "Confirmed"),
            ("Hard Rock Cafe, Bengaluru", "Venue", "hrcafe@mail.com", "9876543279", 30000, "Confirmed"),
            ("Graduation Photo Booth Services", "General", "photobooth@mail.com", "9876543278", 10000, "Confirmed")
        ],
        8: [  # Meera's Baby Shower
            ("Sheraton High Tea", "Catering", "sheraton@mail.com", "9876543265", 60000, "Confirmed"),
            ("Rose Petals Florals", "Decoration", "rosepetals@mail.com", "9876543266", 40000, "Confirmed"),
            ("Sheraton Grand, Pune", "Venue", "sheratonpune@mail.com", "9876543289", 50000, "Confirmed"),
            ("Baby Shower Games Emcee", "General", "babyemcee@mail.com", "9876543288", 12000, "Confirmed")
        ],
        9: [  # Anjali & Rohan Engagement
            ("Umaid Palace Catering", "Catering", "umaid@mail.com", "9876543267", 350000, "Confirmed"),
            ("Desert Melodies Band", "Music", "desert@mail.com", "9876543268", 100000, "Confirmed"),
            ("Umaid Bhawan Palace, Jodhpur", "Venue", "umaidbhawan@mail.com", "9876543290", 250000, "Confirmed"),
            ("Custom Engagement Gifting Hampers", "General", "hampers@mail.com", "9876543298", 50000, "Confirmed")
        ]
    }

    for idx, ev in enumerate(events):
        for name, cat, email, phone, cost, status in vendors_pool[idx]:
            v = Vendor(
                event_id=ev.id,
                name=name,
                category=cat,
                email=email,
                contact=phone,
                cost=cost,
                status=status,
                rating=4.5
            )
            db.session.add(v)

    # 6. Feedback (10 events)
    feedback_pool = {
        0: [  # Wedding
            ("Absolutely stunning venue! The decorations were breathtaking.", 5, "Positive", "😍"),
            ("Food was delicious but service was a bit slow during dinner.", 4, "Neutral", "😊"),
            ("The photography team captured every moment beautifully.", 5, "Positive", "😍"),
            ("Music could have been better during the sangeet night.", 3, "Neutral", "😐"),
            ("Overall a magical experience, everything was well organised.", 5, "Positive", "😍"),
            ("Parking was a nightmare, but inside everything was perfect.", 4, "Neutral", "😊"),
        ],
        1: [  # Birthday
            ("Best birthday party ever! The DJ was amazing!", 5, "Positive", "😍"),
            ("Loved the rooftop setting, very Instagram-worthy.", 5, "Positive", "😍"),
            ("The cake was a masterpiece, tasted as good as it looked!", 5, "Positive", "😍"),
            ("A bit too crowded, but the vibe was great.", 3, "Neutral", "😐"),
            ("Surprise element was perfectly executed, so much fun!", 4, "Positive", "😊"),
        ],
        2: [  # College Event
            ("Keynote sessions were incredibly insightful and inspiring.", 5, "Positive", "😍"),
            ("Hackathon was well organised with great mentorship.", 4, "Positive", "😊"),
            ("Food quality was average, expected better from the caterers.", 2, "Negative", "😞"),
            ("The robotics competition was the highlight of the fest!", 5, "Positive", "😍"),
            ("Registration process was smooth and hassle-free.", 4, "Positive", "😊"),
            ("Venue was a bit warm, AC wasn't working properly.", 2, "Negative", "😞"),
        ],
        3: [  # Corporate
            ("Excellent panels with truly thought-provoking discussions.", 5, "Positive", "😍"),
            ("Networking dinner was a great touch, made valuable connections.", 5, "Positive", "😍"),
            ("Presentations ran over time, schedule needs better management.", 3, "Neutral", "😐"),
            ("The venue and hospitality were top-notch, very professional.", 5, "Positive", "😍"),
            ("Some sessions felt too sales-pitchy rather than educational.", 2, "Negative", "😞"),
            ("Overall a well-executed summit, looking forward to next year.", 4, "Positive", "😊"),
        ],
        4: [  # Karan & Divya's Sangeet Night
            ("The stage setup and lighting were outstanding. Loved the vibes!", 5, "Positive", "😍"),
            ("The Rajasthani street food stalls were a hit! Outstanding catering.", 5, "Positive", "😍"),
            ("DJ did a decent job, but skipped a couple of requested sangeet songs.", 4, "Neutral", "😊")
        ],
        5: [  # AI Synergy Developers Hackathon
            ("Super fast internet and great cloud support. The mentors were helpful.", 5, "Positive", "😍"),
            ("Loved the pizza and energy drinks! Made code debugging easier.", 4, "Positive", "😊"),
            ("The hacking session space was slightly cramped, but overall had an amazing crowd.", 4, "Positive", "😊")
        ],
        6: [  # Corporate Strategy Offsite
            ("The strategy alignment was smooth and the Goan food was perfect.", 5, "Positive", "😍"),
            ("Great AV setup for our presentations.", 5, "Positive", "😍")
        ],
        7: [  # Arjun's Graduation Party
            ("Amazing music and delicious burgers! Loved the party.", 5, "Positive", "😍"),
            ("Had a blast with friends, highly recommend this place.", 4, "Positive", "😊")
        ],
        8: [  # Meera's Baby Shower
            ("A very pleasant high tea experience and beautiful florals.", 5, "Positive", "😍"),
            ("Fun games and lovely atmosphere.", 4, "Positive", "😊")
        ],
        9: [  # Anjali & Rohan Engagement
            ("The engagement ceremony was regal and royal. Perfect venue!", 5, "Positive", "😍"),
            ("A grand musical evening, very well organized.", 5, "Positive", "😍")
        ]
    }

    for idx, ev in enumerate(events):
        for comment, rating, sentiment, emoji in feedback_pool[idx]:
            f = Feedback(
                event_id=ev.id,
                guest_name="Guest User",
                comment=comment,
                rating=rating,
                sentiment=sentiment,
                emoji=emoji
            )
            db.session.add(f)

    # 7. Budget Items (10 events)
    budget_pool = {
        0: [  # Wedding
            ("Venue Rental", "Venue", 450000, 420000),
            ("Catering & Bar", "Catering", 525000, 490000),
            ("Floral Decorations", "Decorations", 225000, 200000),
            ("Photography & Video", "Photography", 150000, 150000),
            ("DJ & Live Band", "Entertainment", 75000, 60000),
            ("Invitations & Misc", "Miscellaneous", 75000, 55000),
        ],
        1: [  # Birthday
            ("Venue Booking", "Venue", 30000, 30000),
            ("Food & Drinks", "Catering", 45000, 42000),
            ("Theme Decorations", "Decorations", 30000, 28000),
            ("DJ & Sound System", "Entertainment", 30000, 30000),
            ("Photo Booth", "Photography", 7500, 7000),
            ("Party Favours & Misc", "Miscellaneous", 7500, 5000),
        ],
        2: [  # College Event
            ("Auditorium Booking", "Venue", 87500, 80000),
            ("Catering & Snacks", "Catering", 87500, 75000),
            ("Stage & Banners", "Decorations", 52500, 48000),
            ("AV & Tech Setup", "Tech/AV", 52500, 52500),
            ("Marketing & Promo", "Marketing", 35000, 30000),
            ("Prizes & Miscellaneous", "Miscellaneous", 35000, 25000),
        ],
        3: [  # Corporate
            ("Convention Centre", "Venue", 280000, 280000),
            ("Meals & Refreshments", "Catering", 240000, 235000),
            ("AV & Presentation Tech", "Tech/AV", 120000, 118000),
            ("Decor & Signage", "Decorations", 80000, 72000),
            ("Entertainment & Speaker Fees", "Entertainment", 40000, 40000),
            ("Printing & Miscellaneous", "Miscellaneous", 40000, 32000),
        ],
        4: [  # Karan & Divya's Sangeet Night
            ("Choreography & Sound", "Entertainment", 150000, 140000),
            ("Theme Lighting", "Decorations", 100000, 95000),
            ("Venue Rental", "Venue", 150000, 150000),
            ("Catering & Drinks", "Catering", 100000, 90000),
        ],
        5: [  # AI Synergy Developers Hackathon
            ("Cloud Infrastructure", "Tech/AV", 120000, 115000),
            ("Catering & Snacks", "Catering", 60000, 58000),
            ("Prize Pool", "Miscellaneous", 50000, 50000),
            ("Venue & Setup", "Venue", 20000, 18000),
        ],
        6: [  # Corporate Strategy Offsite
            ("Goa Hyatt Conference Lawn", "Venue", 300000, 300000),
            ("Conference Catering & Dinner", "Catering", 200000, 190000),
            ("Audio Visual Equipment", "Tech/AV", 50000, 48000),
            ("Miscellaneous Logistics", "Miscellaneous", 50000, 45000)
        ],
        7: [  # Arjun's Graduation Party
            ("HRC Lounge Area", "Venue", 30000, 30000),
            ("Dinner & Drinks", "Catering", 40000, 38000),
            ("DJ Sound & Lighting", "Entertainment", 25000, 25000),
            ("Invitations & Decor", "Miscellaneous", 5000, 4500)
        ],
        8: [  # Meera's Baby Shower
            ("Sheraton Banquet Hall", "Venue", 60000, 60000),
            ("High Tea & Desserts", "Catering", 60000, 55000),
            ("Floral Decor & Setup", "Decorations", 40000, 38000),
            ("Return Gifts & Games", "Miscellaneous", 20000, 18000)
        ],
        9: [  # Anjali & Rohan Engagement
            ("Umaid Palace Lawns", "Venue", 300000, 300000),
            ("Engagement Feast", "Catering", 350000, 340000),
            ("Traditional Music Band", "Entertainment", 100000, 100000),
            ("Exotic Floral Mandap", "Decorations", 50000, 48000)
        ]
    }

    for idx, ev in enumerate(events):
        for _, category, estimated, actual in budget_pool[idx]:
            b = BudgetItem(
                event_id=ev.id,
                category=category,
                allocated_amount=float(estimated),
                spent_amount=float(actual)
            )
            db.session.add(b)

    # 8. Reminders / Notifications
    from app.models.reminder import Reminder
    reminders_data = [
        {
            "title": "New RSVP from Priya Sharma",
            "message": "Priya Sharma has confirmed attendance for Raj & Meera's Wedding.",
            "remind_at": datetime.utcnow() - timedelta(minutes=2),
            "is_read": False,
            "event_id": events[0].id,
            "user_id": demo_user.id
        },
        {
            "title": "Event Coming Up",
            "message": "Event 'Sarah's Sweet 16 Bash' is in 12 days.",
            "remind_at": datetime.utcnow() - timedelta(hours=1),
            "is_read": False,
            "event_id": events[1].id,
            "user_id": demo_user.id
        },
        {
            "title": "AI Report Generated",
            "message": "AI successfully generated the budget report for National Youth Tech Summit.",
            "remind_at": datetime.utcnow() - timedelta(hours=3),
            "is_read": True,
            "event_id": events[2].id,
            "user_id": demo_user.id
        },
        {
            "title": "Sangeet Prep Update",
            "message": "A new task 'Arrange custom stage lighting' has been added to Karan & Divya's Sangeet Night.",
            "remind_at": datetime.utcnow() - timedelta(hours=4),
            "is_read": False,
            "event_id": events[4].id,
            "user_id": demo_user.id
        },
        {
            "title": "Hackathon Registration Alert",
            "message": "Sam Altman registered for AI Synergy Developers Hackathon.",
            "remind_at": datetime.utcnow() - timedelta(hours=5),
            "is_read": False,
            "event_id": events[5].id,
            "user_id": demo_user.id
        }
    ]
    for r_data in reminders_data:
        r = Reminder(**r_data)
        db.session.add(r)

    # 9. Commit
    db.session.commit()
    print("Database seeding completed.")
