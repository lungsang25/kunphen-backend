"""Seed the hero slider with the five slides the website currently ships hardcoded.

The images live in the website repo as bundled assets, so they have to be pushed to
S3 before the CMS can own them. Idempotent: does nothing once hero_slides has rows.

Usage: python -m scripts.seed_hero_slides [path/to/kunphen-frontend/src/assets]
"""
import sys
from pathlib import Path

from app.database import SessionLocal
from app.models import HeroSlide
from app.services.s3 import upload_bytes

DEFAULT_ASSETS_DIR = (
    Path(__file__).resolve().parents[2] / "kunphen-frontend" / "src" / "assets"
)

# Filename, title and subtitle, copied verbatim from the website's HeroSlider.tsx so
# the CMS starts out showing exactly what the live homepage shows.
SLIDES = [
    ("hero-1.jpg", "Ancient Healing Wisdom", "Rooted in centuries of Tibetan medical tradition"),
    ("hero-2.jpg", "Natural Remedies", "Herbal formulations crafted with care and precision"),
    ("hero-3.jpg", "Expert Practitioners", "Guided by experienced Tibetan medicine doctors"),
    ("hero-4.jpg", "Traditional Medicines", "Time-tested herbal compounds for holistic wellness"),
    ("hero-5.jpg", "Healing Gardens", "Where nature and medicine come together"),
]


def seed(assets_dir: Path) -> None:
    db = SessionLocal()
    try:
        if db.query(HeroSlide).count() > 0:
            print("Hero slides already seeded, skipping")
            return

        missing = [name for name, _, _ in SLIDES if not (assets_dir / name).is_file()]
        if missing:
            raise SystemExit(
                f"Missing hero images in {assets_dir}: {', '.join(missing)}\n"
                "Pass the website's src/assets directory as the first argument."
            )

        for order, (name, title, subtitle) in enumerate(SLIDES):
            url = upload_bytes((assets_dir / name).read_bytes(), name, "image/jpeg")
            db.add(
                HeroSlide(
                    image_url=url,
                    title=title,
                    subtitle=subtitle,
                    sort_order=order,
                    is_active=True,
                )
            )
            print(f"Uploaded {name} -> {url}")

        db.commit()
        print(f"Seeded {len(SLIDES)} hero slides")
    finally:
        db.close()


if __name__ == "__main__":
    seed(Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_ASSETS_DIR)
