import math
from typing import List
import requests
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_async_session
from .models import Plant, PlantResponse, PlantSuitabilityResponse
from .suitability import get_weather_and_suitability


def _replace_nan_with_none(plant):
    """
    Replace NaN values with None for a Plant object.

    This function iterates over all attributes of a Plant object. If a float
    attribute is NaN, it replaces the value with None.

    :param plant: The Plant object to process.
    :return: The processed Plant object with NaN values replaced by None.
    """
    for field, value in plant.__dict__.items():
        if isinstance(value, float) and math.isnan(value):
            setattr(plant, field, None)
    return plant


def get_plant_router() -> APIRouter:
    """
    Create and return an APIRouter for plant-related endpoints.

    This router includes endpoints for retrieving all plants, searching by scientific name,
    searching by common name, general searching, and finding similar plants based on embeddings.

    :return: An APIRouter with the plant-related routes.
    """
    router = APIRouter()

    @router.get("/")
    async def get_all_plants(session: AsyncSession = Depends(get_async_session)):
        """
        Retrieve all plants from the database.

        :param session: Database session dependency.
        :return: A list of Plant objects with NaN values replaced by None.
        """
        result = await session.execute(select(Plant))
        plants = result.scalars().all()
        if not plants:
            raise HTTPException(status_code=404, detail="No plants found")
        # Replace NaN values with None
        plants = [_replace_nan_with_none(plant) for plant in plants]
        return plants

    @router.get("/scientific_name/{scientific_name}", response_model=list[PlantResponse])
    async def get_plant_by_scientific_name(scientific_name: str, db: AsyncSession = Depends(get_async_session)):
        """
        Retrieve plants by their scientific name.

        The scientific name is matched case-insensitively. If the name is found,
        all matching plants are returned.

        :param scientific_name: The scientific name of the plant to search for.
        :param db: Database session dependency.
        :return: A list of Plant objects matching the scientific name.
        """
        scientific_name = scientific_name.strip()
        query = select(Plant).where(Plant.ScientificName.ilike(scientific_name))
        result = await db.execute(query)
        plants = result.scalars().all()
        if not plants:
            raise HTTPException(status_code=404, detail="Plant not found")
        # Replace NaN values with None
        plants = [_replace_nan_with_none(plant) for plant in plants]
        return plants

    @router.get("/common_name/{common_name}", response_model=list[PlantResponse])
    async def get_plant_by_common_name(common_name: str, db: AsyncSession = Depends(get_async_session)):
        """
        Retrieve plants by their common name.

        The common name is searched case-insensitively and as a substring.
        If the common name is found within any part of the COMNAME field, all matching plants are returned.

        :param common_name: The common name to search for.
        :param db: Database session dependency.
        :return: A list of Plant objects matching the common name.
        """
        common_name = common_name.strip()
        query = select(Plant).where(Plant.COMNAME.ilike(f"%{common_name}%"))
        result = await db.execute(query)
        plants = result.scalars().all()
        if not plants:
            raise HTTPException(status_code=404, detail="No plants found")
        # Replace NaN values with None
        plants = [_replace_nan_with_none(plant) for plant in plants]
        return plants

    @router.get("/search/{query}", response_model=list[PlantResponse])
    async def search_plants(query: str, db: AsyncSession = Depends(get_async_session)):
        """
        Search plants by a general query.

        The query is searched case-insensitively in both the ScientificName and SYNO (Synonyms) fields.
        If a match is found, all matching plants are returned.

        :param query: The search query to match against the ScientificName and SYNO fields.
        :param db: Database session dependency.
        :return: A list of Plant objects matching the search query.
        """
        query = query.strip()
        query_stmt = select(Plant).where(
            (Plant.ScientificName.ilike(f"%{query}%")) | (Plant.SYNO.ilike(f"%{query}%"))
        )
        result = await db.execute(query_stmt)
        plants = result.scalars().all()
        if not plants:
            raise HTTPException(status_code=404, detail="No plants found")
        # Replace NaN values with None
        plants = [_replace_nan_with_none(plant) for plant in plants]
        return plants

    @router.get("/suitability/single/{scientific_name}", response_model=PlantSuitabilityResponse)
    async def calculate_suitability_for_plant(
            scientific_name: str,
            location: str,
            session: AsyncSession = Depends(get_async_session)
    ):
        query = select(Plant).where(Plant.ScientificName.ilike(scientific_name.strip()))
        result = await session.execute(query)
        plant = result.scalars().first()

        if not plant:
            raise HTTPException(status_code=404, detail="Plant not found.")

        suitability_data = await get_weather_and_suitability(location, scientific_name, session)

        plant_response = PlantSuitabilityResponse(
            **suitability_data
        )

        return plant_response

    return router
