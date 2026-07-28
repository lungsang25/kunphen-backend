"""Seed the database with the current website mock data.

Usage: python -m scripts.seed
"""
from datetime import datetime, timezone

from app.database import SessionLocal
from app.models import Article, GalleryImage, Medicine

PLACEHOLDER = "/placeholder.svg"

MEDICINES = [
    {
        "name": "Agar-35",
        "tibetan_name": "ཨ་གར་སོ་ལྔ།",
        "description": "A calming formula for stress, anxiety, and nervous system balance.",
        "full_description": "Agar-35 is one of the most renowned Tibetan formulations, composed of 35 carefully selected ingredients including aquilaria, clove, and saffron. It is traditionally used to pacify wind (rLung) imbalances manifesting as anxiety, insomnia, and heart palpitations.",
        "image_url": PLACEHOLDER,
        "uses": ["Anxiety & Stress Relief", "Insomnia", "Heart Palpitations", "Nervous System Support"],
    },
    {
        "name": "Ratna Samphel",
        "tibetan_name": "རིན་ཆེན་བསམ་འཕེལ།",
        "description": "A precious pill for detoxification and immune system strengthening.",
        "full_description": "Ratna Samphel, or 'Precious Wish-fulfilling Jewel,' is a revered compound pill containing processed precious metals and rare herbs. Used for deep-level detoxification and rejuvenation of the body's vital energies.",
        "image_url": PLACEHOLDER,
        "uses": ["Detoxification", "Immune Boosting", "Chronic Fatigue", "Overall Rejuvenation"],
    },
    {
        "name": "Manu-4",
        "tibetan_name": "མ་ནུ་བཞི་ཐང་།",
        "description": "A digestive formula for balancing stomach heat and acidity.",
        "full_description": "Manu-4 is a classic four-ingredient digestive formula combining pomegranate, long pepper, cinnamon, and cardamom. It is used to restore digestive fire (me-drod) and treat conditions related to bile (mKhris-pa) imbalances.",
        "image_url": PLACEHOLDER,
        "uses": ["Digestive Issues", "Acid Reflux", "Appetite Regulation", "Stomach Balance"],
    },
    {
        "name": "Dashel Dutsi",
        "tibetan_name": "བདེ་གཤེལ་བདུད་རྩི།",
        "description": "A warming remedy for joint pain and cold-related conditions.",
        "full_description": "Dashel Dutsi, the 'Nectar of Comfort,' combines warming herbs and minerals to address pain stemming from cold and damp conditions. Particularly effective for arthritis, rheumatism, and cold-type kidney disorders.",
        "image_url": PLACEHOLDER,
        "uses": ["Joint Pain", "Arthritis", "Cold Constitution", "Kidney Health"],
    },
]

ARTICLES = [
    {
        "title": "Understanding the Three Humors in Tibetan Medicine",
        "slug": "understanding-the-three-humors-in-tibetan-medicine",
        "category": "Philosophy",
        "published_at": datetime(2026, 1, 15, tzinfo=timezone.utc),
        "excerpt": "Explore the foundational concept of rLung, mKhris-pa, and Bad-kan — the three nyepa that govern all physiological and psychological functions.",
        "content": "Tibetan medicine, or Sowa Rigpa, understands health through the balance of three humors (nyepa): **rLung** (wind), **mKhris-pa** (bile), and **Bad-kan** (phlegm).\n\n## rLung — Wind\n\nGoverns movement: breathing, circulation, nerve impulses, and thoughts. Imbalance manifests as anxiety, insomnia, and restlessness.\n\n## mKhris-pa — Bile\n\nGoverns heat and transformation: digestion, metabolism, and intellect. Imbalance manifests as acidity, inflammation, and irritability.\n\n## Bad-kan — Phlegm\n\nGoverns stability and fluid: structure, lubrication, and calm. Imbalance manifests as lethargy, congestion, and heaviness.\n\nHealth is the dynamic equilibrium of all three.",
        "image_url": PLACEHOLDER,
    },
    {
        "title": "The Healing Power of Himalayan Herbs",
        "slug": "the-healing-power-of-himalayan-herbs",
        "category": "Herbal Medicine",
        "published_at": datetime(2026, 1, 8, tzinfo=timezone.utc),
        "excerpt": "A deep dive into the rare medicinal plants found in the Himalayas and their therapeutic applications in traditional Tibetan formulations.",
        "content": "The Himalayas host some of the world's most potent medicinal plants, many harvested above 3,000 meters where harsh conditions concentrate their active compounds.\n\n## Key Herbs\n\n- **Saffron** — cooling, used in precious pills\n- **Aquilaria (Agar)** — calming, central to Agar-35\n- **Pomegranate** — restores digestive fire\n- **Cardamom** — warms the kidneys\n\nTraditional collection follows strict seasonal and ethical guidelines to preserve these fragile alpine ecosystems.",
        "image_url": PLACEHOLDER,
    },
    {
        "title": "Pulse Diagnosis: Reading the Body's Rhythms",
        "slug": "pulse-diagnosis-reading-the-bodys-rhythms",
        "category": "Treatments",
        "published_at": datetime(2025, 12, 28, tzinfo=timezone.utc),
        "excerpt": "Learn how Tibetan physicians use subtle pulse readings at the radial artery to diagnose imbalances and guide treatment plans.",
        "content": "Pulse diagnosis (rtsa) is one of the most refined diagnostic arts in Tibetan medicine. The physician reads six positions on the radial arteries of both wrists.\n\n## The Reading\n\nEach position corresponds to specific organs, and the physician assesses depth, speed, strength, and rhythm. A skilled practitioner can detect imbalances long before symptoms appear.\n\nPulse reading requires decades of practice and is typically combined with urine analysis and detailed questioning.",
        "image_url": PLACEHOLDER,
    },
    {
        "title": "Seasonal Living According to Sowa Rigpa",
        "slug": "seasonal-living-according-to-sowa-rigpa",
        "category": "Wellness",
        "published_at": datetime(2025, 12, 15, tzinfo=timezone.utc),
        "excerpt": "Tibetan medicine emphasizes living in harmony with the seasons. Discover dietary and lifestyle recommendations for each time of year.",
        "content": "Sowa Rigpa divides the year into six seasons, each favoring the accumulation of a different humor.\n\n## Winter\n\nFavor warm, heavy, oily foods. Bad-kan accumulates in the cold.\n\n## Spring\n\nLight, rough foods to counter accumulated phlegm.\n\n## Summer\n\nCool, light foods and avoidance of excessive sun protect against mKhris-pa disorders.\n\n## Autumn\n\nWarm, grounding routines pacify rLung as winds rise.\n\nAligning diet and behavior with the seasons is considered the first line of preventive medicine.",
        "image_url": PLACEHOLDER,
    },
]

GALLERY = [
    ("Morning prayers at the monastery", 1),
    ("Traditional herb preparation", 2),
    ("Consultation with Dr. Dorje", 3),
    ("Tibetan medicine formulations", 4),
    ("Medicinal herb garden", 5),
    ("Community health camp", 6),
    ("Patient wellness seminar", 7),
    ("Research laboratory", 8),
]


def seed() -> None:
    db = SessionLocal()
    try:
        if db.query(Medicine).count() == 0:
            db.add_all(Medicine(**m) for m in MEDICINES)
            print(f"Seeded {len(MEDICINES)} medicines")
        else:
            print("Medicines already seeded, skipping")

        if db.query(Article).count() == 0:
            db.add_all(Article(**a) for a in ARTICLES)
            print(f"Seeded {len(ARTICLES)} articles")
        else:
            print("Articles already seeded, skipping")

        if db.query(GalleryImage).count() == 0:
            db.add_all(
                GalleryImage(image_url=PLACEHOLDER, caption=caption, sort_order=order)
                for caption, order in GALLERY
            )
            print(f"Seeded {len(GALLERY)} gallery images")
        else:
            print("Gallery already seeded, skipping")

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
