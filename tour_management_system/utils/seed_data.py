from datetime import date, timedelta

from auth import hash_password
from config import ADMIN_EMAIL, ADMIN_PASSWORD, ROLES
from database import get_session
from models import Booking, Payment, Resource, TourPackage, User


TOUR_IMAGES = {
    "Goa": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=1200&q=80",
    "Manali": "https://images.unsplash.com/photo-1605649487212-47bdab064df7?auto=format&fit=crop&w=1200&q=80",
    "Kashmir": "https://images.unsplash.com/photo-1595815771614-ade9d652a65d?auto=format&fit=crop&w=1200&q=80",
    "Rajasthan": "https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=1200&q=80",
    "Kerala": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=1200&q=80",
    "Jaipur": "https://images.unsplash.com/photo-1603262110263-fb0112e7cc33?auto=format&fit=crop&w=1200&q=80",
    "Meghalaya": "https://images.unsplash.com/photo-1622454546394-a7b6c9f8f4cf?auto=format&fit=crop&w=1200&q=80",
    "Dubai": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=1200&q=80",
    "Bali": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=1200&q=80",
    "Singapore": "https://images.unsplash.com/photo-1525625293386-3f8f99389edd?auto=format&fit=crop&w=1200&q=80",
    "Andaman": "https://images.unsplash.com/photo-1540202404-a2f29016b523?auto=format&fit=crop&w=1200&q=80",
    "Ladakh": "https://images.unsplash.com/photo-1581793745862-99fde7fa73d2?auto=format&fit=crop&w=1200&q=80",
}


def itinerary(*days):
    return "\n".join(f"Day {index + 1}: {text}" for index, text in enumerate(days))


EXTRA_PACKAGES = [
    (
        "Varanasi Spiritual Circuit",
        "Varanasi",
        "Ganga aarti, heritage alleys, temple visits, sunrise boat rides, and Sarnath history.",
        4,
        13999,
        26,
        36,
        "Heritage",
        "https://images.unsplash.com/photo-1561361058-c24cecae35ca?auto=format&fit=crop&w=1200&q=80",
        itinerary("Arrival and evening Ganga aarti", "Sunrise boat ride and old-city walk", "Sarnath Buddhist circuit", "Temple visits and departure"),
    ),
    (
        "Rishikesh River Rush",
        "Rishikesh",
        "Rafting, riverside camps, yoga mornings, cafes, and Himalayan foothill views.",
        3,
        9999,
        18,
        28,
        "Adventure",
        "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=1200&q=80",
        itinerary("Arrival and riverside camp", "White-water rafting and bonfire", "Yoga morning and Lakshman Jhula visit"),
    ),
    (
        "Coorg Coffee Trails",
        "Coorg",
        "Coffee estates, waterfalls, misty viewpoints, spice plantations, and homestay comfort.",
        4,
        17999,
        22,
        32,
        "Nature",
        "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=1200&q=80",
        itinerary("Arrival and estate walk", "Abbey Falls and Madikeri Fort", "Plantation tour and viewpoint sunset", "Local breakfast and departure"),
    ),
    (
        "Udaipur Royal Romance",
        "Udaipur",
        "Lake views, palaces, candlelight dinner, folk dance, and royal old-city lanes.",
        4,
        21999,
        16,
        24,
        "Honeymoon",
        "https://images.unsplash.com/photo-1599661046827-dacde6976549?auto=format&fit=crop&w=1200&q=80",
        itinerary("Arrival and lake evening", "City Palace and Jagdish Temple", "Sajjangarh sunset and cultural dinner", "Shopping and departure"),
    ),
    (
        "Mysore Ooty Family Delight",
        "Mysore and Ooty",
        "Palace architecture, gardens, toy train memories, tea estates, and cool hill weather.",
        5,
        23999,
        24,
        36,
        "Family",
        "https://images.unsplash.com/photo-1578662996442-48f60103fc96?auto=format&fit=crop&w=1200&q=80",
        itinerary("Mysore arrival and palace", "Brindavan Gardens", "Ooty transfer and lake", "Tea gardens and viewpoints", "Departure"),
    ),
    (
        "Spiti Valley Expedition",
        "Spiti",
        "Cold desert landscapes, monasteries, high-altitude villages, and dramatic Himalayan roads.",
        8,
        48999,
        9,
        18,
        "Adventure",
        "https://images.unsplash.com/photo-1616423841125-830766a04681?auto=format&fit=crop&w=1200&q=80",
        itinerary("Shimla arrival", "Drive to Kalpa", "Nako and Tabo", "Kaza monasteries", "Key and Kibber", "Chandratal route", "Manali transfer", "Departure"),
    ),
    (
        "Sikkim Himalayan Escape",
        "Sikkim",
        "Gangtok, Tsomgo Lake, monasteries, waterfalls, and mountain viewpoints.",
        6,
        31999,
        15,
        24,
        "Nature",
        "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=1200&q=80",
        itinerary("Gangtok arrival", "Tsomgo Lake and Baba Mandir", "Rumtek Monastery", "Pelling transfer", "Skywalk and waterfalls", "Departure"),
    ),
    (
        "Pondicherry French Quarter",
        "Pondicherry",
        "Colorful streets, seaside promenade, cafes, Auroville, beaches, and boutique stays.",
        3,
        12999,
        30,
        40,
        "Beach",
        "https://images.unsplash.com/photo-1582972236019-ea4af5ffe587?auto=format&fit=crop&w=1200&q=80",
        itinerary("Arrival and French Quarter walk", "Auroville and cafes", "Promenade sunrise and departure"),
    ),
    (
        "Hampi Backpacker Heritage",
        "Hampi",
        "Boulder landscapes, UNESCO ruins, coracle rides, temples, and sunset points.",
        4,
        14999,
        20,
        30,
        "Heritage",
        "https://images.unsplash.com/photo-1600100397608-f0100f0c158e?auto=format&fit=crop&w=1200&q=80",
        itinerary("Arrival and riverside stay", "Virupaksha Temple and bazaar ruins", "Vittala Temple and coracle ride", "Sunrise viewpoint and departure"),
    ),
    (
        "Lakshadweep Coral Cruise",
        "Lakshadweep",
        "Lagoon beaches, coral viewing, island leisure, snorkeling, and turquoise water stays.",
        5,
        64999,
        8,
        16,
        "Beach",
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
        itinerary("Kochi reporting and transfer", "Island arrival and lagoon walk", "Snorkeling and glass-bottom boat", "Beach leisure", "Return transfer"),
    ),
    (
        "Thailand Island Hopper",
        "Thailand",
        "Bangkok energy, Phuket beaches, Phi Phi excursion, street food, and island nightlife.",
        6,
        55999,
        25,
        40,
        "International",
        "https://images.unsplash.com/photo-1528181304800-259b08848526?auto=format&fit=crop&w=1200&q=80",
        itinerary("Bangkok arrival", "Temple city tour", "Phuket transfer", "Phi Phi island tour", "Beach leisure", "Departure"),
    ),
    (
        "Maldives Blue Lagoon",
        "Maldives",
        "Water villas, lagoon swims, reef snorkeling, sunset cruise, and premium island comfort.",
        5,
        82999,
        12,
        20,
        "Honeymoon",
        "https://images.unsplash.com/photo-1514282401047-d79a71a590e8?auto=format&fit=crop&w=1200&q=80",
        itinerary("Male arrival and resort transfer", "Lagoon leisure", "Snorkeling and water sports", "Sunset cruise", "Departure"),
    ),
    (
        "Vietnam Culture Trail",
        "Vietnam",
        "Hanoi, Ha Long Bay, lantern streets, local markets, and scenic boat experiences.",
        7,
        61999,
        18,
        30,
        "International",
        "https://images.unsplash.com/photo-1528127269322-539801943592?auto=format&fit=crop&w=1200&q=80",
        itinerary("Hanoi arrival", "Old Quarter tour", "Ha Long Bay cruise", "Da Nang transfer", "Hoi An lantern walk", "Ba Na Hills", "Departure"),
    ),
    (
        "Japan Cherry Blossom Sampler",
        "Japan",
        "Tokyo neighborhoods, Kyoto temples, bullet train experience, and seasonal gardens.",
        7,
        149999,
        10,
        20,
        "International",
        "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=1200&q=80",
        itinerary("Tokyo arrival", "Tokyo city highlights", "Mt Fuji region", "Bullet train to Kyoto", "Kyoto temples", "Osaka evening", "Departure"),
    ),
    (
        "Europe Student Explorer",
        "Paris, Swiss Alps and Amsterdam",
        "A compact Europe starter tour with city icons, alpine views, canals, and group-friendly planning.",
        9,
        189999,
        14,
        28,
        "International",
        "https://images.unsplash.com/photo-1467269204594-9661b134dd2b?auto=format&fit=crop&w=1200&q=80",
        itinerary("Paris arrival", "Eiffel Tower and Louvre area", "Lucerne transfer", "Mt Titlis excursion", "Rhine Falls", "Amsterdam canals", "Zaanse Schans", "Free day", "Departure"),
    ),
    (
        "Auli Snow Escape",
        "Auli",
        "Snow views, ropeway ride, skiing basics, pine forests, and Himalayan sunrise moments.",
        5,
        26999,
        14,
        24,
        "Adventure",
        "https://images.unsplash.com/photo-1483921020237-2ff51e8e4b22?auto=format&fit=crop&w=1200&q=80",
        itinerary("Haridwar arrival and transfer", "Joshimath to Auli", "Skiing basics and ropeway", "Gurso Bugyal walk", "Departure"),
    ),
    (
        "Kutch White Desert Festival",
        "Kutch",
        "White desert sunsets, craft villages, tent city experience, folk music, and local cuisine.",
        4,
        20999,
        21,
        32,
        "Heritage",
        "https://images.unsplash.com/photo-1518002054494-3a6f94352e9d?auto=format&fit=crop&w=1200&q=80",
        itinerary("Bhuj arrival", "Craft villages and museum", "White Rann sunset and folk show", "Mandvi beach and departure"),
    ),
    (
        "Munnar Tea Garden Retreat",
        "Munnar",
        "Rolling tea estates, misty hills, dams, viewpoints, and calm nature walks.",
        4,
        16999,
        27,
        38,
        "Nature",
        "https://images.unsplash.com/photo-1593693397690-362cb9666fc2?auto=format&fit=crop&w=1200&q=80",
        itinerary("Arrival and tea estate walk", "Eravikulam National Park", "Mattupetty Dam and viewpoints", "Departure"),
    ),
    (
        "Mumbai City Lights",
        "Mumbai",
        "Marine Drive, heritage buildings, Bollywood studio, street food, and coastal city energy.",
        3,
        11999,
        32,
        45,
        "Family",
        "https://images.unsplash.com/photo-1529253355930-ddbe423a2ac7?auto=format&fit=crop&w=1200&q=80",
        itinerary("Arrival and Marine Drive", "South Mumbai heritage and food trail", "Studio visit and departure"),
    ),
    (
        "Hyderabad Nizam Trail",
        "Hyderabad",
        "Charminar lanes, Golconda Fort, biryani food trail, museums, and lake views.",
        3,
        10999,
        34,
        44,
        "Heritage",
        "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?auto=format&fit=crop&w=1200&q=80",
        itinerary("Arrival and Charminar", "Golconda Fort and Qutub Shahi Tombs", "Museum visit and departure"),
    ),
    (
        "Gokarna Slow Beach",
        "Gokarna",
        "Quiet beaches, cliff walks, yoga mornings, seafood cafes, and laid-back coastal stays.",
        4,
        14999,
        19,
        28,
        "Beach",
        "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=1200&q=80",
        itinerary("Arrival and Om Beach", "Half Moon Beach trek", "Temple visit and cafe evening", "Departure"),
    ),
    (
        "Tawang Monastery Route",
        "Tawang",
        "Northeast mountain roads, monasteries, high passes, lakes, and quiet borderland views.",
        7,
        42999,
        10,
        20,
        "Nature",
        "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80",
        itinerary("Guwahati arrival", "Bomdila transfer", "Dirang valley", "Sela Pass and Tawang", "Monastery and local sights", "Return route", "Departure"),
    ),
    (
        "Gir Wildlife Weekend",
        "Gir",
        "Wildlife safari, forest lodge stay, interpretation zone, local food, and nature photography.",
        3,
        18999,
        12,
        22,
        "Nature",
        "https://images.unsplash.com/photo-1516426122078-c23e76319801?auto=format&fit=crop&w=1200&q=80",
        itinerary("Arrival and forest lodge", "Morning safari and interpretation zone", "Local village visit and departure"),
    ),
    (
        "Agra Mathura Vrindavan",
        "Agra, Mathura and Vrindavan",
        "Taj Mahal sunrise, Mughal history, temple towns, and cultural evening experiences.",
        3,
        12999,
        28,
        42,
        "Family",
        "https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=1200&q=80",
        itinerary("Agra arrival and fort", "Taj Mahal sunrise and Mathura transfer", "Vrindavan temples and departure"),
    ),
]


def seed_database():
    with get_session() as session:
        if not session.query(User).filter(User.email == ADMIN_EMAIL).first():
            session.add(
                User(
                    name="Demo Administrator",
                    email=ADMIN_EMAIL,
                    phone="9999999999",
                    password_hash=hash_password(ADMIN_PASSWORD),
                    role=ROLES["ADMIN"],
                    is_active=True,
                )
            )

        if not session.query(User).filter(User.email == "customer@example.com").first():
            customer = User(
                name="Aarav Sharma",
                email="customer@example.com",
                phone="9876543210",
                password_hash=hash_password("Customer@123"),
                role=ROLES["CUSTOMER"],
                is_active=True,
            )
            session.add(customer)
            session.flush()
        else:
            customer = session.query(User).filter(User.email == "customer@example.com").first()

        if session.query(TourPackage).count() == 0:
            packages = [
                ("Goa Beach Escape", "Goa", "Sunlit beaches, Portuguese lanes, seafood nights, and water sports.", 4, 15999, 18, 30, "Beach", TOUR_IMAGES["Goa"], itinerary("Arrival and beach walk at Calangute", "Fort Aguada and water sports", "Old Goa churches and cruise dinner", "Leisure morning and departure")),
                ("Manali Adventure", "Manali", "Mountain escape with rafting, Solang Valley activities, and cozy evenings.", 5, 18999, 14, 25, "Adventure", TOUR_IMAGES["Manali"], itinerary("Arrival and Mall Road", "Solang Valley adventure activities", "Atal Tunnel and Sissu excursion", "Local temples and cafes", "Departure")),
                ("Kashmir Paradise", "Kashmir", "Houseboats, gardens, snow views, and calm lakes in the valley.", 6, 32999, 12, 20, "Nature", TOUR_IMAGES["Kashmir"], itinerary("Srinagar arrival and Dal Lake shikara", "Mughal gardens", "Gulmarg day trip", "Pahalgam valley", "Local markets", "Departure")),
                ("Rajasthan Heritage Tour", "Rajasthan", "Royal forts, desert evening, folk performances, and historic cities.", 7, 27999, 20, 32, "Heritage", TOUR_IMAGES["Rajasthan"], itinerary("Jaipur arrival", "Amber Fort and City Palace", "Jodhpur Mehrangarh Fort", "Jaisalmer desert camp", "Camel safari", "Udaipur lake evening", "Departure")),
                ("Kerala Backwaters", "Kerala", "Lush greenery, houseboat stay, tea gardens, and peaceful canals.", 5, 24999, 16, 28, "Family", TOUR_IMAGES["Kerala"], itinerary("Cochin arrival", "Munnar tea gardens", "Munnar sightseeing", "Alleppey houseboat", "Departure")),
                ("Jaipur Heritage Journey", "Jaipur", "A compact royal city break with forts, bazaars, and cultural dining.", 3, 11999, 24, 35, "Heritage", TOUR_IMAGES["Jaipur"], itinerary("Arrival and local bazaar", "Amber Fort, Hawa Mahal, City Palace", "Jantar Mantar and departure")),
                ("Meghalaya Nature Explorer", "Meghalaya", "Living root bridges, waterfalls, caves, and green hills.", 6, 28999, 10, 18, "Nature", TOUR_IMAGES["Meghalaya"], itinerary("Shillong arrival", "Cherrapunji waterfalls", "Root bridge trek", "Dawki river", "Mawlynnong village", "Departure")),
                ("Dubai City Escape", "Dubai", "Skyscrapers, desert safari, marina cruise, shopping, and global dining.", 5, 52999, 22, 40, "International", TOUR_IMAGES["Dubai"], itinerary("Arrival and marina", "City tour and Burj Khalifa", "Desert safari", "Miracle Garden and shopping", "Departure")),
                ("Bali Tropical Retreat", "Bali", "Temples, beaches, rice terraces, waterfalls, and island relaxation.", 6, 58999, 15, 30, "Honeymoon", TOUR_IMAGES["Bali"], itinerary("Arrival in Bali", "Ubud and rice terraces", "Waterfall trail", "Nusa Penida day trip", "Beach leisure", "Departure")),
                ("Singapore Explorer", "Singapore", "Urban gardens, Sentosa, skyline experiences, and family attractions.", 4, 44999, 28, 45, "International", TOUR_IMAGES["Singapore"], itinerary("Arrival and Night Safari", "City tour and Gardens by the Bay", "Sentosa Island", "Shopping and departure")),
                ("Andaman Island Holiday", "Andaman", "Clear water beaches, island hopping, and historic Cellular Jail.", 5, 38999, 13, 22, "Beach", TOUR_IMAGES["Andaman"], itinerary("Port Blair arrival", "Cellular Jail and light show", "Havelock ferry", "Radhanagar Beach", "Departure")),
                ("Ladakh Bike Expedition", "Ladakh", "High passes, monasteries, Pangong Lake, and rugged adventure roads.", 8, 45999, 8, 18, "Adventure", TOUR_IMAGES["Ladakh"], itinerary("Leh arrival", "Acclimatization and monasteries", "Khardung La", "Nubra Valley", "Pangong Lake", "Chang La return", "Leh leisure", "Departure")),
            ]
            for title, destination, description, duration, price, available, total, category, image, plan in packages:
                session.add(
                    TourPackage(
                        title=title,
                        destination=destination,
                        description=description,
                        itinerary=plan,
                        duration_days=duration,
                        price=price,
                        available_seats=available,
                        total_seats=total,
                        category=category,
                        image_url=image,
                        is_active=True,
                    )
                )
            session.flush()

        for title, destination, description, duration, price, available, total, category, image, plan in EXTRA_PACKAGES:
            existing_tour = session.query(TourPackage).filter(TourPackage.title == title).first()
            if existing_tour:
                existing_tour.destination = destination
                existing_tour.description = description
                existing_tour.itinerary = plan
                existing_tour.duration_days = duration
                existing_tour.price = price
                existing_tour.total_seats = max(existing_tour.total_seats, total)
                existing_tour.available_seats = min(existing_tour.available_seats, existing_tour.total_seats)
                existing_tour.category = category
                existing_tour.image_url = image
                existing_tour.is_active = True
            else:
                session.add(
                    TourPackage(
                        title=title,
                        destination=destination,
                        description=description,
                        itinerary=plan,
                        duration_days=duration,
                        price=price,
                        available_seats=available,
                        total_seats=total,
                        category=category,
                        image_url=image,
                        is_active=True,
                    )
                )

        if session.query(Booking).count() == 0:
            tours = session.query(TourPackage).limit(4).all()
            statuses = [("Confirmed", "Paid"), ("Pending Payment", "Unpaid"), ("Modified", "Paid")]
            for index, tour in enumerate(tours[:3]):
                status, pay_status = statuses[index]
                travelers = index + 2
                booking = Booking(
                    user_id=customer.id,
                    tour_id=tour.id,
                    booking_date=date.today() - timedelta(days=20 - index * 5),
                    travel_date=date.today() + timedelta(days=20 + index * 15),
                    travelers=travelers,
                    total_amount=tour.price * travelers,
                    status=status,
                    payment_status=pay_status,
                    special_requests="Vegetarian meals preferred." if index == 0 else "",
                )
                tour.available_seats = max(0, tour.available_seats - travelers)
                session.add(booking)
                session.flush()
                if pay_status == "Paid":
                    session.add(
                        Payment(
                            booking_id=booking.id,
                            transaction_id=f"TXN-DEMO-{booking.id:04d}",
                            amount=booking.total_amount,
                            payment_method="UPI",
                            status="SUCCESS",
                        )
                    )
                    session.add(
                        Resource(
                            booking_id=booking.id,
                            resource_type="Hotel Room",
                            resource_name=f"Partner Hotel Block {booking.id}",
                            quantity=max(1, travelers // 2),
                            status="Allocated",
                        )
                    )
