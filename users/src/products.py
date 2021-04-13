import requests

from typing import List

from fastapi import APIRouter, Path, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.db.base import get_session
from src.schemas import ProductSchema
from src import crud


router = APIRouter()


@router.get("/", response_model=List[ProductSchema])
async def get_products(session: AsyncSession = Depends(get_session)) -> List[ProductSchema]:
    products = await crud.get_all_products(session)
    if not products:
        raise HTTPException(
            status_code=404, detail="No products available yet"
        )
    product_list = [ProductSchema(id=p.id, title=p.title, image=p.image, likes=p.likes) for p in products]
    return product_list


@router.post("/{id}/like")
async def like(id: int = Path(..., gt=0), session: AsyncSession = Depends(get_session)):
    # req = requests.get('http://localhost:8000/api/user')
    # data = req.json()

    # assert data['id'] == id

    product = await crud.get_product(session, id)
    pr = ProductSchema(id=product.id, title=product.title, image=product.image, likes=product.likes)
    print(f'PRODUCT: {pr.likes}')
    liked = pr.likes + 1
    print(f'PRODUCT_AFTER: {pr.likes}')
    await crud.update_product(session, pr.id, pr.title, pr.image, likes=liked)
    try:
        await session.commit()
        return {"product": id, "message": "liked"}
    except IntegrityError as ex:
        await session.rollback()
        raise Exception(f"You already liked this product: {ex}")


# @router.post("/api/products/")
# async def create_product(product: ProductSchema, session: AsyncSession = Depends(get_session)):
#     await crud.create_product(session, product.id, product.title, product.image)

#     response_obj = {"title": product.title, "image": product.image}

#     return response_obj