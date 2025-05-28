from typing import List
from fastapi.responses import StreamingResponse
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from . import crud, schemas, database

router = APIRouter()


@router.post("/insert-test", response_model=schemas.TestResponse)
async def create_test(
    test: schemas.TestCreate,
    db: AsyncSession = Depends(database.get_db)
):
    db_test = await crud.get_test(db, test_id=test.test_id)
    if db_test:
        raise HTTPException(status_code=400, detail="Test ID already registered")
    return await crud.create_test(db=db, test=test)


@router.get("/test/{test_id}", response_model=schemas.TestResponse)
async def read_test(
    test_id: str,
    db: AsyncSession = Depends(database.get_db)
):
    db_test = await crud.get_test(db, test_id=test_id)
    if db_test is None:
        raise HTTPException(status_code=404, detail="Test not found")
    return db_test

@router.get("/all-tests/", response_model=List[schemas.TestResponse])
async def read_all_tests(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(database.get_db)
):
    """Barcha testlarni paginatsiya bilan qaytaradi"""
    return await crud.get_all_tests(db, skip=skip, limit=limit)

@router.delete("/delete-test/{test_id}", response_model=schemas.DeleteResponse)
async def delete_test(
    test_id: str,
    db: AsyncSession = Depends(database.get_db)
):
    success = await crud.delete_test(db, test_id=test_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Test topilmadi yoki o'chirishda xatolik yuz berdi"
        )
    return {
        "success": True,
        "message": f"{test_id} testi va uning javoblari muvaffaqiyatli o'chirildi"
    }

@router.post("/insert-response/", response_model=schemas.UserResponseResponse)
async def create_response(
        response: schemas.UserResponseCreate,
        db: AsyncSession = Depends(database.get_db)
):
    test = await crud.get_test(db, test_id=response.test_id)
    if not test:
        raise HTTPException(
            status_code=404,
            detail="Test not found"
        )

    table_name = f"{response.test_id}_answers"
    telegram_id_exist = await crud.telegram_id_exists(db, table_name, response.telegram_id)
    if telegram_id_exist:
        raise HTTPException(
            status_code=403,
            detail="Telegram ID already registered"
        )
    if len(response.answers) != len(test.answers):
        raise HTTPException(
            status_code=400,
            detail=f"Answer length ({len(response.answers)}) doesn't match test requirements ({len(test.answers)})"
        )

    result = await crud.create_user_response(db=db, response=response)
    if not result:
        raise HTTPException(
            status_code=500,
            detail="Failed to save response"
        )

    return result


@router.get("/responses/{test_id}", response_model=List[schemas.UserResponseResponse])
async def read_responses(
        test_id: str,
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(database.get_db)
):
    test = await crud.get_test(db, test_id=test_id)
    if not test:
        raise HTTPException(
            status_code=404,
            detail="Test not found"
        )
    return await crud.get_user_responses(db, test_id=test_id, skip=skip, limit=limit)

@router.get("/export-responses/{test_id}", response_class=StreamingResponse)
async def export_test_results(
    test_id: str,
    db: AsyncSession = Depends(database.get_db)
):
    """Export test results to Excel file"""
    excel_buffer = await crud.export_test_results_to_excel(db, test_id)
    if not excel_buffer:
        raise HTTPException(
            status_code=404,
            detail="Test topilmadi yoki javoblar mavjud emas"
        )

    # Create filename with current date
    filename = f"test_results_{test_id}_{datetime.now().strftime('%Y%m%d')}.xlsx"

    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )