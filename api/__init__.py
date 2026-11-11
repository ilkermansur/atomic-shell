"""Kabuğun kendi API'si. Bütün uçlar /api altındadır.

Arayüz yalnızca bu uçları kullanır; arayüzde yapılabilen her şey buradan da
yapılabilir.
"""
from fastapi import APIRouter

from api import atoms, elements, molecules, runs

router = APIRouter(prefix="/api")
router.include_router(elements.router)
router.include_router(atoms.router)
router.include_router(molecules.router)
router.include_router(runs.router)
