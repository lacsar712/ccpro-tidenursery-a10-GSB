from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.broodstock_cage import BroodstockCage
from app.models.hatchery import Hatchery
from app.models.user import User
from app.schemas.broodstock_cage import (
    BroodstockCageCreate,
    BroodstockCageOut,
    BroodstockCageStock,
    BroodstockCageUpdate,
)

router = APIRouter(prefix="/api/broodstock-cages", tags=["broodstock-cages"])


@router.get("", response_model=List[BroodstockCageOut])
def list_cages(
    hatchery_id: Optional[int] = Query(None, alias="hatcheryId"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(BroodstockCage)
    if hatchery_id is not None:
        q = q.filter(BroodstockCage.hatchery_id == hatchery_id)
    return q.order_by(BroodstockCage.id).all()


@router.post("", response_model=BroodstockCageOut, status_code=status.HTTP_201_CREATED)
def create_cage(
    payload: BroodstockCageCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    hatchery = db.query(Hatchery).filter(Hatchery.id == payload.hatchery_id).first()
    if not hatchery:
        raise HTTPException(status_code=400, detail="育苗场不存在")
    item = BroodstockCage(
        hatchery_id=payload.hatchery_id,
        cage_code=payload.cage_code,
        capacity=payload.capacity,
        occupied=0,
        is_active=payload.is_active,
    )
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="同场笼位号已存在")
    db.refresh(item)
    return item


@router.put("/{cage_id}", response_model=BroodstockCageOut)
def update_cage(
    cage_id: int,
    payload: BroodstockCageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(BroodstockCage).filter(BroodstockCage.id == cage_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="笼位不存在")
    data = payload.model_dump(exclude_unset=True)

    if data.get("is_active") is False and item.is_active:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="仅场长可停用笼位")
        if item.occupied > 0:
            raise HTTPException(status_code=400, detail="笼位仍有亲虾占用，无法停用")

    new_capacity = data.get("capacity")
    if new_capacity is not None and new_capacity < item.occupied:
        raise HTTPException(status_code=400, detail="容纳尾数不能小于当前占用尾数")

    for k, v in data.items():
        setattr(item, k, v)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="同场笼位号已存在")
    db.refresh(item)
    return item


@router.post("/{cage_id}/stock-in", response_model=BroodstockCageOut)
def stock_in(
    cage_id: int,
    payload: BroodstockCageStock,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    item = db.query(BroodstockCage).filter(BroodstockCage.id == cage_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="笼位不存在")
    if not item.is_active:
        raise HTTPException(status_code=400, detail="笼位已停用，无法入笼")
    if item.occupied + payload.count > item.capacity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="入笼后占用尾数超出笼位容纳上限",
        )
    item.occupied += payload.count
    db.commit()
    db.refresh(item)
    return item


@router.post("/{cage_id}/stock-out", response_model=BroodstockCageOut)
def stock_out(
    cage_id: int,
    payload: BroodstockCageStock,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    item = db.query(BroodstockCage).filter(BroodstockCage.id == cage_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="笼位不存在")
    if payload.count > item.occupied:
        raise HTTPException(status_code=400, detail="出笼尾数超过当前占用，占用不得为负")
    item.occupied -= payload.count
    db.commit()
    db.refresh(item)
    return item
